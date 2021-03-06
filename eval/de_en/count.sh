#!/bin/bash

function print_line
{

	echo "--------------------------------------------------------"
}

for i in $(ls *k-*-*-*.txt | sort -g)
do 
	print_line
	echo "Filename:" $i
	no_lines=$(cat $i | wc -l)
	no_correct=$(cat $i | grep '%Y' | wc -l)
	echo "Number of lines            : " $no_lines
	echo "Number of correct ones     : " $no_correct
	echo -n "Percentage of correct ones : "
	echo $no_correct $no_lines | awk '{ print $1/$2*100 " %"}' 
done

print_line
