#!/bin/bash
DATA_DIR="data/in/"
TMP_PASTED_FILE="tmp_pasted"
TMP_SHUFFLED_FILE="tmp_shuffled"
if [ -z $1 ] || [ -z $2 ];
then
	echo "How to use: $0 <europarl_file_lang_1> <europarl_file_lang_2>"
else 
	file1=$(basename $1)
	file2=$(basename $2)
	echo "Get into directory ${DATA_DIR}."
	cd $DATA_DIR && \
	echo "Paste files $file1 and $file2 together." && \
	paste $file1 $file2 > $TMP_PASTED_FILE && \
	echo "Randomize merged file joint together by line." && \
	shuf $TMP_PASTED_FILE > $TMP_SHUFFLED_FILE && \
	echo "Disjoin file again into two separate files with _rand suffix." && \
	cat $TMP_SHUFFLED_FILE | cut -f1 > ${file1}_rand && \
	cat $TMP_SHUFFLED_FILE | cut -f2 > ${file2}_rand && \
	echo "Delete temporary files created." && \
	rm -f $TMP_PASTED_FILE $TMP_SHUFFLED_FILE
fi
