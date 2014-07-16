#!/usr/bin/python2
# -*- coding: utf-8 -*-

from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
from composes.semantic_space.space import Space
from composes.matrix.dense_matrix import DenseMatrix
from collections import defaultdict
import numpy as np
import re, sys, subprocess, argparse
import helpers

# For use: $ python besttranslations.py --help
# Example (with lemmatized matrix dimensions): $ python besttranslations.py -l -s "en" -t "de" -i "./data/europarl_2014_en.txt"
# Example (with surface form dimensions):      $ python besttranslations.py -s "en" -t "de" -i "./data/europarl_2014_en.txt"

# Static paramaters:
DIFFERENT_POS_PUNISHMENT = 0.3
NUMBER_OF_NEIGHBOURS = 20
NUMBER_OF_TRANSLATIONS = 3
OVERALL_SIMILARITY_WEIGHT = 1
SENTENCE_SIMILARITY_WEIGHT = 3
TREETAGGER_PATH = "/home/reto/bin/cmd/"

# Parameters to be set once starting the program:
source_lang = "de" # default
target_lang = "en" # default
input_is_tokenized = False # default
use_lemmatization = False # default
space_cols_file = "./en-de--10k-sent-lemmatized+pos/europarl.row" # default
loaded_space_file_s = "./de-en--10k-sent-lemmatized+pos/europarl.pkl" # default
loaded_space_file_t = "./en-de--10k-sent-lemmatized+pos/europarl.pkl" # default
input_file = sys.stdin # default
output_file = sys.stdout # default
tag_cutoff = 0 # default: return in format of space_cols_file

# Conversion between names for languages 
long_langtag =  {"nl":"dutch","fi":"finnish","de":"german","it":"italian","pt":"portuguese","es":"spanish","tr":"turkish","da":"danish","en":"english","fr":"french","hu":"hungarian","no":"norwegian","ru":"russian","sv":"swedish"}


# gives ordered list. the nearest elements come first.
# return format: list of best translations as [space dimension, score, sentence dependent similarity, translation dependent similarity]
def get_best_translations(word, tag, lemma, query_space, loaded_space):
    wformat = helpers.dimensionformat(word, tag, lemma, source_lang, use_lemmatization)
    try:
        nearest = loaded_space[source_lang].get_neighbours(wformat, NUMBER_OF_NEIGHBOURS, CosSimilarity(), space2 = loaded_space[target_lang])
    except:
        nearest = query_space.get_neighbours(wformat, NUMBER_OF_NEIGHBOURS, CosSimilarity(), space2 = loaded_space[target_lang])
    r = []
    for n, s in nearest: # n: space dimension. s: translation similarty (how possible is the translation)
        # sentence similarity (how well does the word fit to the sentece):
        z = loaded_space[target_lang].get_sim(n, wformat, CosSimilarity(), space2 = query_space)
        # score to order the best translations. includes translation probability and how a word fits into a sentence
        score = (SENTENCE_SIMILARITY_WEIGHT * z + OVERALL_SIMILARITY_WEIGHT * s) / (SENTENCE_SIMILARITY_WEIGHT + OVERALL_SIMILARITY_WEIGHT)
        if n[-3:] != "_" + target_lang:
            score = 0.0 # Answers in the same language will be punished. TODO: delete when the new matrices are present
        if n[-5:-4] != tag and use_lemmatization:
            score = score * DIFFERENT_POS_PUNISHMENT
        r.append((n, score, z, s))

    best = sorted(r, key=lambda m: m[1], reverse=True)
    return best

# Set the output for each input word
def format_best_translations(word, tag, lemma, best_translations):
    if helpers.valid_pos(tag) and not re.match(r'(\W|\d)', word):
        r = word + "\t\t"
        for i in range(NUMBER_OF_TRANSLATIONS):
            r += best_translations[i][0][:len(best_translations[i][0])-tag_cutoff]
            r += " "
            r += str(best_translations[i][1])
            r += "\t"
        return r.rstrip() + "\n"
    else:
        return word + "\n"

def main():
    global input_is_tokenized, use_lemmatization, space_cols_file, loaded_space_file_s, loaded_space_file_t, source_lang, target_lang, input_file, output_file, tag_cutoff
    
    parser = argparse.ArgumentParser(description="Word translations that fit best to the sentence")
    parser.add_argument("-k", "--tokenized", help="use pretokenized input", action="store_true")
    parser.add_argument("-l", "--lemmatized", help="use lemmatization", action="store_true")
    parser.add_argument("-p", "--returntag", help="return language tag", action="store_true")
    parser.add_argument("-d", "--dimensions", type=str, help="column file for the input matrix")
    parser.add_argument("-m", "--sourcematrix", type=str , help="pickled input matrix for source language")
    parser.add_argument("-y", "--targetmatrix", type=str , help="pickled input matrix for target language")
    parser.add_argument("-s", "--sourcelang", type=str, help="input language")
    parser.add_argument("-t", "--targetlang", type=str, help="output language")
    parser.add_argument("-i", "--infile", type=str, help="input file")
    parser.add_argument("-o", "--outfile", type=str, help="output file")
    args = parser.parse_args()
    
    if args.tokenized:
        input_is_tokenized = True
    if args.lemmatized:
        use_lemmatization = True
    if args.dimensions:
        space_cols_file = args.dimensions
    if args.sourcematrix:
        loaded_space_file_s = args.sourcematrix
    if args.targetmatrix:
        loaded_space_file_t = args.targetmatrix
    if args.sourcelang:
        source_lang = args.sourcelang
    if args.targetlang:
        target_lang = args.targetlang
    if args.infile:
        input_file = open(args.infile, "r")
    if args.outfile:
        output_file = open(args.outfile, "w")
    if args.returntag:
        tag_cutoff = 0
    else:
        if args.lemmatized:
            tag_cutoff = 5
        else:
            tag_cutoff = 3

    # vector dimension/columns for input matrix and matrix per sentence
    space_cols_fileobject = open(space_cols_file, "r")
    space_cols = space_cols_fileobject.read().split("\n")[:-1] #space_cols = space_cols_fileobject.readlines()
    space_cols_fileobject.close()

    # load the space
    loaded_space = {}
    loaded_space[source_lang] = io_utils.load(loaded_space_file_s)
    if not loaded_space.get(target_lang): # only load it once for similary queries in the same language
        loaded_space[target_lang] = io_utils.load(loaded_space_file_t)

    # work on input file
    while True:
        line = input_file.readline()
        words = [] # words in sentence
        lemmas = [] # lemmas in sentence
        pos = [] # part-of-speech tags per word in sentence
        formatted = [] # 
        freq = defaultdict(lambda: defaultdict(int)) # matrix for sentence

        # Stop when file is entirely read
        if not line:
            break

        # For pre-treetagged text
        if input_is_tokenized:
            while not re.match(r'[.:?!]', line):
                t = line.rstrip()
                w = t.split("\t")[0]
                p = helpers.getTag(t.split("\t")[1], source_lang)
                l = t.split("\t")[2]
                words.append(w)
                lemmas.append(l)
                pos.append(p)
                formatted.append(helpers.dimensionformat(w, p, l, source_lang, use_lemmatization))
                line = input_file.readline()
                if not line:
                    break

        # Use tree-tagger as lemmatizer and/or tokenizer
        else:
            treetagger = subprocess.Popen(
                [TREETAGGER_PATH + "tree-tagger-" + long_langtag[source_lang] + "-utf8"],
                stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            treetaggerout, stderr = treetagger.communicate(line)
            treeword = treetaggerout.rstrip().split("\n")
            for t in treeword:
                w = t.split("\t")[0]
                p = helpers.getTag(t.split("\t")[1], source_lang)
                l = t.split("\t")[2]
                words.append(w)
                lemmas.append(l)
                pos.append(p)
                formatted.append(helpers.dimensionformat(w, p, l, source_lang, use_lemmatization))

        # fill matrix for sentence
        for i in formatted:
            for j in formatted:
                freq[i][j] += 1

        # bild unique list of the words in this sentence for the rows
        uniqwords = set()
        for l in formatted:
            uniqwords.add(l)
        query_rows = list(uniqwords) # rows for sentence matrix

        # dissect compatible matrix
        m = np.mat(np.zeros(shape=(len(query_rows), len(space_cols))))

        # convert sentence matrix to compatible matrix
        for i in range(len(query_rows)):
            for j in range(len(space_cols)):
                m[i, j] = freq[query_rows[i]][space_cols[j]]

        # build dissect matrix
        query_space = Space(DenseMatrix(m), query_rows, space_cols)

        # for every word print neighbours with similarity
        for i in range(len(words)):
            best_translations = get_best_translations(words[i], pos[i], lemmas[i], query_space, loaded_space)
            output_file.write(format_best_translations(words[i], pos[i], lemmas[i], best_translations))

        if input_is_tokenized:
            output_file.write(line.split("\t")[0] + "\n")

            
    if args.infile:
        input_file.close()
    if args.outfile:
        output_file.close()
            
if __name__ == '__main__':
    main()
