#!/usr/bin/env python

# elbow.py - given a 2D matrix, plot KMeans inertia

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# March 18, 2026 - first documentation, but written a few days ago
# April  2, 2026 - reading vectors from local cache and saving plot to figures


# configure
VECTORS    = 'vectors.pkl'
RANGE      = 16
COMPONENTS = 2
LIBRARY    = 'localLibrary'
ELBOW      = 'vectors-elbow.png'

from matplotlib.pyplot     import plot, grid, show, savefig 
from pathlib               import Path
from pickle                import load
from sklearn.cluster       import KMeans
from sklearn.decomposition import PCA
from rdr                   import configuration, ETC, FIGURES
from sys                   import argv, exit

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <carrel>" )
carrel = argv[ 1 ]

# load the previously cached set of vectors
with open( configuration( LIBRARY)/carrel/ETC/VECTORS, 'rb' ) as handle: X = load( handle )

# initialize PCA and fit the vectors all in one go
X = PCA( n_components=COMPONENTS ).fit_transform( X )

# calculate a list of inertias
inertia = []
for k in range( 1, RANGE ) :

	# fit and update
    kmeans = KMeans( n_clusters=k ).fit( X )
    inertia.append( kmeans.inertia_ )

# plot
plot( range( 1, RANGE ), inertia, marker='o' )
grid( True )

# output and done
savefig( configuration( LIBRARY)/carrel/FIGURES/ELBOW )
exit()
