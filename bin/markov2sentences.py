#!/usr/bin/env python

# markov2sentences.py - given a carrel and an existing two-word phrase, output sentences
# see: https://www.geeksforgeeks.org/markov-chains-in-nlp/


# configure
COUNT   = 96
LIBRARY = 'localLibrary'
CORPUS  = 'carrel.txt'
CACHE   = '../etc/cached-results.txt'

# require
from nltk          import ngrams
from nltk.tokenize import word_tokenize, sent_tokenize
from rdr           import configuration, ETC
from re            import sub
from random        import choices
from sys           import argv, exit

from os      import chdir
from os.path import dirname, abspath

# make sane
chdir( dirname( abspath( __file__ ) ) )


# get input
if len( argv ) != 4 : exit( 'Usage: ' + argv[ 0 ] + " <carrel> <two-word phrase> <depth>" )
carrel = argv[ 1 ]
phrase = argv[ 2 ]
depth  = argv[ 3 ]


# generate sentences
def generate_entences(markov, limit=100, start='i am'):
    n = 0
    curr_state = start
    next_state = None
    story = ""
    story += curr_state+" "
    while n < limit:
        next_state = choices(
            list(markov[curr_state].keys()),
            list(markov[curr_state].values()))

        curr_state = next_state[0]
        story += curr_state+" "
        n += 1
    return story


# tokenize
def Tokenize(txt):
    cleaned_txt = []
    for line in txt:    	
        line = line.lower()
        line = sub(r"[,.\"\'!@#$%^&*(){}?/;`~:<>+=-\\]", "", line)
        tokens = word_tokenize(line)
        words = [word for word in tokens if word.isalpha()]
        cleaned_txt += words
    return cleaned_txt


# model
class MarkovModel:

    def __init__(self, n_gram=2):
        self.n_gram = n_gram
        self.markov_model = {}

    def build_model(self, text):
        for i in range(len(text)-self.n_gram-1):
            curr_state, next_state = "", ""
            for j in range(self.n_gram):
                curr_state += text[i+j] + " "
                next_state += text[i+j+self.n_gram] + " "
            curr_state = curr_state[:-1]
            next_state = next_state[:-1]
            if curr_state not in self.markov_model:
                self.markov_model[curr_state] = {}
                self.markov_model[curr_state][next_state] = 1
            else:
                if next_state in self.markov_model[curr_state]:
                    self.markov_model[curr_state][next_state] += 1
                else:
                    self.markov_model[curr_state][next_state] = 1

        # calculating transition probabilities
        for curr_state, transition in self.markov_model.items():
            total = sum(transition.values())
            for state, count in transition.items():
                self.markov_model[curr_state][state] = count/total

    def get_model(self):
        return self.markov_model
        

# initialize
corpus = configuration( LIBRARY )/carrel/ETC/CORPUS
tokens = Tokenize( sent_tokenize( open( corpus ).read() ) )
model  = MarkovModel()
model.build_model(tokens)

# do the work
cache   = []

for i in range( COUNT ) :

	sentence = generate_entences( model.get_model(), start=phrase, limit=int(depth))
		# update the cache
	cache.append( sentence )


	print( sentence )
	
# output some more and done
with open( CACHE, 'w' ) as handle : handle.write( '\n'.join( cache ) )
exit()

