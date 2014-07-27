#!/usr/bin/python2
# -*- coding: utf-8 -*-

'''
TODO:   
- Add --treetagger-path option.
- Transfer code to helpers.py or parameters.py.
'''
import re, sys, subprocess, argparse
import numpy as np
from collections import defaultdict

from lib.dissect.composes.utils import io_utils
from lib.dissect.composes.similarity.cos import CosSimilarity
from lib.dissect.composes.semantic_space.space import Space
from lib.dissect.composes.matrix.dense_matrix import DenseMatrix

import helpers
from parameters import DIFFERENT_POS_PUNISHMENT, \
                       NUMBER_OF_NEIGHBOURS, NUMBER_OF_TRANSLATIONS, \
                       OVERALL_SIMILARITY_WEIGHT, \
                       SENTENCE_SIMILARITY_WEIGHT, TREETAGGER_PATH, \
                       DATA_DIR_OUT

# For use: $ python besttranslations.py --help
# Example (with lemmatized matrix dimensions): 
# $ python besttranslations.py -l -s "en" -t "de" \
#   -i "./data/europarl_2014_en.txt"
# Example (with surface form dimensions):      
# $ python besttranslations.py -s "en" -t "de" \
#   -i "./data/europarl_2014_en.txt"

# Parameters to be set once starting the program - either per 
# default or per argparse:
source_lang = "en" # default
target_lang = "de" # default
input_is_tokenized = False # default
use_lemmatization = False # default
space_cols_file = ""
loaded_space_file_s = ""
loaded_space_file_t = ""
input_file = sys.stdin # default
output_file = sys.stdout # default
tag_cutoff = 0 # default: return in format of space_cols_file
no_stopword_print = False # default
number_of_neighbours = NUMBER_OF_NEIGHBOURS
number_of_translations = NUMBER_OF_TRANSLATIONS
different_pos_punishment = DIFFERENT_POS_PUNISHMENT

# gives ordered list. the nearest elements come first.
# return format: list of best translations as [space dimension, score, 
# sentence dependent similarity, translation dependent similarity]
def get_best_translations(word, tag, lemma, query_space, loaded_space):
    wformat = helpers.dimensionformat(word, tag, lemma, source_lang, 
                                      use_lemmatization)
    try:
        nearest = loaded_space[source_lang].get_neighbours(wformat, 
                                    number_of_neighbours, 
                                    CosSimilarity(), 
                                    space2 = loaded_space[target_lang])
    except:
        nearest = query_space.get_neighbours(wformat, 
                              number_of_neighbours, 
                              CosSimilarity(), 
                              space2 = loaded_space[target_lang])
    r = []
    
    # n: space dimension. 
    # s: translation similarty (how possible is the translation)
    for n, s in nearest: 
        # sentence similarity 
        # (how well does the word fit to the sentece):
        z = loaded_space[target_lang].get_sim(n, wformat, 
                                              CosSimilarity(), 
                                              space2 = query_space)
        # score to order the best translations. 
        # includes translation probability and how a word fits 
        # into a sentence
        score = (SENTENCE_SIMILARITY_WEIGHT * z \
                 + OVERALL_SIMILARITY_WEIGHT * s) \
                 / (SENTENCE_SIMILARITY_WEIGHT \
                 + OVERALL_SIMILARITY_WEIGHT)
        #if n[-3:] != "_" + target_lang:
        #    score = 0.0 # Answers in the same language 
        # will be punished. TODO: delete when new matrices are present
        if n[-5:-4] != tag and use_lemmatization:
            score = score * different_pos_punishment
        r.append((n, score, z, s))

    best = sorted(r, key=lambda m: m[1], reverse=True)
    return best

# Set the output for each input word
def format_best_translations(word, tag, lemma, best_translations):
    if helpers.valid_pos(tag):
        last_idx = number_of_translations - 1
        r = word.ljust(23) + " & "
        r_orig = r
        # Return a number of candiates
        for i in range(number_of_translations):
            r += best_translations[i][0][:len(best_translations[i][0])
                                         -tag_cutoff]
            r += " (" + "{0:1.2f}".format(best_translations[i][1]) + ")"
            if i < last_idx:
                r += " & "
            elif i == last_idx:
                r += " \\\\"
        return r.rstrip() + "\n"
    elif no_stopword_print:
        return ""
    else:
        return word + " & & & \\\\" + "\n"

def main():
    global input_is_tokenized, use_lemmatization, space_cols_file, \
           loaded_space_file_s, loaded_space_file_t, source_lang, \
           target_lang, input_file, output_file, tag_cutoff, \
           no_stopword_print, number_of_translations, \
           number_of_neighbours, different_pos_punishment
    
    parser = argparse.ArgumentParser(description="Word translations" + \
                                     " that fit best to the sentence")
    parser.add_argument("-k", "--tokenized", 
           help="use pretokenized input", action="store_true")
    parser.add_argument("-l", "--lemmatized", 
           help="use lemmatization", action="store_true")
    parser.add_argument("-p", "--returntag", 
           help="return language tag", action="store_true")
    parser.add_argument("-d", "--dimensions", type=str,
           help="column file for the input matrix")
    parser.add_argument("-m", "--sourcematrix", type=str,
           help="pickled input matrix for source language")
    parser.add_argument("-y", "--targetmatrix", type=str,
           help="pickled input matrix for target language")
    parser.add_argument("-s", "--sourcelang", type=str, 
           help="input language")
    parser.add_argument("-t", "--targetlang", type=str,
           help="output language")
    parser.add_argument("-i", "--infile", type=str, 
           help="input file")
    parser.add_argument("-o", "--outfile", type=str, 
           help="output file")
    parser.add_argument("-nsp", "--no-stopword-print", 
           action="store_true", 
           help="Omit to print words without candidates -- usually " + \
                 "stop words.")
    parser.add_argument("-nt", "--number-of-translations", type=float,
           help="The number of candidates to show for each input word.")
    parser.add_argument("-nn", "--number-of-neighbours", type=int,
           help="The number of neighbours for each input word to " + \
                "consider in the similarity space constructed.")
    parser.add_argument("-dpp", "--different-pos-punishment", 
           type=float, help="The score's fraction to punish a " + \
                             "candidate word which is there, but " + \
                             "has not the same POS as its input peer.")
    parser.add_argument
    args = parser.parse_args()
    
    if args.sourcelang:
        source_lang = args.sourcelang
    if args.targetlang:
        target_lang = args.targetlang
    if args.tokenized:
        input_is_tokenized = True
    if args.lemmatized:
        use_lemmatization = True
    if args.dimensions:
        space_cols_file = args.dimensions
    else:
        space_cols_file = DATA_DIR_OUT \
                        + '_'.join(sorted([source_lang,target_lang])) \
                        + '-words.col'
    if args.sourcematrix:
        loaded_space_file_s = args.sourcematrix
    else:
        loaded_space_file_s = DATA_DIR_OUT + source_lang \
                            + '_' + source_lang + '-' + target_lang \
                            + '.pkl'
    if args.targetmatrix:
        loaded_space_file_t = args.targetmatrix
    else:
        loaded_space_file_t = DATA_DIR_OUT + target_lang \
                            + '_' + target_lang + '-' + source_lang \
                            + '.pkl'
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
    if args.no_stopword_print:
        no_stopword_print = args.no_stopword_print

    # vector dimension/columns for input matrix and matrix per sentence
    space_cols_fileobject = open(space_cols_file, "r")
    # space_cols = space_cols_fileobject.readlines()
    space_cols = space_cols_fileobject.read().split("\n")[:-1] 
    space_cols_fileobject.close()

    # load the space
    loaded_space = {}
    loaded_space[source_lang] = io_utils.load(loaded_space_file_s)
    # only load it once for similary queries in the same language
    if not loaded_space.get(target_lang):
        loaded_space[target_lang] = io_utils.load(loaded_space_file_t)

    # work on input file
    while True:
        line = input_file.readline()
        words = [] # words in sentence
        lemmas = [] # lemmas in sentence
        pos = [] # part-of-speech tags per word in sentence
        formatted = []
        # matrix for sentence
        freq = defaultdict(lambda: defaultdict(int))

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
                formatted.append(helpers.dimensionformat(w, p, l, 
                                 source_lang, use_lemmatization))
                line = input_file.readline()
                if not line:
                    break

        # Use tree-tagger as lemmatizer and/or tokenizer
        else:
            treetagger = subprocess.Popen(
                [TREETAGGER_PATH + "tree-tagger-"
                 + helpers.LONG_LANGTAG[source_lang] + "-utf8"],
                stdin = subprocess.PIPE, stdout = subprocess.PIPE, 
                stderr = subprocess.PIPE)
            treetaggerout, stderr = treetagger.communicate(line)
            treeword = treetaggerout.rstrip().split("\n")
            for t in treeword:
                w = t.split("\t")[0]
                p = helpers.getTag(t.split("\t")[1], source_lang)
                l = t.split("\t")[2]
                words.append(w)
                lemmas.append(l)
                pos.append(p)
                formatted.append(helpers.dimensionformat(w, p, l, 
                                 source_lang, use_lemmatization))

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
            best_translations = get_best_translations(words[i], pos[i], 
                                lemmas[i], query_space, loaded_space)
            output_file.write(format_best_translations(words[i], pos[i], 
                              lemmas[i], best_translations))

        if input_is_tokenized:
            output_file.write(line.split("\t")[0] + "\n")

            
    if args.infile:
        input_file.close()
    if args.outfile:
        output_file.close()
            
if __name__ == '__main__':
    main()
