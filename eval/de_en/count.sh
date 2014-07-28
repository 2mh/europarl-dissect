#!/bin/bash
for i in *
do 
	echo "Filename:" $i
	no_lines=$(cat $i | wc -l)
	no_correct=$(cat $i | grep '%Y' | wc -l)
	echo "Number of lines       : " $no_lines
	echo "Number of correct ones: " $no_correct
	echo -n "Ratio of correct ones : "
	echo $no_correct $no_lines | awk '{ print $1/$2*100}'
done
