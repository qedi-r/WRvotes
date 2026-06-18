#!/bin/bash

# Send mail ONLY if standard input is not empty
EMAIL="$1"
shift
SUBJECT="$@"

body=$(cat /dev/stdin)

if [[ -n ${body} ]]
then

    printf "Subject: %b\n\n%b\n" "${SUBJECT}" "${body}" | \
      msmtp --account=newsletter.mailer.kwlug.org ${EMAIL}

fi 
