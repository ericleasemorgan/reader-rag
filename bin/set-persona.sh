#!/usr/bin/env bash

# persona.sh - cache a system prompt based on a persona

# Eric Lease Morgan <eric_morgan@infomotions.com>
# (c) Infomotions, LLC; distributed under a GNU Public License

# July 15, 2025 - first cut


# configure
PREFIX='You are '
CONJUNCTION=', and you respond in '
SUFFIX='.'
PERSONAS='../etc/personas.txt'
SYSTEMPROMPT='../etc/system-prompt.txt'
CACHEDLENGTH='../etc/cached-length.txt'
CACHEDPERSONA='../etc/cached-persona.txt'

# make sane
cd "$(dirname "$0")"

# initialize
IFS=$'\n'
PERSONAS=( $( cat $PERSONAS ) )
LENGTH=$( cat $CACHEDLENGTH )
INDEX=0

# display a menu of choices
echo -e "\nThe following personas have been predefined. Choose one:\n"
for PERSONA in "${PERSONAS[@]}"; do

	let "INDEX++"
	echo "  $INDEX. $PERSONA"
	
done

# prompt for, get, and normalize a choice
echo
read -p "Enter a choice: " SELECTION
let "SELECTION--"

# build the prompt, save, and cache
SYSTEM=$PREFIX${PERSONAS[$SELECTION]}$CONJUNCTION$LENGTH$SUFFIX
echo $SYSTEM > $SYSTEMPROMPT
echo ${PERSONAS[$SELECTION]} > $CACHEDPERSONA

# done
echo -e "\nDone. The system will now address summarization and elaboration processes as if it was ${PERSONAS[$SELECTION]}, and it will respond in $LENGTH.\n"
exit




