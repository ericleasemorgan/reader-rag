#!/usr/bin/env bash

# search-with-lexicon.sh - yet another another front-end to search.py

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May 21, 2025 - more and more


# configure
SEARCH='../bin/search.py'
ETC='etc'
LEXICON='lexicon.txt'

# get input
if [[ -z $1|| -z $2 ]]; then
	echo "Usage: $0 <carrel> <depth>" >&2
	exit
fi
CARREL=$1
DEPTH=$2

cd "$(dirname "$0")"

# use the Reader to get SIZE number of keywords and build a query
LEXICON="$(rdr get)/$CARREL/$ETC/$LEXICON"
QUERY=$(cat $LEXICON | tr '\n' ' ')

# submit the work, format the output, and done
#$SEARCH $CARREL "$QUERY" $DEPTH | sed "s/$/\n/" | fold -s | less -i --pattern=$PATTERN
echo
$SEARCH $CARREL "$QUERY" $DEPTH | sed "s/$/ /" | fmt
echo
exit
