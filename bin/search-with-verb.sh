#!/usr/bin/env bash

# search-with-verb.sh - a front-end to search-with-verb.py

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May 21, 2025 - fun!


# configure
SEARCHWITHVERB='../bin/search-with-verb.py'

# get input
if [[ -z $1 || -z $2 ]]; then
	echo "Usage: $0 <carrel> <lemma>" >&2
	exit
fi
CARREL=$1
LEMMA=$2

cd "$(dirname "$0")"

# submit the work, format the output, and done
$SEARCHWITHVERB $CARREL $LEMMA | sed "s/$/\n/" | fold -s | less
exit
