#!/bin/bash
# A script to generate a list of abstract PMID's for use in the to-do README for each annotator
# Pass the directory to be searched as the first command line argument 

SEARCHDIR=$1

for entry in "$SEARCHDIR"/*
do 
	base=`basename $entry`
	echo $base
done

