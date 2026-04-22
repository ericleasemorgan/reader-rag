#!/usr/bin/env bash

# search-with-unigrams.sh - yet a sixth front-end to search.py

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May 13, 2025 - first cut; in a FOC ("Fit Of Creativity")
# May 14, 2025 - added unigrams


# configure
SEARCH='../bin/search.py'

# get input
if [[ -z $1 || -z $2 || -z $3 ]]; then
	echo "Usage: $0 <carrel> <breadth> <depth>" >&2
	exit
fi
CARREL=$1
SIZE=$2
DEPTH=$3

cd "$(dirname "$0")"

# use the Reader to get SIZE number of keywords and build a query
QUERY=$(rdr ngrams $CARREL -c | head -n $SIZE | cut -f1 | tr '\n' ' ')

# submit the work, format the output, and done
echo
$SEARCH $CARREL "$QUERY" $DEPTH | sed "s/$/ /" | fmt
echo
exit
