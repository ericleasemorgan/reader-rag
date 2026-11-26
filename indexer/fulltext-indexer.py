#!/usr/bin/env python

# index.py - make an SQL database full text searchable

# configure
LIBRARY  = 'localLibrary'
DATABASE = 'sentences.db'
CACHE    = 'sentences'
PATTERN  = '*.snt'

# SQL statements
CREATEINDX      = 'CREATE VIRTUAL TABLE indx USING FTS5( title, idx, sentence );'
CREATEINDX      = "CREATE VIRTUAL TABLE indx USING FTS5( title, idx, sentence, content='sentences', content_rowid='id' )"
CREATESENTENCES = "CREATE TABLE sentences (id INTEGER PRIMARY KEY, title TEXT, idx TEXT, sentence TEXT)"
DROPINDX        = 'DROP TABLE IF EXISTS indx;'
DROPSENTENCES   = 'DROP TABLE IF EXISTS sentences;'
DROPTRIGGER     = 'DROP TRIGGER IF EXISTS sentences_insert;'
INSERT          = "INSERT INTO sentences (title, idx, sentence) VALUES (?, ?, ?)"
TRIGGERINSERT   = "CREATE TRIGGER sentences_insert AFTER INSERT ON sentences BEGIN INSERT INTO indx(rowid, title, idx, sentence) VALUES (new.id, new.title, new.idx, new.sentence); END"

# require
#import os
#import re
from sqlite3 import connect
#import tempfile
#import sys
from rdr import ETC, configuration
from sys import stderr, argv, exit
from sqlite_vec import load
from pandas     import read_csv

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
	
# create full text table
stderr.write( 'Indexing; the carrel must be set up for full text searching.\n' )
stderr.write( 'Step #1 of 4: Creating table to contain full text...\n' )

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
	for sentence, index in zip( sentences, indexes ) : 
	
		stderr.write( '     title: ' + title + '\n' )
		stderr.write( '     index: ' + index + '\n' )
		stderr.write( '  sentence: ' + sentence + '\n' )
		stderr.write( '\n' )
		
		connection.execute( INSERT, [ title, index, sentence ] )

# commit, close, and done
connection.commit()
connection.close()
stderr.write( "Full text index created.\n" )
exit()

