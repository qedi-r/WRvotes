#!/bin/bash

# Use jq to remove third altitude attribute

usage () { 
  echo $0 [geojson-file]
  echo ""
  echo Compress geojson-file by stripping some attributes. Make a
  echo backup of the original file with the date.
}

die () { 
  usage
  exit 1
}

srcfile=$1

JQ=`which jq`
echo $JQ is here

if [[ -z "$JQ" ]]
then
  echo Oh no! jq not found! Please install it to use this script.
  die
fi

if [[ ! -f "$srcfile" ]] 
then
  echo Oh no! Cannot find file $srcfile.
  die
fi

filepath=`dirname $srcfile`
filebase=`basename --suffix=.geojson  $srcfile`
datenow=`date --iso-8601=seconds`

echo path is $filepath and base is $filebase and date is $datenow


destfile=${filepath}/${filebase}-${datenow}.geojson
mv $srcfile $destfile
jq '.features[].geometry.coordinates[] |= map(.[:2])' $destfile > $srcfile

echo All done!

