#!/bin/bash
if [ -z $1 ] || [ -z $2 ] || [ $1 = $2 ];
then
	echo "How to use : $0 <langCode1> <langCode2>"
	echo "Practically: $0 de en"
else 
	./besttranslations.py -s $1 -t $2 -i ./data/eval-${1}.txt
fi
