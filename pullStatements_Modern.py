#------------------------------------------------------------------------------#
# Original file: pullStatements.py
#
# Description:   This file downloads the FOMC statements from the Fed website,
#                www.federalreserve.gov, and stores them as individual files
#                in the directory 'statements'.
#                
# Input:         A file in the directory 'data', called 'dates.sort.txt',
#                that contains FOMC meeting dates in the format YYYYMMDD, one 
#                date per line. Currently, this file contains dates through
#                2025. If you run this and want more statements, you will need
#                to add the dates manually from the FOMC website, and possibly
#                edit the FOMCstatementURL function.
#                
# Output:        Files titles 'statements.fomc.YYYYMMDD', each of which contains
#                an FOMC statement.
#                
# Author:        Miguel Acosta
#
# Contributors:  Eric Chu
#
# Last edited:   January 5, 2026
#                See change log at bottom of file.
#------------------------------------------------------------------------------#



#--------------------------------- IMPORTS -----------------------------------#
from   bs4    import BeautifulSoup
from   urllib.request import urlopen
from   time   import sleep
from urllib.request import Request
import re,csv,os

#-------------------------DEFINE GLOBAL VARIABLES-----------------------------#
# Directory in which to place statements (careful in changing this--other
# scripts in this package rely on it).

outdir = os.path.join('statements','statements.raw')

#-----------------------------------------------------------------------------#
# FOMCstatementsURL: A function that returns the appropriate URL of the
#   FOMC statements. Given a date string in the format YYYYMMDD, it returns a
#   string with the appropriate URL. I collected the URLs manually.
#-----------------------------------------------------------------------------#

# Main edits: Fed uses the new URL structure since 2006

def FOMCstatementURL(date):
    year = date[0:4]
    dateInt = int(date)

    ## Case 0: Special case for 20081216
    if dateInt == 20081216:
        urlout = 'http://www.federalreserve.gov/newsevents/' + \
                 'pressreleases/monetary' + date + 'b.htm'
    ## Case 1: Pre-1996
    if dateInt < 19960101:
        urlout = 'https://www.federalreserve.gov/fomc/' + date + 'default.htm'
    ## Case 2: 1996 (only one statement)
    elif dateInt >= 19960101 and dateInt < 19970101:
        urlout = 'https://www.federalreserve.gov/fomc/' + date + 'DEFAULT.htm'
    ## Case 3: "https://www.federalreserve.gov/boarddocs/press/general/1999/19990518/"
    elif dateInt >= 19970101 and dateInt < 20020331:
        urlout = 'http://www.federalreserve.gov/boarddocs/' + \
                 'press/general/' + year + '/' + date + '/'
    ## Case 4: "https://www.federalreserve.gov/boarddocs/press/monetary/2002/20020507/"
    elif dateInt >= 20020331 and dateInt < 20030000:
        urlout = 'http://www.federalreserve.gov/boarddocs/press/' + \
                 'monetary/' + year + '/' + date + '/'
    ## Case 5: "https://www.federalreserve.gov/boarddocs/press/monetary/2004/20040810/default.htm"
    elif dateInt >= 20030000 and dateInt < 20060000:
        urlout = 'http://www.federalreserve.gov/boarddocs/press/' + \
                 'monetary/' + year + '/' + date + '/default.htm'
    ## Case 6: "https://www.federalreserve.gov/newsevents/pressreleases/monetary20250917a.htm"
    elif dateInt >= 20060000:
        urlout = 'https://www.federalreserve.gov/newsevents/pressreleases/' + \
                 'monetary' + date + 'a.htm'

    return urlout

#-----------------------------------------------------------------------------#
# getDate: A function that uses the BeautifulSoup library to scrape the
#   text of the FOMC statement from the Fed website, which the funnction
#   returns as a string. Note that there is little effort to clean the text---
#   that is reserved for another step.
#-----------------------------------------------------------------------------#

def getStatement(mtgDate):
    url = FOMCstatementURL(mtgDate)
    try:
        hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        html = urlopen(Request(url,headers=hdr)).read()
        soup = BeautifulSoup(html)
        allText = soup.get_text(" ")
        
        # Start patterns: Check legacy patterns first, then modern ones
        start_patterns = [
            r"[Ff]or\s[Ii]mmediate\s[Rr]elease",  # Legacy pattern (1999-2015)
            r"[Ff]or\s+release\s+at\s+\d+:\d+\s+[ap]\.?m\.?\s+[A-Z]{3}T?"  # Modern pattern (2016+) e.g., "For release at 2:00 p.m. EDT"
        ]
        
        startLoc = None
        for pattern in start_patterns:
            match = re.search(pattern, allText, re.IGNORECASE)
            if match:
                startLoc = match.start()
                break
        
        if startLoc is None:
            return ""
            
        statementText = allText[startLoc:]

        # End patterns: Check legacy patterns first, then modern ones
        end_patterns = [
            r"[0-9]{4}\s[Mm]onetary\s[Pp]olicy",  # Legacy pattern (1999-2015) e.g., "2015 Monetary Policy"
            r"Last\s+Update:\s+[A-Za-z]+\s+\d+,\s+\d{4}"  # Modern pattern (2016+) e.g., "Last Update: January 31, 2006"
        ]
        
        endLoc = None
        for pattern in end_patterns:
            match = re.search(pattern, statementText, re.IGNORECASE)
            if match:
                endLoc = match.start()
                break
        
        if endLoc is None:
            pass
            # Use the full statement if we can't find the end
        else:
            statementText = statementText[:endLoc]
        
        # Remove "Share" section that appears in "modern" FOMC statements
        share_match = re.search(r'\s+Share\s+', statementText)
        if share_match:
            after_share = statementText[share_match.end():]
            lines = after_share.split('\n')
            first_content_idx = 0
            for i, line in enumerate(lines):
                if line.strip() and len(line.strip()) > 20:
                    first_content_idx = i
                    break
            # Keep everything before "Share" + skip to first real content
            before_share = statementText[:share_match.start()]
            real_content = '\n'.join(lines[first_content_idx:])
            statementText = before_share + '\n' + real_content
        
        # Clean up excessive whitespace: collapse multiple blank lines into one
        statementText = re.sub(r'\n\s*\n\s*\n+', '\n\n', statementText)
        statementText = re.sub(r' {2,}', ' ', statementText)
            
        # Add a printed message for tracking
        # If we see this error messgae printed out in terminal, just delete the corresponding files manually.
        # Then, run the one-line script again!
        statementText = statementText.encode('ascii', 'ignore').decode('ascii')
        print(f"Extracted statement text ({len(statementText)} characters)") # To eyeball whether this scrape works
        return statementText
    except Exception as e:
        print(f"[!!] Error accessing URL: {e}") # Comment out this line for a cleaner terminal
        return ""
        
        # Notes: if a FOMC statement is not scraped properly, we'll  notice the file size being 0.
        # What to do: delete that file manually, and simply run this program again
        # in "main()" below, there's a skip-existing-file feature so we only re-scrape the deleted files/dates


#-----------------------------------------------------------------------------#
# The Main function reads the file data/data.sort.txt, forms a list of the
#   meeting dates contained therein, and loops over them, at each iteration
#   calling the function getStatement to get the FOMC statement from
#   that date. It then prints out the results to individual files.
#-----------------------------------------------------------------------------#

# Main eits:
# Added more annoucement dates with 'dates_sort_modified.txt': post 2016
# Added progress tracking & skip feature (re-scraping only those missing dates/files)

def main():
    
    dates_file = os.path.join('data','dates_sort_modified.txt') # More fomc announcment dates in this new file
    
    releaseDates = [line.rstrip() for line in open(dates_file, 'r')]
    print(f"Found {len(releaseDates)} dates to process") # For porgress tracking

    # Check which dates already have files and skip them
    # This is better for progress tracking
    os.makedirs(outdir, exist_ok=True)
    existing_files = {re.findall(r'[0-9]{8}',f)[0]
                      for f in os.listdir(outdir) if f.endswith('.txt')}
    # If 20070628 exists, also mark 20070618 as existing
    if '20070628' in existing_files:
        existing_files.add('20070618')
    releaseDates = [d for d in releaseDates if d not in existing_files] # Added a skip feature
    print(f"Skipping {len(existing_files)} already pulled, processing {len(releaseDates)} remaining") # For progress tracking

    for releaseDate in releaseDates:
        print(f"\nProcessing date: {releaseDate}") # For porgress tracking
        data = getStatement(releaseDate)
        
        if not data:
            print(f"[!!] Skipping {releaseDate} - no data retrieved") # For porgress tracking
            continue
        
        # Give the Fed servers a break
        sleep(2) 
        # The URL for 20070628 is stored at 20070618 page.
        if releaseDate.find("20070618")>-1:
           releaseDate = "20070628"
        filename="statement.fomc." + releaseDate +".txt"
        filepath = os.path.join(outdir,filename)
        print(f"Saving to: {filepath}") # For progress tracjing
        f = open(filepath, 'w')
        f.write(data)
        f.close()


if __name__ == "__main__":
    main()


#------------------------------------------------------------------------------#
# Change log                                                                   #
#------------------------------------------------------------------------------#
# First public version: January 21, 2015
# 
# Modification date: October 15, 2025
# 
# Modified by Eric Chu
#
#    Main edits:
#    1) Updated dates since 2016 ("dates_sort_modified.txt")
#    2) Updated URL patterns to reflect changes in the Federal Reserve's
#       website ("Modern" vs "Legacy")
#    3) Updated text extraction patterns to handle changes in Modern statement 
#       formatting (e.g., "For Immediate Release" to "For release at ...", and
#       "Monetary Policy" to "Last Update: ...")
#    4) Removed the "Share" section that appears in Modern statements
#    5) Added progress tracking (re-scraping only those missing dates/files)
#       with some messages
#
#
# Modification date: January 5, 2026
#
# Modified by Miguel Acosta
#
#    1) Added pre-1999 statements (note: added an unscheduled meeting 10/15/1998)
#    2) Added remaining 2025 statements
#    3) Added header to url request
#    4) Modification to missing dates/files logic 
#
#------------------------------------------------------------------------------#    
