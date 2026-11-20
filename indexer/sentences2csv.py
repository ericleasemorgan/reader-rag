#!/usr/bin/env python

# sentences2csv.py - given a TEI file, output a CSV file of sentences

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June     12, 2026 - first cut
# June     13, 2026 - output to the file system; blazingly fast!?
# November 19, 2026 - parallelized but a while ago; adjusting entire index.sh stack


# configure
COLUMNS    = [ 'item', 'idx', 'sentence' ]
CACHE      = 'sentences'
EXTENSION  = '.snt'
LIBRARY    = 'localLibrary'
PATTERN    = '*.xml'
XML        = 'xml'
WORKERS    = 16 

# require
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml               import etree
from pandas             import DataFrame
from pathlib            import Path
from rdr                import configuration, TXT
from shutil             import rmtree
from sys                import stderr, argv, exit


# given a file, output csv to the file system
def file2cache( file, cache ):

    try:
    
        # initialize
        item = Path( file ).stem
        xml  = etree.parse( str( file ) )

        # find and process each sentence in the given file; create a list of records
        records = []
        for sentence in xml.xpath( '//body//s' ) : records.append( [ item, sentence.xpath( './@xml:id' )[ 0 ], sentence.text ] )
                
        # create a dataframe from the records and output
        sentences = DataFrame( records, columns=COLUMNS )
        with open( cache/( item + EXTENSION ), 'w' ) as handle : handle.write( sentences.to_csv( index=False ) )
            
        # done
        return str( file )
        
    except Exception as e : return f"Error processing {file}: {e}"


# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# initialize
carrel = configuration( LIBRARY )/carrel
cache  = carrel/CACHE

# make sane; re-initialize
rmtree( cache, ignore_errors=True )
cache.mkdir()

# in parallel, find and process each file in the given carrel
files = list( ( carrel/XML ).glob( PATTERN ) )
with ThreadPoolExecutor( max_workers=WORKERS ) as workers :

    # submit the work; someone will say I have VERY bad variable names here and below
    results = [ workers.submit( file2cache, file, cache ) for file in files ]
    
    # examine returned results
    for result in as_completed( results ) :
    
        result = result.result()
        if result : stderr.write( result + '\n' )

# done
exit()
