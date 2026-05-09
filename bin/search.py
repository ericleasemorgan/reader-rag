#!/usr/bin/env python

# search.py = given a query, search a database and output results
# see: 
#   https://github.com/asg017/sqlite-vec/
#   https://github.com/asg017/sqlite-vec/blob/main/examples/simple-python/demo.py
#   https://github.com/asg017/sqlite-vec/issues/116

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributred under a GNU Public License

# May  16, 2025 - with a lack of hearing, a FOC, and because the CRC machines were under maintence
# May  17, 2025 - migrated to Euclidian (VEC_DISTANCE_L2) distances
# May  30, 2025 - added cache; tomorrow is my last day here at Notre Dame, yikes!
# June  6, 2025 - calling it my own; added a bit of documentation
# June 13, 2025 - added additional caches
# Jult  4, 2025 - changed embedder

# MODEL - locusai/multi-qa-minilm-l6-cos-v1:768
# MODEL - nomic-embed-text


# configure
MODEL         = 'locusai/multi-qa-minilm-l6-cos-v1'
LIBRARY       = 'localLibrary'
SELECT        = "SELECT title, item, sentence, VEC_DISTANCE_L2(embedding, ?) AS distance FROM sentences ORDER BY distance LIMIT ?"
DATABASE      = 'sentences.db'
COLUMNS       = [ 'titles', 'items', 'sentences', 'distances' ]
CACHEDRESULTS = '../etc/context.txt'
CACHEDCARREL  = '../etc/cached-carrel.txt'
CACHEDQUERY   = '../etc/cached-query.txt'
CACHEDCITES   = '../etc/cached-cites.txt'

# require
from ollama     import embed
from pandas     import DataFrame
from rdr        import configuration, ETC
from sqlite_vec import load
from sqlite3    import connect
from struct     import pack
from sys        import argv, exit
from typing     import List

from os      import chdir
from os.path import dirname, abspath

# make sane
chdir( dirname( abspath( __file__ ) ) )

# get input
if len( argv ) != 4 : exit( 'Usage: ' + argv[ 0 ] + " <carrel> <query> <depth>" )
carrel = argv[ 1 ]
query  = argv[ 2 ]
depth  = argv[ 3 ]

# serializes a list of floats into a compact "raw bytes" format; makes things more efficient?
def serialize( vector: List[float]) -> bytes : return pack( "%sf" % len( vector ), *vector )

# initialize
library = configuration( LIBRARY )

# get all sentences; might not be scalable
database = connect( library/carrel/ETC/DATABASE )
database.enable_load_extension( True )
load( database )

# save the cache for other possible processes
with open( CACHEDCARREL, 'w' ) as handle : handle.write( carrel )

# save the cache for other possible processes
with open( CACHEDQUERY, 'w' ) as handle : handle.write( query )

# vectorize query and search; get a set of matching records
query   = embed( model=MODEL, input=query ).model_dump( mode='json' )[ 'embeddings' ][ 0 ]
records = database.execute( SELECT, [ serialize( query ), depth ] ).fetchall()

# process each result; create a list of sentences
sentences = []
for record in records :

	# parse
	title    = record[ 0 ]
	item     = record[ 1 ]
	sentence = record[ 2 ]
	distance = record[ 3 ]
	
	# update
	sentences.append( [title, item, sentence, distance ] )

# create a dataframe of the sentences and sort by title
sentences = DataFrame( sentences, columns=COLUMNS )
sentences = sentences.sort_values( [ 'titles', 'items' ] )

# process/output each sentence; along the way, create a cache
results = []
cites   = []
for index, result in sentences.iterrows() :

	# parse
	title    = result[ 'titles' ]
	item     = result[ 'items' ]
	sentence = result[ 'sentences' ]
	
	# update the caches
	results.append( sentence )
	cites.append( '\t'.join( [ title, str( item ) ] ) )

	# output
	print( sentence )
	
# save the remaining caches and done
with open( CACHEDCITES, 'w' )   as handle : handle.write( '\n'.join( cites ) )
with open( CACHEDRESULTS, 'w' ) as handle : handle.write( '\n'.join( results ) )
exit()