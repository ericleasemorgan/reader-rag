#!/usr/bin/env python

# summarize.py - use an LLM to summarize the cached results

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public license

# May 23, 2025 - first cut; building my own RAG system
# July 5, 2025 - adding more sophisticated prompts


# configure
MODEL        = 'deepseek-v3.1:671b-cloud'
CONTEXT      = '../etc/context.txt'
SYSTEMPROMPT = '../etc/system-prompt.txt'
PROMPT       = 'Summarize the following context: %s'

# require
from ollama  import generate, ResponseError
from os      import chdir
from os.path import dirname, abspath
from re      import sub
from sys     import exit

# make sane
chdir( dirname( abspath( __file__ ) ) )

# initialize
context = sub( r'\s', ' ', open( CONTEXT ).read() )
system  = open( SYSTEMPROMPT ).read()
prompt  = ( PROMPT % ( context ) )

# try to do the work
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
