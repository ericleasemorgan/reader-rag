#!/usr/bin/env python

# fulltext-indexer.py - create a full text index of a given carrel

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# November 26, 2026 - not first documentation and surely written a while ago


# configure
LIBRARY  = 'localLibrary'
DATABASE = 'sentences.db'
CACHE    = 'sentences'
PATTERN  = '*.snt'

# SQL statements
CREATEINDX      = "CREATE VIRTUAL TABLE indx USING FTS5( title, idx, sentence, content='sentences', content_rowid='id' )"
CREATESENTENCES = "CREATE TABLE sentences (id INTEGER PRIMARY KEY, title TEXT, idx TEXT, sentence TEXT)"
DROPINDX        = 'DROP TABLE IF EXISTS indx;'
DROPSENTENCES   = 'DROP TABLE IF EXISTS sentences;'
DROPTRIGGER     = 'DROP TRIGGER IF EXISTS sentences_insert;'
INSERT          = "INSERT INTO sentences (title, idx, sentence) VALUES (?, ?, ?)"
TRIGGERINSERT   = "CREATE TRIGGER sentences_insert AFTER INSERT ON sentences BEGIN INSERT INTO indx(rowid, title, idx, sentence) VALUES (new.id, new.title, new.idx, new.sentence); END"

CREATEEMBEDDINGS = "CREATE VIRTUAL TABLE embeddings USING vec0( sentence_id INTEGER PRIMARY KEY, embedding float[384])"
DROPEMBEDDINGS   = "DROP TABLE IF EXISTS embeddings"

# require
from pandas     import read_csv
from rdr        import ETC, configuration
from sqlite_vec import load
from sqlite3    import connect
from sys        import stderr, argv, exit
from tqdm       import tqdm

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# initialize
database = configuration( LIBRARY )/carrel/ETC/DATABASE
cache    = configuration( LIBRARY )/carrel/CACHE

# create database
stderr.write( "Creating full text tables\n" )
connection = connect( database )
connection.enable_load_extension( True )
load( connection )
connection.execute( DROPSENTENCES )
connection.execute( DROPTRIGGER )
connection.execute( DROPINDX )
connection.execute( CREATESENTENCES )
connection.execute( CREATEINDX )
connection.execute( TRIGGERINSERT )

connection.execute( DROPEMBEDDINGS )
connection.execute( CREATEEMBEDDINGS )
 
# create full text table
stderr.write( 'Indexing; the carrel must be set up for full text searching.\n' )
stderr.write( 'Step #1 of 4: Creating table to contain full text...\n' )

# get the list of files so tqdm knows the total
files = sorted( cache.glob( PATTERN ) )
stderr.write( "Filling database with sentences\n" )

# fill database with a progress bar
for file in tqdm( files, desc="Indexing", unit="file" ):

	# initialize
	title = file.stem

	# re-initialize and normalize
	records   = read_csv( file )
	sentences = list( records[ 'sentence' ] )
	sentences = [ str( sentence ) for sentence in sentences ]
	indexes   = list( records[ 'idx' ] )
	indexes   = [ str( index ) for index in indexes ]

	# do the work
	for sentence, index in zip( sentences, indexes ) : connection.execute( INSERT, [ title, index, sentence ] )

# commit, close, and done
connection.commit()
connection.close()
stderr.write( "\nFull text index created.\n" )
exit()
