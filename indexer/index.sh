#!/usr/bin/env bash

# index.sh - make carrel searchable as well as search results verifyable; one script to rule many

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# June     12, 2026 - first cut
# November 14, 2026 - added full text index; vectorize.py broke on under Golden Gate
# November 15, 2026 - didn't really break
# November 21, 2026 - adding simplified command-line input


# get input
if [[ -z $1 || -z $2 ]]; then
	echo "Usage: $0 <carrel> <initialize|fulltext|semantics>" >&2
	exit
fi
CARREL=$1
OPERATION=$2

# make sane
cd "$(dirname "$0")"

# intialize the database
if [[ $OPERATION == 'initialize' ]]; then

	# create rudimentary XML filess
	echo -e "\nStep #1 of 5: Transforming plain text to XML" >&2
	./txt2xml.sh $CARREL

	# markup the sentences in them
	echo -e "\nStep #2 of 5: Parsing XML into sentences" >&2
	./morphadorn.sh $CARREL

	# transform the XML into HTML
	echo -e "\nStep #3 of 5: Transforming XML into HTML" >&2
	./xml2htm.sh $CARREL

	 # save the sentences to sets of CSV files
	echo -e "\nStep #4 of 5: Extracting sentences and caching them to CSV files" >&2
	./sentences2csv.py $CARREL

	echo -e "\nInitialization complete.\n" >&2
	exit
	
fi

# intialize the database
if [[ $OPERATION == 'fulltext' ]]; then

	# vectororize (index) them
	echo -e "\nFull text indexing sentences" >&2
	./fulltext-indexer.py $CARREL

	# done
	exit
	
fi

# intialize the database
if [[ $OPERATION == 'semantics' ]]; then

	# vectororize (index) them
	echo -e "\nStep #4 of 6: Semantically indexing sentences" >&2
	./vectorize.py $CARREL

	# done
	exit
	
fi


