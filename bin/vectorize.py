#!/usr/bin/env python

# vectorize.py - given a carrel, create a database of sentences and their embeddings
# see: https://github.com/asg017/sqlite-vec/

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May   16, 2025 - with a lack of hearing, a FOC, and because the CRC machines were under maintence
# May   17, 2025 - migrated to Euclidian (VEC_DISTANCE_L2) distances
# May   22, 2025 - added title of item and item (sentence) number to database
# June   7, 2025 - normalized sentences so they are always strings
# July   4, 2025 - using a new embedder; actually moved to Ollama
# March 30, 2026 - started caching vectors as a file
# March 31, 2026 - started caching vectors in the database
# April  2, 2026 - scaled back to older embedder because nomic mysteriously broke;cached vectors to a file 
# [Date]        - improved performance via batch inserts, incremental commits, and context management
# [Date]        - parallelized embedding generation using ThreadPoolExecutor

# MODEL:SIZE - locusai/multi-qa-minilm-l6-cos-v1:768:384
# MODEL:SIZE - nomic-embed-text:768

# configure
MODEL       = 'locusai/multi-qa-minilm-l6-cos-v1'
CREATE      = "CREATE TABLE sentences (title TEXT, idx TEXT, sentence TEXT, embedding FLOAT[384] CHECK (TYPEOF(embedding)=='blob' AND VEC_LENGTH(embedding)==384))"
INSERT      = "INSERT INTO sentences (title, idx, sentence, embedding) VALUES (?, ?, ?, ?)"
PATTERN     = '*.snt'
LIBRARY     = 'localLibrary'
DATABASE    = 'sentences.db'
CACHE       = 'sentences'
VECTORS     = 'vectors.pkl'
MAX_WORKERS = 4 # Adjust based on your system and Ollama capabilities

# require
from concurrent.futures import ThreadPoolExecutor, as_completed
from ollama     import embed, ResponseError
from pandas     import read_csv
from pathlib    import Path
from rdr        import configuration, ETC
from sqlite_vec import load
from sqlite3    import connect
from struct     import pack
from sys        import stderr, argv, exit

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# serializes a list of floats into a compact "raw bytes" format; makes things more efficient
def serialize( vector: list[ float ] ) -> bytes : return pack( "%sf" % len( vector ), *vector )

# function to process a single file in parallel
def process_file( file_path, model ):
	try:
		# re-initialize and normalize
		title = file_path.stem
		records = read_csv( file_path )
		sentences = [ str( sentence ) for sentence in records[ 'sentence' ] ]
		indexes = [ str( index ) for index in records[ 'idx' ] ]
		
		# vectorize the sentences; cpu-intensive
		embeddings = embed( model=model, input=sentences ).model_dump( mode='json' )[ 'embeddings' ]
		
		# prepare batch rows for executemany
		rows = [
			( title, index, sentence, serialize( embedding ) )
			for sentence, index, embedding in zip( sentences, indexes, embeddings )
		]
		return ( file_path, rows )
		
	except ResponseError as e:
		stderr.write(f"Status Code: {e.status_code}; Error: {e.error}; Call Eric?\n")
		return ( file_path, None )
	except Exception as e:
		stderr.write(f"Error processing {file_path}: {e}\n")
		return ( file_path, None )

# initialize
stderr.write( "Initializing\n" )
cache = configuration( LIBRARY )/carrel/CACHE

# (re-)create database
stderr.write( "Creating database\n" )
db_path = configuration( LIBRARY )/carrel/ETC/DATABASE
db_path.unlink( missing_ok=True )

# use a context manager to ensure the database connection is closed safely
with connect( db_path ) as database :
	database.enable_load_extension( True )
	load( database )
	database.execute( CREATE )
	
	# process each text in the given carrel in parallel
	stderr.write( "Indexing texts\n" )
	files = list( cache.glob( PATTERN ) )
	
	with ThreadPoolExecutor( max_workers=MAX_WORKERS ) as executor:
		futures = { executor.submit( process_file, file, MODEL ): file for file in files }
		
		count = 0
		for future in as_completed( futures ):
			file_path, rows = future.result()
			count += 1
			stderr.write( '  %s (%s)\n' % ( file_path, str( count ) ) )
			
			if rows:
				# do the batch insert sequentially in the main thread to avoid SQLite lock issues
				database.executemany( INSERT, rows )
				database.commit()

# done
exit()
