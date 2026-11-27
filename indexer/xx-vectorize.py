#!/usr/bin/env python

# vectorize.py - given a carrel, create a database of sentences and their embeddings
# see: https://github.com/asg017/sqlite-vec/

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May      16, 2025 - with a lack of hearing, a FOC, and because the CRC machines were under maintence
# May      17, 2025 - migrated to Euclidian (VEC_DISTANCE_L2) distances
# May      22, 2025 - added title of item and item (sentence) number to database
# June      7, 2025 - normalized sentences so they are always strings
# July      4, 2025 - using a new embedder; actually moved to Ollama
# March    30, 2026 - started caching vectors as a file
# March    31, 2026 - started caching vectors in the database
# April     2, 2026 - scaled back to older embedder because nomic mysteriously broke; cached vectors to a file
# November 19, 2026 - factored out the duplicate functions; stream lining ./index.sh
 

# MODEL:SIZE - locusai/multi-qa-minilm-l6-cos-v1:768:384
# MODEL:SIZE - nomic-embed-text:768

# configure
MODEL      = 'locusai/multi-qa-minilm-l6-cos-v1'
INSERT     = "INSERT INTO embeddings (sentence_id, embedding) VALUES (?, ?)"
PATTERN    = '*.snt'
LIBRARY    = 'localLibrary'
DATABASE   = 'sentences.db'
CACHE      = 'sentences'
VECTORS    = 'vectors.pkl'

CREATEEMBEDDINGS = "CREATE VIRTUAL TABLE embeddings USING vec0( sentence_id INTEGER PRIMARY KEY, embedding float[384])"
DROPEMBEDDINGS   = "DROP TABLE IF EXISTS embeddings"
SELECTALL        = 'SELECT * FROM sentences ORDER BY id\n'

# require
from numpy      import array
from ollama     import embed, ResponseError
from pandas     import read_csv
from pathlib    import Path
from pickle     import dump
from rdr        import configuration, ETC
from re         import sub
from sqlite_vec import load
from sqlite3    import connect
from struct     import pack
from sys        import stderr, argv, exit
from typing     import List

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# serializes a list of floats into a compact "raw bytes" format; makes things more efficient?
def serialize( vector: List[ float ] ) -> bytes : return pack( "%sf" % len( vector ), *vector )

# initialize
cache    = configuration( LIBRARY )/carrel/CACHE
database = configuration( LIBRARY )/carrel/ETC/DATABASE

# load database
stderr.write( "Loading database\n" )
connection = connect( database )
connection.enable_load_extension( True )
load( connection )
connection.execute( DROPEMBEDDINGS )
connection.execute( CREATEEMBEDDINGS )

# process each text in the given carrel; reading from the file system when I oguth to read from the database, no?
stderr.write( "Indexing texts\n" )
for record in connection.execute( SELECTALL ) :

	# parse
	id    = record[ 0 ] 
	title    = record[ 1 ] 
	idx      = record[ 2 ]
	sentence = record[ 3 ]
	
	# normalize
	#title    = title.replace( "'", "''" )
	#sentence = sentence.replace( '\r', '\n' )
	#sentence = sentence.replace( '\n', ' ' )
	#sentence = sentence.replace( "'",  "''")
	#sentence = sub( ' +' , ' ', sentence )

	# sql
	#sql = TEMPLATE
	#sql = sql.replace( '##TITLE##', title )
	#sql = sql.replace( '##IDX##', str( idx ) )
	#sql = sql.replace( '##SENTENCE##', sentence )

	# debug
	stderr.write( '        id: ' + str(id) + '\n' )
	stderr.write( '     title: ' + title + '\n' )
	stderr.write( '       idx: ' + str( idx ) + '\n' )
	stderr.write( '  sentence: ' + sentence + '\n' )
	stderr.write( '\n' )
		
	# vectorize the sentences; cpu-intensive
	try :
	
		# do the work
		embedding = embed( model=MODEL, input=sentence ).model_dump( mode='json' )[ 'embeddings' ][ 0 ]
	
		#print( embedding )
		#exit()
		
		# process each sentence/embeddding combination
		#for sentence, index, embedding in zip( sentences, indexes, embeddings ) :
			
		# do the work
		connection.execute( INSERT, [ id, serialize( embedding ) ] )	

	except ResponseError as e:

		stderr.write(f"Status Code: {e.status_code}; Error: {e.error}; Call Eric?\n")
		continue
	
# commit and close
connection.commit()
connection.close()

# cache vectors to the carrel as a file; the etc directory is becoming bloated
#with open( configuration( LIBRARY )/carrel/ETC/VECTORS, 'wb' ) as handle : dump( array( embeddings ), handle )

# done
exit()

