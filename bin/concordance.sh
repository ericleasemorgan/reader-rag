#!/usr/bin/env bash


CACHE='../etc/cached-results.txt'

if [[ -z $1 || -z $2 ]]; then
	echo "Usage: $0 <carrel> <query>" >&2
	exit
fi
CARREL=$1
QUERY=$2

cd "$(dirname "$0")"

SENTENCES=$( rdr concordance $CARREL -q "$QUERY" -w 80 | sed "s/^.*$QUERY/$QUERY/" | sort | uniq )
echo -n "$SENTENCES" > $CACHE
echo -n "$SENTENCES" | less