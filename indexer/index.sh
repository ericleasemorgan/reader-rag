#!/usr/bin/env bash

# index.sh - make carrel searchable as well as search results verifyable; one script to rule many

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June     12, 2026 - first cut
# November 14, 2026 - added full text index; vectorize.py broke on under Golden Gate
# November 15, 2026 - didn't really break


# get input
if [[ -z $1 ]]; then
	echo "Usage: $0 <carrel>" >&2
	exit
fi
CARREL=$1

# make sane
cd "$(dirname "$0")"

# create rudimentary XML filess
echo -e "\nStep #1 of 6: Transforming plain text to XML" >&2
./txt2xml.sh $CARREL

# markup the sentences in them
echo -e "\nStep #2 of 6: Parsing XML into sentences" >&2
./morphadorn.sh $CARREL

# save the sentences to sets of CSV files
echo -e "\nStep #3 of 6: Extracting sentences to CSV files" >&2
./sentences2csv.py $CARREL

# vectororize (index) them
echo -e "\nStep #4 of 6: Semantically indexing sentences" >&2
./vectorize.py $CARREL

# transform the XML into HTML
echo -e "\nStep #5 of 6: Transforming XML into HTML" >&2
./xml2htm.sh $CARREL

# create a full text (not semantic) index
echo -e "\nStep #6 of 6: Full text indexing sentences" >&2
./fulltext-indexer.py $CARREL

# done
echo -e "\nDone" >&2
exit

