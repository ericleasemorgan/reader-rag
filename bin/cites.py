#!/usr/bin/env python

# cites.py - analize citations

# Eric Lease Morggan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June 20, 2025 - Happy Birthday, Christa; while at Sigma New Golf Outing


# configure
CITATIONS = '../etc/cached-cites.txt'
CARREL    = '../etc/cached-carrel.txt'
NAMES     = [ 'items', 'sentences' ]
LIBRARY   = 'localLibrary'
SCHEMA    = 'file://'
COLUMNS   = ['items', 'authors', 'titles', 'dates', 'summaries', 'keywords', 'caches' ]

# require
from pandas import read_csv
from rdr    import bibliography, configuration
from json   import loads, dumps
from sys    import argv, exit
from os      import chdir
from os.path import dirname, abspath

# make sane
chdir( dirname( abspath( __file__ ) ) )

# get input
if len( argv ) != 2 : exit( "Usage: " + argv[ 0 ] + " <human|json|csv>" )
output = argv[ 1 ]

# initialize
carrel         = open( CARREL ).read()
bibliographics = loads( bibliography( carrel, format='json', save=False ) )
citations      = read_csv( CITATIONS, sep='\t', names=NAMES )
library        = configuration( LIBRARY )

# loop through each citation; create lists of bibliographic elements
authors   = []
titles    = []
dates     = []
summaries = []
keywords  = []
caches    = []
for _, citation in citations.iterrows() :

	# parse
	id            = str( citation[ 'items' ] )
	bibliographic = next( ( bibliographic for bibliographic in bibliographics if bibliographic[ 'id' ] == id ), None )
	
	# update
	authors.append( str( bibliographic[ 'author' ] ) )
	titles.append( bibliographic[ 'title' ] )
	dates.append( str( bibliographic[ 'date' ] ) )
	summaries.append( bibliographic[ 'summary' ] )
	keywords.append( bibliographic[ 'keywords' ] )
	caches.append( SCHEMA + str(library/carrel/'cache'/( id + bibliographic[ 'extension' ] ) ) )

# augement the citations
citations[ 'authors' ]   = authors
citations[ 'titles' ]    = titles
citations[ 'dates' ]     = dates
citations[ 'summaries' ] = summaries
citations[ 'keywords' ]  = keywords
citations[ 'caches' ]    = caches

# group by items, and sort by count of sentences
citations = citations.groupby( COLUMNS, as_index=False )[ 'sentences' ].count()
citations = citations.sort_values( 'sentences', ascending=False )

# branch accordingly; human output
if output == 'human' :

	# process each citation
	for _, citation in citations.iterrows() :
	
		# parse
		item      = citation[ 'items' ]
		author    = citation[ 'authors' ]
		sentences = citation[ 'sentences' ]
		title     = citation[ 'titles' ]
		date      = citation[ 'dates' ]
		summary   = citation[ 'summaries' ]
		keywords  = citation[ 'keywords' ]
		cache     = citation[ 'caches' ]
		
		# output
		print( '       item: %s' % item )
		print( '     author: %s' % author )
		print( '      title: %s' % title )
		print( '       date: %s' % date )
		#print( '    summary: %s' % summary )
		print( '   keywords: %s' % keywords )
		print( '  sentences: %s' % sentences )
		print( '      cache: %s' % cache  )
		print()

elif output == 'json' : print( citations.to_json( orient='records', default_handler=str ) )
elif output == 'csv'  : print( citations.to_csv( index=False ) )
else                  : exit( "Unknown value for output (" + output + "). Usage: " + argv[ 0 ] + " <human|json|csv>" )

# done
exit()
