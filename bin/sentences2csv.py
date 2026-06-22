#!/usr/bin/env python

# sentences2csv.py - given a TEI file, output a CSV file of sentences

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June 12, 2026 - first cut
# June 13, 2026 - output to the file system; blazingly fast!?
# [Date]       - parallelized execution using ThreadPoolExecutor

# configure
COLUMNS    = [ 'item', 'idx', 'sentence' ]
CACHE      = 'sentences'
EXTENSION  = '.snt'
LIBRARY    = 'localLibrary'
PATTERN    = '*.xml'
XML        = 'xml'
MAX_WORKERS = 8  # Adjust based on your system's cores

# require
from lxml    import etree
from pathlib import Path
from sys     import stderr, argv, exit
from pandas  import DataFrame
from rdr     import configuration, TXT
from shutil  import rmtree
from concurrent.futures import ThreadPoolExecutor, as_completed

# define a function to process a single file
def process_file(file, cache):
    try:
        # initialize
        item = Path(file).stem
        xml  = etree.parse(str(file))

        # find and process each sentence in the given file; create a list of records
        records = []
        for sentence in xml.xpath( '//body//s' ) :
            # update the list of records
            records.append( [ item, sentence.xpath( './@xml:id' )[ 0 ], sentence.text ] )
                
        # create a dataframe from the records, output, and done
        sentences = DataFrame( records, columns=COLUMNS )
        with open( cache/( item + EXTENSION ), 'w' ) as handle : 
            handle.write( sentences.to_csv( index=False ) )
            
        return str(file)
        
    except Exception as e:
        return f"Error processing {file}: {e}"

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# initialize
carrel = configuration( LIBRARY )/carrel
cache  = carrel/CACHE

# make sane
rmtree( cache, ignore_errors=True )
cache.mkdir()

# find and process each file in the given carrel in parallel
files = list( ( carrel/XML ).glob( PATTERN ) )
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [ executor.submit(process_file, file, cache) for file in files ]
    
    for future in as_completed(futures):
        result = future.result()
        if result:
            # debug
            stderr.write( result + '\n' )

# done
exit()
