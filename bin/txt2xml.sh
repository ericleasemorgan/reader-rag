#!/usr/bin/env bash

# txt2xml.sh - a front-end to txt2xml.py

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June 12, 2026 - rooted in the TEI Toolbox of November 2018
# [Date]        - parallelized execution using xargs


# configure
TXT='txt'
PATTERN='*.txt'
TXT2XML='./bin/txt2xml.py'
XML='xml'
EXTENSION='xml'
MAX_JOBS=4  # number of parallel jobs to run concurrently

# get input
if [[ -z $1 ]]; then
	echo "Usage: $0 <carrel>" >&2
	exit
fi
CARREL=$1

# initialize
LIBRARY=$(rdr get)

# make sane
rm -rf "$LIBRARY/$CARREL/$XML"
mkdir "$LIBRARY/$CARREL/$XML"

# get and process each txt file in parallel using xargs
find "$LIBRARY/$CARREL/$TXT" -name "$PATTERN" -print0 | \
xargs -0 -P "$MAX_JOBS" -I {} bash -c '
    FILE="$1"
    OUTDIR="$2"
    EXT="$3"
    SCRIPT="$4"
    
    # debug
    echo "$FILE" >&2
    
    # get key and output
    BASENAME=$(basename "$FILE")
    BASENAME="${BASENAME%.*}"
    OUTPUT="$OUTDIR/$BASENAME.$EXT"
    
    # do the work
    "$SCRIPT" "$FILE" "$BASENAME" > "$OUTPUT"
' _ {} "$LIBRARY/$CARREL/$XML" "$EXTENSION" "$TXT2XML"

# done
exit
