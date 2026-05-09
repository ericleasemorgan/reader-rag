#!/usr/bin/env python

# json2pathfinder.py - given a Distant Reader index.json file, output an HTML file akin to a pathfinder

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# November 19, 2025 - first investigations; after seeing that I got a B- for a pathfinder in library school
# November 20, 2025 - added summaries and filling out the content; Happy birthday to me!


# configure
LIBRARY             = 'localLibrary'
LLM                 = 'deepseek-v3.1:671b-cloud'
PROMPTSYSTEM        = 'You are a helpful academic librarian, and you respond in four sentences.'
PROMPTELABORATE     = 'What is "%s", and use only the following as the source of the answer: %s'
TEMPLATE            = '../etc/json2pathfinder-template.txt'
ELABORATE           = True
THRESHOLD           = 1
PATHFINDER          = 'pathfinder.htm'

# require
from datetime import datetime
from json     import loads
from ollama   import generate
from pathlib  import Path
from rdr      import configuration, BIBLIOGRAPHYJSON, STOPWORDS, ETC, CACHE
from sys      import argv, exit, stderr
from os       import chdir
from os.path  import dirname, abspath

# make sane
chdir( dirname( abspath( __file__ ) ) )

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ] 

# debug
stderr.write( 'Processing %s\n' % carrel )

# initialize
library  = configuration( LIBRARY )
with open( library/carrel/BIBLIOGRAPHYJSON ) as handle : bibliographics = loads( handle.read() )
with open( library/carrel/ETC/STOPWORDS )    as handle : stopwords = handle.read().splitlines()

# count and tabulate the keywords
keywords = {}
for index, record in enumerate( bibliographics ) :

	items = record[ 'keywords' ].split( '; ' )
	for item in items :
	
		# ignore stopwords
		if item in stopwords : continue
		
		# update the list of keyword frequencies
		if item in keywords : keywords[ item ] += 1
		else                : keywords[ item ] =  1	

# sort the frequency list by... frequency
keywords = sorted( keywords.items(), key=lambda x:x[ 1 ], reverse=True )
keywords.pop( 0 )

# process each keyword
seen     = []
toc      = []
sections = []
for index, keyword in enumerate( keywords ) :

	# re-initialize
	frequency = keyword[ 1 ]
	keyword   = keyword[ 0 ]
	citations = []
	summaries = []
	
	# sanity check; but this is a poor check
	if ' ' in keyword : continue
	
	# process each bibliographic; inefficient, I'm sure
	for record in bibliographics :
	
		# re-initialize
		id = record[ 'id' ]
		
		# don't do the work if it has already been done
		if id in seen : continue
		
		# check for desired record
		if keyword in record[ 'keywords' ].split( '; ' ) :
		
			# parse
			author    = record[ 'author' ]
			title     = record[ 'title' ]
			date      = record[ 'date' ]
			summary   = record[ 'summary' ]
			keywords  = record[ 'keywords' ]
			extension = record[ 'extension' ]
			
			# build a pseudo-citation
			url = '../' + CACHE + '/' + id + extension
			citation = ( '<li style="margin-bottom: 1em"><a href="%s">%s</a> by %s (%s) - %s <strong>Keywords</strong>: %s</li>' % ( url, title, author, date, summary, keywords ) )
			
			# update
			citations.append( citation )
			summaries.append( summary )
			seen.append( id )
			
	# another sanity check
	if len( citations ) > 0 :
	
		# based on the summaries, define the given keyword; tricky
		summary = ''
		if ELABORATE and len( summaries ) > THRESHOLD : 
		
			prompt  = PROMPTELABORATE % ( keyword, ' '.join( summaries ) )
			summary = generate( LLM, prompt, system=PROMPTSYSTEM )
			summary = summary[ 'response' ]
			
		# output
		sections.append( '<a id="%s"><h2>%s</h2></a><blockquote><em>%s</em></blockquote><ul>%s</ul>' % ( keyword, keyword.capitalize(), summary, '\n'.join( citations ) ) )

		# update
		toc.append( '<a href="#%s">%s</a>' % ( keyword, keyword.capitalize() ) )
	
# build the HTML
with open( TEMPLATE ) as handle : html = handle.read()
html = html.replace( '##CARREL##', carrel )
html = html.replace( '##TABLEOFCONTENTS##', '; '.join( toc ) )
html = html.replace( '##SECTIONS##', '\n'.join( sections ) )
html = html.replace( '##DATE##', datetime.today().strftime('%Y-%m-%d') )

# output and done
with open( '/'.join( [ str( library ), carrel, ETC, PATHFINDER ] ), 'w' ) as handle : handle.write( html )
exit()

