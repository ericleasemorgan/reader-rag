#!/usr/bin/env bash

# tell-a-story.sh - a front-end to tell-a-story.py

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# May 21, 2025 - more just for fun; a simple demonstration


# configure
TELLASTORY='../bin/tell-a-story.py'

# get input
if [[ -z $1 ]]; then
	echo "Usage: $0 <carrel>" >&2
	exit
fi
CARREL=$1

cd "$(dirname "$0")"

# do the work
clear
echo
echo
echo "Once Upon A Time "
echo 
echo -e "$($TELLASTORY $CARREL)" | fold -s
echo
echo -e "The End"
echo

# done
exit

