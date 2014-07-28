#!/bin/bash
REQUIRED_LANG="en"

function help {
	echo "How to use     : $0 <langCode1> <langCode2> [<further arguments>]"
	echo "Practice ex 1: : $0 de en"
	echo "Practice ex 2: : $0 de en -nsp # No printing of stop words"

}

# Check for languages unset or they being the same.
if [ -z $1 ] || [ -z $2 ] || [ $1 = $2 ]
then
	help
# Require one language to be fixed.
# XXX: Later it'll be possible to only specify one language for
# semantic analysis in one language only.
elif [ $1 != $REQUIRED_LANG ] && [ $2 != $REQUIRED_LANG ]
then
	echo "Remark: One of the two languages needs to be \"en\"."
	help
else
	./besttranslations.py -s $1 -t $2 -i ./data/eval-${1}.txt ${@:3}
fi
