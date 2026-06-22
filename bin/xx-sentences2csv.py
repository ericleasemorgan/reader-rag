#!/usr/bin/env python

# sentences2csv.py - given a TEI file, output a CSV file of sentences

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June 12, 2026 - first cut


# configure
COLUMNS = [ 'item', 'index', 'sentence' ]

# require
from lxml    import etree
from pathlib import Path
from sys     import argv, exit
from pandas  import DataFrame

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <file>" )
file = argv[ 1 ]

# initialize
item = Path( file ).stem
xml  = etree.parse( file )

# find and process each sentence; create a list of records
records = []
for sentence in xml.xpath( '//body//s' ) :

		# update the list of records
		records.append( [ item, sentence.xpath( './@xml:id' )[ 0 ], sentence.text ] )
			
# create a dataframe from the records, output, and done
sentences = DataFrame( records, columns=COLUMNS )
print( sentences.to_csv( index=False ) )



