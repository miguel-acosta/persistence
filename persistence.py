# Filename:    persistence.py
#
# Description: This file reads the term-document matrix (tdm) data, created by
#              cleanStatements.py, and outputs the data from figures 1, 2, 3,
#              5a, 5b, and 6 from Acosta and Meade (2015) (figure 4 can be
#              generated from the calculatePersistence function below, too).
#
# Input:       Three csv files: tdm.sparse*.csv, tdm.words*.csv, tdm.docs*.csv,
#              for each type of preprocessing under consideration (here, we use
#              two sets, one where *='' (more preprocessing) and *='.np' (no
#              preprocessing).
#              The decision about which files to load is made in the main
#              function below, as is the list of words and phrases for which
#              you would like a word count.
#
# Output:      csv files:
#                output/persistence_AM15.csv, which contains the
#                  persistence data (figures 3, 5a, 5b)
#                output/persistenceMA_AM15.csv, which contains the moving
#                  average of the persistence data (figures 3, 5a, 5b, 6)
#                output/count_*.csv, which contains the word/phrase counts
#                  found in figure 1 (where * is an identifier for the search
#                  you're running).
#
# Author:      Miguel Acosta
#              www.acostamiguel.com
#
# Last edited: January 26, 2015


#--------------------------------- IMPORTS -----------------------------------#
import os
import numpy as np
from   scipy.sparse import csr_matrix
import matplotlib
from   datetime import datetime as dt
import pandas as pd
import csv


#-------------------------DEFINE GLOBAL VARIABLES-----------------------------#
# Location of the term-document matrices
from cleanStatements import outputDir
TDMdir = outputDir
# Location of the moderately cleanned statements
from cleanStatements import cleanDirNP
statementDir = cleanDirNP
# Location in which to store output
outdir = 'output'

#-----------------------------------------------------------------------------#
# cossim: calculates the cosine similarity of two vectors (numpy arrays),
#   a and b.
#-----------------------------------------------------------------------------#
def cossim(a,b):
    numerator = np.dot(a,b)
    norma = np.dot(a,a)
    normb = np.dot(b,b)
    denominator = np.sqrt(norma*normb)
    return(numerator/denominator)


#-----------------------------------------------------------------------------#
# calculatePersistence: calculates the semantic persistence of FOMC statements,
#   found in figures 3, 5a, and 5b. The inputs are:
#     fileSuffix: The identifier, defined in cleanStatements.py, that indicates
#       how much preprocessing is used in generating the term-document matrices
#       (this is a string).
#     IDF: Boolean for whether or not to use inverse-document-frequency
#       weighting
#     descriptive: A string used to describe the parameters you've chosen in
#       the calculation of persistence (e.g. 'Baseline' or 'No Preprocessing')
#     persistenceAll: A pandas data frame, to which the persistence for each
#       meeting is added, for each parameterization.
#   Returns persistenceAll, which is added to each time the function is called.
#-----------------------------------------------------------------------------#
def calculatePersistence(fileSuffix, IDF, descriptive, persistenceAll):
    # File names containing the tdm, associated words (rows) and document
    # names (columns)
    TDMfile   = os.path.join(TDMdir,'tdm.sparse' + fileSuffix + '.csv')
    wordsFile = os.path.join(TDMdir,'tdm.words'  + fileSuffix + '.csv')
    docsFile  = os.path.join(TDMdir,'tdm.docs'   + fileSuffix + '.csv')

    # Read in tdm, whose first row is the column number (j), second rows is a
    # row number (i), and final column is the word count for word i in document
    # j.
    TDMsparse  = np.genfromtxt(TDMfile, delimiter=',')
    nwords     = int(max(TDMsparse[:,1])+1)
    ndocs      = int(max(TDMsparse[:,0])+1)
    TDM        = csr_matrix((TDMsparse[:,2],
                             (TDMsparse[:,1], TDMsparse[:,0])),
                            shape = (nwords,ndocs)).toarray()
    # Read in words and documents associated with rows and columns of the tdm
    wordsRaw = np.array([line.rstrip() for line in open(wordsFile, 'r')])
    docsRaw  = np.array([line.rstrip() for line in open(docsFile, 'r')])


    # Sort these alphabetically (this is chronoligical for the document names)
    wsort = np.argsort(wordsRaw)
    words = wordsRaw[wsort]
    dsort = np.argsort(docsRaw)
    docs  = docsRaw[dsort]

    # Sort the tdm according to the alphabetical sorting
    TDM = TDM[wsort,:]
    TDM = TDM[:,dsort]

    # Apply term-frequency, inverse document frequency weighting (TF-IDF)
    if IDF:
        TDMbool = TDM
        TDMbool[TDMbool > 0] = 1
        # number of documents in which term i occurs
        n_i = np.sum(TDMbool, axis = 1)
        # Inverse document frequency
        IDFvec = np.log(ndocs/n_i)
        IDFmat = np.tile(IDFvec,(ndocs,1)).transpose()

        # Multiply term-frequency by inverse document frequency to get TF-IDF
        TDM = np.multiply(IDFmat, TDM)

    # Calculate semantic persistence
    persistence = []
    for d in range(1,ndocs):
        persistence.append(cossim(TDM[:,d],TDM[:,d-1]))

    if persistenceAll.empty:
        dates = [dt.strptime(doc[15:23], '%Y%m%d') for doc in docs.tolist()]
        persistenceAll = pd.DataFrame(persistence,
                                      index = dates[1:],
                                      columns = [descriptive])
    else:
        persistenceAll  [descriptive] = persistence
    return(persistenceAll)

#-----------------------------------------------------------------------------#
# wordCounts: counts the number of times that a word/phrase is used in each
#   FOMC statement. It takes as an input 'words,' which is a list containing
#   words and/or phrases to count--this code sums across the words in the list,
#   so if you're interested in how oftern 'inflation' or
#   'inflation expectations' are used, then include these in the 'words' list.
#   The output is what is displayed in figure 2, and it is saved in
#   output/counts_*.csv, where *=outname, some mnemonic to describe the search
#   (for the 'inflation' example, we might let outname='pi')
#   total is a boolean indicating whether the total number of words in the
#   statements should be counted, instead of a particular query.
#-----------------------------------------------------------------------------#
def wordCounts (words, total,outname):
    statementList = sorted([ f for f in os.listdir(statementDir)
                      if os.path.isfile(os.path.join(statementDir,f))])
    dates = [dt.strptime(s[15:23], '%Y%m%d') for s in statementList]

    # The main data frame where the counts will be stored
    frequencies = pd.DataFrame([0]*(len(statementList)),
                               index = dates,
                               columns = ['Count'])
    for word in words:
        for statement in statementList:
            date = dt.strptime(statement[15:23], '%Y%m%d')
            text  = open(os.path.join(statementDir,statement),'r').read()
            if total:
                frequencies['Count'][date] = len(text.split())
            else:
                frequency = text.count(" " + word + " ", 0, len(text))
                frequencies['Count'][date] = frequency + \
                                             frequencies['Count'][date]

    # Print the csv
    frequencies.to_csv(path_or_buf = \
                       os.path.join(outdir,'counts_' + outname + '.csv'),
                       index_label = "Date")


#-----------------------------------------------------------------------------#
# The main function essentially runs the two main functions above, wordCounts
#   and calculatePersistence. It is also here where parameter choices are made.
#   It also calculates the moving averages of the persistence variable, and
#   prints the output to a csv.
#-----------------------------------------------------------------------------#
def main():
    # Calculate the persistence results: these lists of length three
    # correspond to the three levels of preprocessing in Acosta and
    # Meade (2015)
    fileSuffixes = ['.np',   '',  '']
    IDF          = [False,False,True]
    descriptive  = ['Baseline', 'Preprocessing', 'Preprocessing + IDF']
    n_alts       = len(descriptive)

    # persistenceAll contains the persistence figure for each meeting
    persistenceAll = pd.DataFrame()
    for i in range(0,n_alts):
        persistenceAll = calculatePersistence(fileSuffixes[i],
                                              IDF[i],
                                              descriptive[i],
                                              persistenceAll)
    # persistenceAllMA contains an eight meeting moving average
    persistenceAllMA  = pd.rolling_mean(persistenceAll,8)

    # Print persistence csv
    persistenceAll.to_csv(path_or_buf = \
                          os.path.join(outdir,'persistence_AM15.csv'),
                          index_label = "Date", float_format = '%1.2f')
    persistenceAllMA.to_csv(path_or_buf = \
                            os.path.join(outdir,'persistenceMA_AM15.csv'),
                            index_label = "Date", float_format = '%1.2f')
    # Word Counts: countList is a list of lists that contain queries that
    #  you'd like to run (i.e., the number of times that the word in the list
    # occurs in the statements.
    countLists = [['inflation expectations', 'inflationary expectations'], \
                  ['productive', 'productivity'], \
                  ['energy', 'commodity', 'commodities', 'oil'], \
                  ['foreign', 'global', 'abroad', 'geopolitical'], \
                  ['weather', 'hurricane', 'katrina', 'winter'], \
                  []]
    searchOutnames=['piexp', 'prod', 'energy', 'foreign', 'weather', 'all']
    for ii in range(len(countLists)):
        wordCounts(countLists[i],(not countLists[i]),searchOutnames[i])


if __name__ == "__main__":
    main()
