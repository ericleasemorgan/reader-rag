#!/usr/bin/env bash

# search-with-modals.sh - yet another another another front-end to search.py

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May 21, 2025 - more and more and more


# configure
MODALS='../modals'
ETC='etc'
LEXICON='lexicon.txt'

# get input
if [[ -z $1 ]]; then
	echo "Usage: $0 <carrel>" >&2
	exit
fi
CARREL=$1
SIZE=$2

cd "$(dirname "$0")"

# use the Reader to get SIZE number of keywords and build a query
LEXICON="$(rdr get)/$CARREL/$ETC/$LEXICON"
QUERY=$(cat $LEXICON | tr '\n' ' ')

# build a pattern
PATTERN="\b$(echo $QUERY | sed "s/ /\\\b|\\\b/g")\b"
echo "  Pattern: $PATTERN" >&2

# submit the work, format the output, and done
$MODALS $CARREL | sed "s/$/\n/" | fold -s | less -i --pattern=$PATTERN
exit
