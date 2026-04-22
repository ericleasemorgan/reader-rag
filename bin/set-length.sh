#!/usr/bin/env bash

# set-length.sh - cache a system prompt based on a persona and response length

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# April 16, 2026 - while in a laundramat in Plymouth (Indiana) 


# configure
PREFIX='You are '
CONJUNCTION=', and you respond in '
SUFFIX='.'
LENGTHS='../etc/lengths.txt'
SYSTEMPROMPT='../etc/system-prompt.txt'
CACHEDPERSONA='../etc/cached-persona.txt'
CACHEDLENGTH='../etc/cached-length.txt'

# make sane
cd "$(dirname "$0")"

# initialize
IFS=$'\n'
LENGTHS=( $( cat $LENGTHS ) )
PERSONA=$( cat $CACHEDPERSONA )
INDEX=0

# display a menu of choices
echo -e "\nThe following lengths have been predefined. Choose one:\n"
for LENGTH in "${LENGTHS[@]}"; do

	let "INDEX++"
	echo "  $INDEX. $LENGTH"
	
done

# prompt for, get, and normalize a choice
echo
read -p "Enter a choice: " SELECTION
let "SELECTION--"

# build the prompt, save, and cache
SYSTEM=$PREFIX$PERSONA$CONJUNCTION${LENGTHS[$SELECTION]}$SUFFIX
echo $SYSTEM > $SYSTEMPROMPT
echo ${LENGTHS[$SELECTION]} > $CACHEDLENGTH

# done
echo -e "\nDone. The system will now address summarization and elaboration processes as if it was $PERSONA, and it will respond in ${LENGTHS[$SELECTION]}.\n"
exit




