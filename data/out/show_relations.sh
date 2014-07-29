#!/bin/bash
lang_1="de"
lang_2="en"

function echo_line {
	echo "--------------------------------------------------------"
}

for data_out_dir in $(echo *k-* | sed -e "s| |\n|g" | sort -g)
do
	echo_line
	echo "Data output folder   : $data_out_dir"
	echo "Size of folder       : $(du -hs $data_out_dir | cut -f1)"
	(
	cd $data_out_dir
	no_lang_1_words=$(cat ${lang_1}-words.row | wc -l)
	no_lang_2_words=$(cat ${lang_2}-words.row | wc -l)
	echo "Number of \"${lang_1}\" words : " $no_lang_1_words
	echo "Number of \"${lang_2}\" words : " $no_lang_2_words
	echo "Ratio \"${lang_1}\" to \"${lang_2}\" words   : " \
	$(echo $no_lang_1_words $no_lang_2_words | awk '{ print $1/$2 }')
	no_lang_1_1_comb=$(cat ${lang_1}_${lang_1}-${lang_2}.sm | grep -v _${lang_2} | wc -l)
	echo "Number of \"${lang_1}\"<->\"${lang_1}\" combinations:" $no_lang_1_1_comb
	no_lang_2_2_comb=$(cat ${lang_2}_${lang_2}-${lang_1}.sm | grep -v _${lang_1} | wc -l)
	echo "Number of \"${lang_2}\"<->\"${lang_2}\" combinations:" $no_lang_2_2_comb
	echo "Ratio of \"${lang_1}\"<->\"${lang_1}\" to \"${lang_2}\"<->\"${lang_2}\" :" \
	$(echo $no_lang_1_1_comb $no_lang_2_2_comb | awk '{ print $1/$2 }')
	)
done
echo_line
#wc -l $(ls *k-*/*.sm | sort -g)
