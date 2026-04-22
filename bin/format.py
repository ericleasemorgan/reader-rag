#!/usr/bin/env python

# sentences2paragraphs.py - given a list of sentences, output an "essay"; good for summarization
# see: https://medium.com/@npolovinkin/how-to-chunk-text-into-paragraphs-using-python-8ae66be38ea6

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May  25, 2025 - first cut; fun!
# June  6, 2025 - commented out shortenting and lengthening sentences
# July  4, 2025 - moved to Ollam and a different embedder


# configure
MODEL     = 'nomic-embed-text'
SENTENCES = '../etc/context.txt'
PSIZE     = 16

# require
from math                     import exp
from ollama                   import embed
from re                       import sub
from scipy.signal             import argrelextrema
from sklearn.metrics.pairwise import cosine_similarity
from sys                      import exit
import numpy                  as     np

from os      import chdir
from os.path import dirname, abspath

# make sane
chdir( dirname( abspath( __file__ ) ) )


def rev_sigmoid( x:float )->float : return ( 1 / ( 1 + exp( 0.5*x ) ) )
    
def activate_similarities( similarities:np.array, p_size=10 )->np.array :

        """ Function returns list of weighted sums of activated sentence similarities

        Args:
            similarities (numpy array): it should square matrix where each sentence corresponds to another with cosine similarity
            p_size (int): number of sentences are used to calculate weighted sum 

        Returns:
            list: list of weighted sums
        """
        
        # To create weights for sigmoid function we first have to create space. P_size will determine number of sentences used and the size of weights vector.
        x = np.linspace( -10, 10, p_size )
 
        # Then we need to apply activation function to the created space
        y = np.vectorize(rev_sigmoid) 
 
        # Because we only apply activation to p_size number of sentences we have to add zeros to neglect the effect of every additional sentence and to match the length ofvector we will multiply
        activation_weights = np.pad(y(x),(0,similarities.shape[0]-p_size))
 
        ### 1. Take each diagonal to the right of the main diagonal
        diagonals = [similarities.diagonal(each) for each in range(0,similarities.shape[0])]
 
        ### 2. Pad each diagonal by zeros at the end. Because each diagonal is different length we should pad it with zeros at the end
        diagonals = [np.pad(each, (0,similarities.shape[0]-len(each))) for each in diagonals]
 
        ### 3. Stack those diagonals into new matrix
        diagonals = np.stack(diagonals)
        ### 4. Apply activation weights to each row. Multiply similarities with our activation.
        diagonals = diagonals * activation_weights.reshape(-1,1)
 
        ### 5. Calculate the weighted sum of activated similarities
        activated_similarities = np.sum(diagonals, axis=0)

        return activated_similarities

# initialize
sentences = open( SENTENCES ).read().splitlines()

# vectorize and activated similaritites; for longer sentences increase the value of PSIZE
embeddings = embed( model=MODEL, input=sentences ).model_dump( mode='json' )[ 'embeddings' ]

try : similarities = activate_similarities( cosine_similarity(embeddings), p_size=PSIZE )
except ValueError as error : exit( "Number of sentences too small. If this error continues, call Eric.\n" )
	
# compute the minmimas -- the valleys between sentences
minmimas = argrelextrema( similarities, np.less, order=2 )

# break sentences into smaller ones
#sentece_length = [len(each) for each in sentences]
#long           = np.mean( sentece_length ) + np.std( sentece_length ) *2
#short          = np.mean( sentece_length ) - np.std( sentece_length ) *2
#text           = ''
#for sentence in sentences :
#
#    if len(sentence) > long:
#		# let's replace all the commas with dots
#        fragments = sentence.replace( ',', '.' )
#        for fragment in fragments.split("."): text+= f'{fragment}. '
#    else : text+= f'{sentence}. '
#
#sentences = text.split('. ')
#
## Now let's concatenate short ones
#text = ''
#for sentence in sentences:
#    if len(sentence) < short : text+= f'{sentence} '
#    else                     : text+= f'{sentence}. '
        
#Get the order number of the sentences which are in splitting points
splits = [ minmima for minmima in minmimas[ 0 ] ]

# Create empty string
text = ''
for index, sentence in enumerate( sentences ) :

    # Check if sentence is a minima (splitting point)
    if index in splits :
    
        # If it is than add a dot to the end of the sentence and a paragraph before it.
        text += f'\n\n{sentence} '

    else:
    
        # If it is a normal sentence just add a dot to the end and keep adding sentences.
        text += f'{sentence} '


# do the tiniest bit of normalization
text = sub( ' +', ' ', text ) 

# output and done
print( text )
exit()
       