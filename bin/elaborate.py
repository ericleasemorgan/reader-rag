#!/usr/bin/env python

# elaborate.py - given set of cached content and a query, address the query

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public license

# May 23, 2025 - first cut; building my own RAG system
# July 5, 2025 - started adding prompts


# configure
MODEL        = 'deepseek-v3.1:671b-cloud'
CONTEXT      = '../etc/context.txt'
PROMPT       = 'Answer the question "%s" and use only the following as the source of the answer: %s'
SYSTEMPROMPT = '../etc/system-prompt.txt'

# require
from ollama  import generate, ResponseError
from sys     import argv, exit
from re      import sub
from os      import chdir
from os.path import dirname, abspath

# get input
if len( argv ) != 2 : exit( 'Usage: ' + argv[ 0 ] + " <question>" )
question = argv[ 1 ]

# make sane
chdir( dirname( abspath( __file__ ) ) )

# initialize
system  = open( SYSTEMPROMPT ).read()
context = sub( r'\s', ' ', open( CONTEXT ).read() )
prompt  = ( PROMPT % ( question, context ))

# submit the work, output, and done
try :

	result = generate( MODEL, prompt, system=system )
	print( result[ 'response' ] )

except ResponseError as e:

    print(f"Error: {e.error}")
    print(f"Status Code: {e.status_code}")
    
    # Handle specific error types
    #if e.status_code == 404:
    #    print("Model not found. Try: ollama pull llama3.2")
    #elif e.status_code == 400:
    #    print("Bad request:", e.error)
    #elif e.status_code == 500:
    #    print("Server error:", e.error)
    #else:
    #    print(f"Unexpected error {e.status_code}: {e.error}")

exit()
