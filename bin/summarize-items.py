#!/usr/bin/env python

# summaries2carrel.py - given a carrel, summarize each item and update the carrel accordingly
# see: https://medium.com/@ryver.dev/building-a-simple-ai-powered-text-summarizer-with-transformers-in-python-0a31c848e1d2

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# April   28, 2024 - first cut
# June    26, 2024 - based on previous work; computationally expensive but more than plausible
# January 16, 2025 - added ability to use gpu


# pre-configure
MODEL         = 'deepseek-v3.1:671b-cloud'
SYSTEMPROMPT  = 'You are a business man, and you respond in one paragraph.'
PROMPT        = 'Summarize the following context: %s'
CONFIGURATION = 'localLibrary'
PATTERN       = '*.txt'
TEMPLATE      = "UPDATE bib SET 'summary' = '##SUMMARY##' WHERE id IS '##KEY##';"

# require
from pathlib      import Path
from rdr          import configuration, TXT, ETC, DATABASE
from sqlite3      import connect
from sys          import argv, exit, stderr
from ollama       import generate
from re           import sub

# get input
if len( argv ) != 2 : exit( "Usage: " + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# initialize
library    = Path( configuration( CONFIGURATION ) )
files      = library/carrel/TXT
connection = connect( library/carrel/ETC/DATABASE )
cursor     = connection.cursor()

# process each of the given files; summarize each item
files = sorted( list( files.glob( PATTERN ) ) )
lenth = str( len( files ) )
for index, file in enumerate( files ) :

	# re-initialize
	key    = file.stem
	prompt = ( PROMPT % ( sub( r'\s', ' ', open( file ).read() ) ) )

	# summarize
	try : summary = generate( MODEL, prompt, system=SYSTEMPROMPT )[ 'response' ]
	except : 
		stderr.write ( 'Error: File to big? Call Eric.\n\n' )
		continue
		
	# escape summary and create update statement
	summary = summary.replace( "'", "''" )
	update  = TEMPLATE.replace( '##KEY##', key ).replace( '##SUMMARY##', summary )
	
	# debug
	stderr.write( '  item #' + str( index + 1 ) + ' of ' + lenth + ': ' + update + '\n\n' )
	
	# do the work
	cursor.execute( update )
	connection.commit()
		
# clean up and done
connection.close()
exit()
