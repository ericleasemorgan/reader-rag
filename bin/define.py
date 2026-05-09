#!/usr/bin/env python

# define.py - given a carrel and a word, output definitions of the word

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# March    27, 2023 - first cut
# June      6, 2023 - added command line input
# November  5, 2023 - used more intelligent tokenization, and greatly refined output
# May      26, 2025 - using database of sentences; ought to output json


# configure
LIBRARY         = 'localLibrary'
SELECTSENTENCES = "SELECT sentence FROM sentences"
SENTENCES       = 'sentences.db'
VERBOSE         = False
CACHE           = '../etc/context.txt'

# require
from nltk     import word_tokenize
from nltk.wsd import lesk
from rdr      import configuration, ETC
from sys      import argv, exit, stderr
from sqlite3  import connect
from os       import chdir
from os.path  import dirname, abspath

# make sane
chdir( dirname( abspath( __file__ ) ) )

# get input
if len( argv ) != 3 : exit( "Usage: " + argv[ 0 ] + " <carrel> <word>" )
carrel = argv[ 1 ]
word   = argv[ 2 ]

# initialize
library = configuration( LIBRARY )

# get all sentences; might not be scalable
sentences  = []
connection = connect( library/carrel/ETC/SENTENCES )
results    = connection.execute( SELECTSENTENCES ).fetchall()
for result in results : sentences.append( result[ 0 ] )

# get and process each sentence; create a set of matching results
results = [] 
for sentence in sentences : 

	if sentence == None : continue
	
	# filter
	if word.lower() in sentence.lower() :
					
		# disambiguate; the magic happens here
		synset = lesk( word_tokenize( sentence ), word )
		
		# update, conditionally
		if synset : results.append( ( synset, sentence ) )
	
# count & tabulate the results
synsets = {}
for result in results :

	# parse
	synset = result[ 0 ]
	
	# count and tabulate
	if synset in synsets : synsets[ synset ] += 1
	else                 : synsets[ synset ] =  1

# sort and process each resulting synset; tricky
synsets = dict( sorted( synsets.items(), key=lambda x:x[ 1 ], reverse=True ) )
cache   = []

for synset in synsets.keys() :
	
	# get the list of matching sentences; pythonic
	sentences = [ result[ 1 ] for result in results if result[ 0 ] is synset ]
		
	# output
	stderr.write( '      synset: ' + synset.name()            + '\n' )	
	stderr.write( '   frequency: ' + str( synsets[ synset ] ) + '\n' )	
	stderr.write( '  definition: ' + synset.definition()      + '\n' )
	
	# ouput some more
	for sentence in sentences : cache.append( sentence  )
	
	# delimit
	stderr.write( '\n' )

# output some more and done
with open( CACHE, 'w' ) as handle : handle.write( '\n'.join( cache ) )
exit()
