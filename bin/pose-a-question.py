#!/usr/bin/env python

# pose-a-question.py - given the name of a carrel, output a randomly selected question

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May 30, 2025 - last day at Notre Dame!


# configure
LIBRARY  = 'localLibrary'
SELECT   = 'SELECT sentence FROM sentences WHERE sentence LIKE "%?" ORDER BY RANDOM() LIMIT 1'
DATABASE = 'sentences.db'
CACHE    = '../etc/cached-carrel.txt'

# require
from rdr     import configuration, ETC
from sqlite3 import connect
from sys import argv, exit

from os      import chdir
from os.path import dirname, abspath

# make sane
chdir( dirname( abspath( __file__ ) ) )


# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# initialize
connection = connect( configuration( LIBRARY )/carrel/ETC/DATABASE )

# cache
with open( CACHE, 'w' ) as handle : handle.write( carrel )

# do the work, output, and done
results = connection.execute( SELECT ).fetchone()
sentence = results[ 0 ]
print( sentence )
exit()
