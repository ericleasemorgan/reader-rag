#!/usr/bin/env python

# reduce.py - use PCA to reduce a large matrix to only two or three dimensions
# see: https://github.com/AccelAI/AI-Tutorials/blob/main/PCA_Tutorial/PCA_Tutorial.ipynb

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# March 18, 2026 - first documentation, but written a few days ago
# March 20, 2026 - added command-line input
# March 31, 2026 - removed scaling as well as caching
# April  2, 2026 - reading vectors from local cache and saving plot to figures


# configure
VECTORS  = 'vectors.pkl'
LIBRARY  = 'localLibrary'
REDUCED2 = 'vectors-reduced-2.png'
REDUCED3 = 'vectors-reduced-3.png'

# require
from matplotlib.pyplot     import scatter, show, figure, savefig
from pathlib               import Path
from pickle                import load
from sys                   import stderr, argv, exit
from sklearn.decomposition import PCA
from rdr                   import configuration, ETC, FIGURES

# get input
if len( argv ) != 3 : exit( 'Usage: ' + argv[ 0 ] + " <carrel> <2|3>" )
carrel     = argv[ 1 ]
components = int( argv[ 2 ] )

# load the vectors
with open( configuration( LIBRARY)/carrel/ETC/VECTORS, 'rb' ) as handle: X = load( handle )

# initialize PCA, fit the vectors, and cache; do the work
pca         = PCA( n_components=components )
projections = pca.fit_transform( X )

# branch accordingly; visualize
if components == 2 :

	# create a 2d scatter plot
	scatter( projections[ :,0 ], projections[ :,1 ], s=16 )
	savefig( configuration( LIBRARY)/carrel/FIGURES/REDUCED2 )
	
elif components == 3 :
	
	# create a 3d scatter plot; kewl
	figure = figure()
	figure = figure.add_subplot( 111, projection='3d' )
	figure.scatter( projections[ :,0 ], projections[ :,1 ], projections[ :,2 ], s=16 )
	savefig( configuration( LIBRARY)/carrel/FIGURES/REDUCED3 )

else : exit( 'Invalid value for components (%s). Call Eric.' % str( components ) )

# output
exit()



