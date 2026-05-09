#!/usr/bin/env python

# search-with-verb.py - output sentences whose subject is a lexicon word and whose verb is a form a given lemma

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June 26, 2022 - first cut; not perfect, but fun and good enough
# June 27, 2022 - added parallel processing and a few modes
# July 29, 2022 - add lemma as input on the command line
# May  26, 2025 - used database of sentences instead of iterator


# configure
LIBRARY         = 'localLibrary'
SELECTTOKENS    = "SELECT DISTINCT( token ) FROM pos WHERE lemma IS '##LEMMA##'"
SELECTSENTENCES = "SELECT sentence FROM sentences ORDER BY title, item"
SENTENCES       = 'sentences.db'
GRAMMAR         = '''
  NOUNPRASE: {<DT>?<JJ.*>*<NN.?>+}
  PREDICATE: {<VB.*>}
    GRAMMAR: {<NOUNPRASE><PREDICATE><NOUNPRASE>}
'''

# require
from multiprocessing import Pool
from nltk            import word_tokenize, pos_tag, RegexpParser
from rdr             import configuration, ETC, LEXICON, DATABASE
from sqlite3         import connect
from sys             import argv, exit

# migrate the results of sql queries into a generator; smart!?
def select2generator( connection, sql ) :

	# query the given connection
	results = connection.execute( sql ).fetchall()
	
	# yield each result; ought to be very memory efficient
	for result in connection.execute( sql ).fetchall(): yield( result[ 0 ] )

# given a sentence, a grammar, a list of words, and a list of verbs, return a set of sentences
def extractSentences( sentence, parser, lexicon, verbs ) :
		
	if ( sentence == None ) : return
	
	# normalize and tokenize
	tokens = word_tokenize( sentence.lower() )
	tokens = [ token.lower() for token in tokens ]

	# check for given nouns
	if lexicon.intersection( set( tokens ) ) :

		# get parts-of-speech and create an NLTK tree
		pos  = pos_tag( tokens )
		tree = parser.parse( pos )

		# process each branch
		for branch in tree.subtrees( lambda t : t.label() == 'GRAMMAR' ) :

			# get all subject words; re-check for given nouns
			subjects = []
			leaves   = branch[ 0 ].leaves()
			for leaf in leaves : subjects.append( leaf[ 0 ] )
			if lexicon.intersection( set( subjects ) ) :	

				# get the verb; check for given verbs and output, conditionally
				verb = branch[ 1 ].flatten().leaves()[ 0 ][ 0 ]
				if verb in verbs : print( sentence )

	# done
	return()
	
	
# do the work
if __name__ == '__main__' : 

	# get input
	if len( argv ) != 3 : exit( 'Usage: ' + argv[ 0 ] + " <carrel> <lemma>" )
	carrel = argv[ 1 ]
	lemma  = argv[ 2]

	# initialize
	parser   = RegexpParser( GRAMMAR )
	library  = configuration( LIBRARY )
	
	# read and normalize the given lexicon
	with open( library/carrel/ETC/LEXICON ) as handle : lexicon = handle.read().splitlines()
	lexicon = [ word.lower() for word in lexicon ]
	lexicon = set( lexicon )
	
	# get all forms of the given lemma
	verbs      = []
	connection = connect( library/carrel/ETC/DATABASE )
	results    = connection.execute( SELECTTOKENS.replace( '##LEMMA##', lemma ) ).fetchall()
	for result in results : verbs.append( result[ 0 ] )
	
	# get all sentences; might not be scalable
	sentences = select2generator( connect( library/carrel/ETC/SENTENCES ), SELECTSENTENCES )
	
	# get and parallel process each sentence in the given carrel
	pool = Pool()
	pool.starmap( extractSentences, [ [ sentence, parser, lexicon, verbs ] for sentence in sentences ] )

	# clean up and done
	pool.close()
	exit()

