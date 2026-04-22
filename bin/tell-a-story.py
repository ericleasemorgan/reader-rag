#!/usr/bin/env python

# make-story.py - given a carrel use Markov modeling to output a short paragraph -- a story
# see: https://github.com/jsvine/markovify/

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May 20, 2025 - just for fun
# May 26, 2025 - selected a random item from the carrel; much faster!
# May 27, 2025 - added bibliographics


# configure
COUNT   = 2
LENGTH  = 4
MAXIMUM = 256
LIBRARY = 'localLibrary'
PATTERN = '*.txt'
SELECT  = "select author, title, date from bib where id is ?"
CACHE     = '../etc/cached-results.txt'

# require
from markovify import Text, combine
from pathlib   import Path
from random    import choice
from rdr       import configuration, TXT, ETC, DATABASE
from sqlite3   import connect
from sys       import argv, exit

from os      import chdir
from os.path import dirname, abspath

# make sane
chdir( dirname( abspath( __file__ ) ) )


# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# initialize
library = configuration( LIBRARY )
file    = choice( [ file for file in ( library/carrel/TXT).glob( PATTERN ) ] )

# get and output= bibliographics
key                     = file.stem 
connection              = connect( library/carrel/ETC/DATABASE )
( author, title, date ) = connection.execute( SELECT, [ key ] ).fetchone()
print( 'From "%s" by %s (%s) :: %s\n' % ( title, author, date, key ) )

# model the text, and generate "count" paragraphs
model   = Text( open( file ).read() )
cache   = []
for i in range( COUNT ) : 

	# create a set of "legth" sentences
	sentences = []
	for j in range( LENGTH ) :
	
		# create a setence "maximum" characters long
		sentences.append( model.make_short_sentence( MAXIMUM ) )

	# output
	print( ' '.join( sentences ) + '\n' )

	# CACHE
	cache.append( ' '.join( sentences ) )
	
# output some more and done
with open( CACHE, 'w' ) as handle : handle.write( '\n'.join( cache ) )
exit()
