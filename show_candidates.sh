#!/bin/bash
if [ -z $1 ] || [ -z $2 ] || [ $1 = $2 ];
then
	echo "How to use     : $0 <langCode1> <langCode2> [<further arguments>]"
	echo "Practice ex 1: : $0 de en"
	echo "Practice ex 2: : $0 de en -nsp # No printing of stop words"
else 
	./besttranslations.py -s $1 -t $2 -i ./data/eval-${1}.txt ${@:3}
fi
