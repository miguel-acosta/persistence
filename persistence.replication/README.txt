These files can be used to replicate Acosta and Meade's (2015) "Hanging on
every word: Semantic analysis of the FOMC's postmeeting statement." There
are four steps in reproducing the results:

    1. download the FOMC statements,
    2. clean the statements and create term-document matrices for analysis,
    3. perform linguistic analysis, count words and phrases, and report results.


Each step (and substep above) is performed by a single Python script.
Running the scripts in order will leave you with the results that we
display in our note. In what follows I give a brief description of each
script, saving more detailed explanations for comments therein.

1.  Download the FOMC statements.
    While I do not provide the FOMC statements themselves, the code in
    "pullStatements.py" downloads the statments from the Fed's website,
    and stores them for you in the directory "statements".

2.  Clean the statements and create term-document matrices for analysis.
    The code in "pullStatements.py" reads in the FOMC statements, downloaded
    in step 1, cleans them, and creates term-document matrices. In this code,
    you can choose the different parameters for the extent of document
    preprocessing (excluding stop words, stemming, the number of times a word
    must occur to be counted, the characters that are kept, etc.).

3.  Perform linguistic analysis, count words and phrases, and report results.
    The code in "persistence.py" takes the term-document matrices from step
    2, and calculates the "semantic persistence" measure that is in our note.
    (I generally refer to this as "persistence" in the code). In here, you
    can further decide whether or not to use  inverse-document frequency
    weighting. This code also performs word/phrase counts of the FOMC
    statements.

This code was all written and tested in a Linux environment  in Python 2.7.10.
To run a python script, open your shell/terminal/command prompt,
navigate to where the code is stored, and type 'python filename.py'. The
code should work on a Mac and in Windows, but it does rely on some packages
that you may need to install (nltk, numpy, pandas, urlopen). See the
websites of these packages for installation instructions. 


A few notes:

   The statements, in all forms (raw (from the internet), and any cleaned
   versions) are stored in the 'statements' directory. Any output from any
   of these files is stored in the 'output' directory.

   Note that python uses 0 to index the first item in a list. You will need
   to account for this if you read the term-document matrices into Matlab,
   for example.

   My python code all follows the same general format
     a. General notes at the top
     b. Importing any additional python packages
     c. Declaring global variables
     d. Any functions needed
     e. A 'main' function, the very last function, that does all of the work
        and calls the other functions. The 'main' function is called by a line
	at the very bottom of the file, which (I think) is python style. 

   I also left a file, persistence.m, which was originally used for the FEDS
   note, and replaces the part of persistence.py that calculates the 
   persistence measure. It is not well documented nor tested with this
   updated version of the python code.

   The 'data' directory here contains various files needed by the python code.

   The file textmining_withnumbers.py is used for creating the term-document
   matrix. It is a slight modification of textmining.py, which can be found
   at http://www.christianpeccei.com/textmining/. 
