#!/usr/bin/env python

# rrag.py - a command-line interface used to do RAG against Distant Reader study carrels

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June      3, 2026 - started yesterday, and today embellished search
# June      4, 2026 - added lexicons to search
# June     11, 2026 - added reformat
# November 13, 2026 - added match
# November 14, 2026 - hard-coded personas and lengths


# require
from json    import dumps
from pathlib import Path
from rrag    import Searcher, Citations, Cacher, Summarizer, Settings, Elaborate, Reformatter, Matcher
import click
import rdr


# match
@click.command()
@click.argument( 'carrel' )
@click.option( '--query',   '-q', default='love' )
def match( carrel, query ) : 
	'''Fulltext search <carrel> with <query> and retrieve sentences'''

	# search; results get cached
	results = Matcher().match( carrel, query )

	# get sentences, format, and done
	sentences = Citations().to_sentences()
	paragraph = ' '.join( sentences )
	click.echo( paragraph )


# search
@click.command()
@click.argument( 'carrel' )
@click.option( '--type',    '-t', default='simple', type=click.Choice( [ 'simple', 'keywords', 'unigrams', 'bigrams', 'nouns', 'semantics', 'lexicon' ] ) )
@click.option( '--query',   '-q', default='love' )
@click.option( '--depth',   '-d', default=1 )
@click.option( '--breadth', '-b', default=8 )
def search( carrel, type, query, breadth, depth ) :
	'''Semantic search <carrel> with <query> and retrieve <depth> sentences'''
	
	# configure
	LIBRARY = 'localLibrary'
	
	if type == 'lexicon' :
	
		lexicon = rdr.configuration( LIBRARY )/carrel/( rdr.ETC )/( rdr.LEXICON )
		with open( lexicon ) as handle : lexicon = handle.read().splitlines()
		query = ' '.join( lexicon )
	
	if type == 'nouns' :
	
		nouns = rdr.pos( carrel, select='words', like='N', count=True, normalize=True ).splitlines()[ :breadth ]
		nouns = [ noun.split( '\t' )[ 0 ] for noun in nouns ]
		query = ' '.join( nouns )
	
	if type == 'keywords' :
	
		keywords = rdr.keywords( carrel, count=True ).splitlines()[ :breadth ]
		keywords = [ keyword.split( '\t' )[ 0 ] for keyword in keywords ]
		query    = ' '.join( keywords )
	
	if type == 'unigrams' :
	
		unigrams = rdr.ngrams( carrel, size=1, count=True ).splitlines()[ :breadth ]
		unigrams = [ unigram.split( '\t' )[ 0 ] for unigram in unigrams ]
		query    = ' '.join( unigrams )
	
	if type == 'bigrams' :
	
		bigrams = rdr.ngrams( carrel, size=2, count=True ).splitlines()[ :breadth ]
		bigrams = [ bigram.split( '\t' )[ 0 ] for bigram in bigrams ]
		query    = ' '.join( bigrams )
	
	if type == 'semantics' :
	
		if ' ' in query :
		
			words = ''
			
			for word in query.split() :
				
				semantics = rdr.word2vec( carrel, type='similarity', query=word, topn=breadth ).splitlines()
				semantics = [ semantic.split( '\t' )[ 0 ] for semantic in semantics ]
				semantics.append( word )
				words = words + ' '.join( semantics )
			
			query = words
			
		else :
		
			semantics = rdr.word2vec( carrel, type='similarity', query=query, topn=breadth ).splitlines()
			semantics = [ semantic.split( '\t' )[ 0 ] for semantic in semantics ]
			semantics.append( query )
			query     = ' '.join( semantics )
		
	# search; results get cached
	results = Searcher().search( carrel, query, depth )

	# get sentences, format, and done
	sentences = Citations().to_sentences()
	paragraph = ' '.join( sentences )
	click.echo( paragraph )


# summarize
@click.command()
def summarize() : 
	'''Distill search results'''
	click.echo( Summarizer().summarize() )


# reformat
@click.command()
def reformat() : 
	'''Create paragraphs from search results'''
	click.echo( Reformatter().reformat() )


# elaborate
@click.command()
@click.argument( 'question' )
def elaborate( question ) : 
	'''Apply <question/command> to search results'''
	click.echo( Elaborate().elaborate( question ) )


# get settings
@click.command()
def get() : 
	'''Get preferences and caches'''
	
	# configure
	SETTINGS = [ 'persona', 'length', 'carrel' ]
	
	# create a list of all the settings and done
	settings = {}
	for setting in SETTINGS : settings[ setting ] = Settings().get( setting )
	click.echo( dumps( settings ) )


# set settings
@click.command()
@click.argument( 'setting', default='persona', type=click.Choice( [ 'persona', 'length' ] ) )
def set( setting ) : 
	'''Set preferences'''
	
	# configure
	PERSONAS = [ 'a child in the second grade', 'a child in the eigth grade', 'a high school valedictorian', 'a sophmoric college student', 'a helpful librarian', 'a sarcastic librarian', 'a university professor', 'an erudite scholar', 'an artist' ]
	LENGTHS  = [ 'a single word', 'two words', 'four words', 'a single sentence', 'two sentences', 'four sentences', 'one paragraph', 'two paragraphs', 'four paragraphs' ]

	# initialize
	if setting   == 'persona' : choices = PERSONAS
	elif setting == 'length'  : choices = LENGTHS
	
	# read, display, and get a setting
	choice = choose( choices, setting )
	
	# save and done
	Settings().set( setting, choice )
	click.echo( 'Success. The %s has been set to "%s".' % ( setting, choice ) )
	
	
# cite
@click.command()
@click.argument( 'format', default='json', type=click.Choice( [ 'json', 'csv', 'tsv' ] ) )
def cite( format ) : 
	'''Cite results'''
	click.echo( Citations().to_citations( format ) )
	
	
def choose(lines, type):
    print("\nChoose a %s:\n" % type )
    for i, line in enumerate(lines, 1): print(f"  {i}. {line}")
    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(lines): return lines[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(lines)}")
        except ValueError:
            print("Please enter a valid number")


@click.group()
def rrag(): pass


# build the commands
rrag.add_command(cite)
rrag.add_command(get)
rrag.add_command(elaborate)
rrag.add_command(match)
rrag.add_command(search)
rrag.add_command(set)
rrag.add_command(summarize)
rrag.add_command(reformat)


# go
if __name__ == '__main__': rrag()

