#!/usr/bin/env bash

# search-with-semantics.sh - another front-end to search.py

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May 13, 2025 - first cut; in a FOC ("Fit Of Creativity")
# May 14, 2025 - added semantics


# configure
SEARCH='../bin/search.py'

# get input
if [[ -z $1 || -z $2  || -z $3 || -z 4 ]]; then
	echo "Usage: $0 <carrel> <word> <breadth> <depth>" >&2
	exit
fi
CARREL=$1
WORD=$2
BREADTH=$3
DEPTH=$4

cd "$(dirname "$0")"

# use the Reader to build a query of semantically related word to the given word
QUERY="$WORD "$(rdr semantics $CARREL -q $WORD -s $BREADTH | cut -f1 | tr '\n' ' ')

# do the work and done
echo
$SEARCH $CARREL "$QUERY" $DEPTH | sed "s/$/ /" | fmt 
echo
exit
