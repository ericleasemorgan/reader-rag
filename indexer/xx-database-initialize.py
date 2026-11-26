#!/usr/bin/env python

# initialize-database.py - given the name of a carrel, create a database of sentences

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# November 19, 2026 - first cut; while in the Culver Public Library
# November 20, 2026 - intialized embeddings with 9's to make all sentences irrelevant; Happy birthday to me!


# configure
LIBRARY  = 'localLibrary'
DATABASE = 'sentences.db'

CREATESENTENCES  = "CREATE TABLE sentences (id INTEGER PRIMARY KEY, title TEXT, idx TEXT, sentence TEXT)"
CREATEFULLTEXT   = "CREATE VIRTUAL TABLE indx USING FTS5( title, idx, sentence, content='sentences', content_rowid='id' )"
CREATEEMBEDDINGS = "CREATE VIRTUAL TABLE embeddings USING vec0( sentence_id INTEGER PRIMARY KEY, embedding float[384])"

TRIGGERINSERT    = "CREATE TRIGGER sentences_insert AFTER INSERT ON sentences BEGIN INSERT INTO indx(rowid, title, idx, sentences) VALUES (new.id, new.headline, new.body); END"


# require
from pandas     import read_csv
from rdr        import configuration, ETC
from sqlite_vec import load
from sqlite3    import connect
from struct     import pack
from sys        import stderr, argv, exit

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# initilize
#cache = configuration( LIBRARY )/carrel/CACHE

# create database
stderr.write( "Creating database\n" )
database = configuration( LIBRARY )/carrel/ETC/DATABASE
database.unlink( missing_ok=True )
database = connect( database )
#database.enable_load_extension( True )
#load( database )
database.execute( CREATESENTENCES )
#database.execute( CREATEFULLTEXT )
#database.execute( CREATEEMBEDDINGS )
#database.execute( TRIGGERINSERT )

exit()

# fill database
stderr.write( "Filling database with sentences\n" )
count = 0
for index, file in enumerate( cache.glob( PATTERN ) ):

	# increment and debug
	title =  file.stem
	count += 1
	stderr.write( '  %s (%s)\n' % ( file, str( count ) ) )

	# re-initialize and normalize
	records   = read_csv( file )
	sentences = list( records[ 'sentence' ] )
	sentences = [ str( sentence ) for sentence in sentences ]
	indexes   = list( records[ 'idx' ] )
	indexes   = [ str( index ) for index in indexes ]

	# do the work
	for sentence, index in zip( sentences, indexes ) : database.execute( INSERT, [ title, index, sentence, nines ] )	

# commit, close, and done
database.commit()
database.close()
stderr.write( "Creating database. Done.\n" )
exit()

