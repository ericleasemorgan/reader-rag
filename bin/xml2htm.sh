#!/usr/bin/env bash

# xml2htm.sh - transform TEI files into HTML files

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June 12, 2026 - rooted in the TEI Toolbox of November 2018
# [Date]        - parallelized execution using xargs


# configure
PATTERN='*.xml'
XML='xml'
EXTENSION='htm'
HTM='htm'
XML2HTML='./etc/xml2html.xsl'
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
rm -rf "$LIBRARY/$CARREL/$HTM"
mkdir "$LIBRARY/$CARREL/$HTM"

# get and process each xml file in parallel using xargs
find "$LIBRARY/$CARREL/$XML" -name "$PATTERN" -print0 | \
xargs -0 -P "$MAX_JOBS" -I {} bash -c '
    FILE="$1"
    OUTDIR="$2"
    EXT="$3"
    XSLT="$4"
    
    # debug
    echo "$FILE" >&2
            
    # get key and output
    BASENAME=$(basename "$FILE")
    BASENAME="${BASENAME%.*}"
    OUTPUT="$OUTDIR/$BASENAME.$EXT"
    
    # do the work
    xsltproc "$XSLT" "$FILE" > "$OUTPUT"
' _ {} "$LIBRARY/$CARREL/$HTM" "$EXTENSION" "$XML2HTML"

# done
exit
