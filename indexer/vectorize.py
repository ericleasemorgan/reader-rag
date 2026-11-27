#!/usr/bin/env python

# vectorize.py - given a carrel, create a database of sentences and their embeddings
# see: https://github.com/asg017/sqlite-vec/

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# configure
MODEL      = 'locusai/multi-qa-minilm-l6-cos-v1'
INSERT     = "INSERT INTO embeddings (sentence_id, embedding) VALUES (?, ?)"
LIBRARY    = 'localLibrary'
DATABASE   = 'sentences.db'

CREATEEMBEDDINGS = "CREATE VIRTUAL TABLE embeddings USING vec0( sentence_id INTEGER PRIMARY KEY, embedding float[384])"
DROPEMBEDDINGS   = "DROP TABLE IF EXISTS embeddings"
SELECTALL        = 'SELECT id, sentence FROM sentences ORDER BY id'

# require
from ollama     import embed, ResponseError
from rdr        import configuration, ETC
from sqlite_vec import load
from sqlite3    import connect
from struct     import pack
from sys        import stderr, argv, exit
from tqdm       import tqdm
from typing     import List

# tuning
BATCH_SIZE = 128

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# serializes a list of floats into a compact "raw bytes" format
def serialize( vector: List[ float ] ) -> bytes :
	return pack( "%sf" % len( vector ), *vector )

# initialize
database = configuration( LIBRARY )/carrel/ETC/DATABASE

# load database
stderr.write( "Loading database\n" )
connection = connect( database )
connection.enable_load_extension( True )
load( connection )
connection.execute( DROPEMBEDDINGS )
connection.execute( CREATEEMBEDDINGS )

# fetch all sentences upfront
stderr.write( "Loading sentences from database\n" )
records = connection.execute( SELECTALL ).fetchall()
stderr.write( f"Loaded {len(records)} sentences\n" )

# process in batches
stderr.write( "Generating embeddings\n" )
connection.execute( "BEGIN" )

for i in tqdm( range( 0, len( records ), BATCH_SIZE ),
               desc="Vectorizing", unit="batch" ):

	# get the current batch
	batch   = records[ i : i + BATCH_SIZE ]
	ids       = [ r[ 0 ] for r in batch ]
	sentences = [ str( r[ 1 ] ) for r in batch ]

	# embed the entire batch in a single API call
	try :
		response  = embed( model=MODEL, input=sentences )
		embeddings = response[ 'embeddings' ]

	except ResponseError as e :
		stderr.write( f"\nStatus Code: {e.status_code}; Error: {e.error}; Call Eric?\n" )
		continue

	# batch-insert all embeddings at once
	params = [ ( id, serialize( emb ) ) for id, emb in zip( ids, embeddings ) ]
	connection.executemany( INSERT, params )

# commit and close
connection.commit()
connection.close()
stderr.write( "\nDone.\n" )
exit()
