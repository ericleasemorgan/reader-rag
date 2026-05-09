#!/usr/bin/env python

# index.py - make an SQL database full text searchable

# configure
LIBRARY        = 'localLibrary'
DATABASE       = 'sentences.db'
SANITYCHECK    = "SELECT * FROM sqlite_master WHERE type='table' AND name='fulltext';"
DROPFULLTEXT   = 'DROP TABLE IF EXISTS fulltext;'
CREATEFULLTEXT = 'CREATE TABLE fulltext ( title TEXT, item INT, sentence TEXT );\n'
TEMPLATE       = "INSERT INTO fulltext ( title, item, sentence ) VALUES ( '##TITLE##', '##ITEM##', '##SENTENCE##' );\n"
DROPINDX       = 'DROP TABLE IF EXISTS indx;'
SELECTALL      = 'SELECT * FROM sentences ORDER BY title, item;\n'

# these are what we want
CREATEINDX     = 'CREATE VIRTUAL TABLE indx USING FTS5( title, item, sentence );'
INDEX          = 'INSERT INTO indx SELECT title, item, sentence FROM fulltext;';

# require
import os
import re
import sqlite3
import tempfile
import sys
from rdr import ETC, configuration
from sys import argv, exit

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# initialize
database    = configuration( LIBRARY )/carrel/ETC/DATABASE
transaction = tempfile.NamedTemporaryFile( delete=False ).name

# connect to database
connection                 = sqlite3.connect( database )
connection.isolation_level = None
cursor                     = connection.cursor()
	
# create full text table
sys.stderr.write( 'Indexing; the carrel must be set up for full text searching.\n' )
sys.stderr.write( 'Step #1 of 4: Creating table to contain full text...\n' )
connection.execute( DROPFULLTEXT )
connection.execute( CREATEFULLTEXT )

# read full text
sys.stderr.write( 'Step #2 of 4: Reading full text; please be patient...\n' )
with open( transaction, 'w', encoding='utf-8'  ) as handle : handle.write( 'BEGIN TRANSACTION;\n' )
for record in connection.execute( SELECTALL ) :

	# parse
	title    = record[ 0 ] 
	item     = record[ 1 ]
	sentence = record[ 2 ]
	
	# normalize
	title    = title.replace( "'", "''" )
	sentence = sentence.replace( '\r', '\n' )
	sentence = sentence.replace( '\n', ' ' )
	sentence = sentence.replace( "'",  "''")
	sentence = re.sub( ' +' , ' ', sentence )

	# sql
	sql = TEMPLATE
	sql = sql.replace( '##TITLE##', title )
	sql = sql.replace( '##ITEM##', str( item ) )
	sql = sql.replace( '##SENTENCE##', sentence )

	# debug
	sys.stderr.write( '     title: ' + title + '\n' )
	sys.stderr.write( '      item: ' + str( item ) + '\n' )
	sys.stderr.write( '  sentence: ' + sentence + '\n' )
	sys.stderr.write( '\n' )

	# update
	with open( transaction, 'a', encoding='utf-8'  ) as handle : handle.write( sql )

# close the transaction
with open( transaction, 'a', encoding='utf-8'  ) as handle : handle.write( 'END TRANSACTION;\n' )

# write full text
sys.stderr.write( 'Step #3 of 4: Writing full text to database...\n' )
with open( transaction, encoding='utf-8'  ) as handle :

	# repeat forever, almost
	while True :
		sql = handle.readline()
		if not sql : break
		connection.execute( sql )

# index; do the actual work
sys.stderr.write( 'Step #4 of 4: Indexing; please be patient...\n' )
connection.execute( DROPINDX )
connection.execute( CREATEINDX )
connection.execute( INDEX )

# clean up, and done
os.remove( transaction )
sys.stderr.write( 'Done. Happy searching!\n' )
exit()

	
