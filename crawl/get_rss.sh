#! /bin/bash

INPUT_FILE=$1
ROOT_DIR=$2

if [ ! -e $ROOT_DIR ]; then
  mkdir $ROOT_DIR
fi
  

while read line
do
  url=$(echo "$line" | cut -d' ' -f1)
  name=$(echo "$line" | cut -d' ' -f2)

  # create the city subdirectory if it doesn't exist
  if [ ! -e $ROOT_DIR/$name ]; then
    mkdir $ROOT_DIR/$name
  fi

  today=$(date "+%Y-%m-%d")
  curl "$url" > $ROOT_DIR/$name/$today.rss

done < $INPUT_FILE
