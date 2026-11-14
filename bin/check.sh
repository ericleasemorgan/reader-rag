#!/usr/bin/env bash

# check.sh - make sure all vectorized databases work

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June 29, 2025 - first cut


# configure
SEARCH='../bin/search.py'
QUERY='love'
DEPTH='1'

# make sane
cd "$(dirname "$0")"
tabs 18

# initialize
LIBRARY=$( rdr get )
CARRELS=$( rdr catalog )

# process each carrel
for CARREL in ${CARRELS[@]}; do

	printf "$CARREL\t"
	RESULT=$( $SEARCH $CARREL $QUERY $DEPTH )
	if [[ ${#RESULT} > 1 ]]; then
		printf 'WORKS' >&2; 
	else
		printf 'BROKEN' >&2; 
	fi
	
	echo
	
# fini
done
exit