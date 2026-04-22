#!/usr/bin/env bash

# check.sh - make sure all vectorized databases work

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June 29, 2025 - first cut


# configure
SEARCH='../bin/search.py'
QUERY='love'
DEPTH='1'

cd "$(dirname "$0")"

# initialize
LIBRARY=$( rdr get )
CARRELS=$( rdr catalog )

# process each carrel
for CARREL in ${CARRELS[@]}; do

	echo $CARREL
	echo "$SEARCH $CARREL $QUERY $DEPTH"
	$SEARCH $CARREL $QUERY $DEPTH
	echo
	
# fini
done
exit