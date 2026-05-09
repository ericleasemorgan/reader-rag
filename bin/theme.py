#!/usr/bin/env python

# theme.py - given a few configurations, output a list of KMeans clusters and their most signficant words

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# March 18, 2026 - first documentation, but written a few days ago
# March 31, 2026 - using content from carrels; need to get vocabulary from embeddings instead!


# configure
DATABASE = 'sentences.db'
LIBRARY  = 'localLibrary'
SELECT   = 'SELECT sentence FROM sentences'

# require
from pathlib                         import Path
from rdr                             import configuration, ETC, STOPWORDS
from sklearn.cluster                 import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlite3                         import connect
from sys                             import argv, exit
     
# get input
if len( argv ) != 4 : exit( 'Usage: ' + argv[ 0 ] + " <carrel> <depth> <breadth>" )
carrel   = argv[ 1 ]
clusters = int( argv[ 2 ] )
topn     = int( argv[ 3 ] )

# get all sentences from the given carrel
sentences  = []
connection = connect( configuration( LIBRARY )/carrel/ETC/DATABASE )
for item in connection.execute( SELECT ).fetchall() : sentences.append( item[ 0 ] )

# get and normalize stopwords
with open( configuration( LIBRARY )/carrel/ETC/STOPWORDS ) as handle : stopwords = handle.read().splitlines()
stopwords = [ stopword.split( "'")[ 0 ] for stopword in stopwords ]
stopwords = [ stopword.lower() for stopword in stopwords ]

# instaniate models; caution, many parameters ahead
vectorizer = TfidfVectorizer( stop_words=stopwords, max_df=.98, min_df=.02 )
kmeans     = KMeans( n_clusters=clusters, init='k-means++', max_iter=128, n_init=8, random_state=42 )

# vectorize and fit all in one go
kmeans.fit( vectorizer.fit_transform( sentences ) )

# process each cluster; create a list of "topics"
topics     = []
vocabulary = vectorizer.get_feature_names_out()
clusters   = kmeans.cluster_centers_.argsort()[ :, ::-1 ]
for cluster in range( len( clusters ) ) :

	# look up and update
	keywords = [ vocabulary[ index ] for index in clusters[ cluster, :topn ] ]
	topics.append( keywords )
	
# create labels for each topic
labels = []
for topic in topics :
	
	# loop through each feature
	for feature in topic :

		# build the list, conditionally
		if feature in labels : continue
		labels.append( feature )
		break

# process each label/topic combination; create a list of sorted themes
themes = {}
for label, topic in zip( labels, topics ) : themes[ label ] = topic
themes = dict( sorted( themes.items() ) )

# output and done
for key in themes.keys() : print( '%s\t%s' % ( key, ' '.join( themes[ key ] ) ) )
exit()
