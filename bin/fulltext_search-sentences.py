#!/usr/bin/env python

# fulltext_search-sentences.py - given a carrel and a query, search a database

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distriburted under a GNU Public License

# May 9, 2026 - first cut


# configure
DATABASE = 'sentences.db'
LIBRARY  = 'localLibrary'
TEMPLATE = "SELECT title AS 'item', item AS 'index', sentence FROM indx WHERE indx MATCH '##QUERY##' ORDER BY RANK;"

# require
from pandas  import read_sql_query
from rdr     import ETC, configuration
from sqlite3 import connect
from sys     import argv, exit

# get input
if len( argv ) != 3 : exit( 'Usage: ' + argv[ 0 ] + " <carrel> <query>" )
carrel = argv[ 1 ]
query  = argv[ 2 ]

# initialize
database   = configuration( LIBRARY )/carrel/ETC/DATABASE
connection = connect( database )

# build sql, search, output, and done
sql  = TEMPLATE.replace( '##QUERY##', query )
rows = read_sql_query( sql, connection )
print( rows.to_json( orient='index' ) )
exit()
