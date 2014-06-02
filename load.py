#!/usr/bin/python2
# -*- coding: utf-8 -*-

from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
from composes.semantic_space.space import Space
from composes.matrix.dense_matrix import DenseMatrix
from collections import defaultdict
import numpy as np
import sys

# use this program like
# python load.py inputfile inputlanguage
# inputfile: word per line

space_cols_file = "./europarl.row"
loaded_space_file = "./data/out/europarl.pkl"
source_lang = "de" # default

# space lemma format
def lemmaformat(l):
    #return l[2] + "_" + l[1] + "_" + l[3]
    return l[0].lower() + "_" + l[1]

# space dimension format
def dimensionformat(l):
    #return l[2] + "_" + l[1] + "_" + l[3]
    return l[0].lower() + "_" + l[1]

# surrounding words can only be part of the vector, if they exist in the matrix
def valid_dimension(n):
    if n in set(space_cols):
        return True
    else:
        return False

# must be in relevant part of speech group (not yet completed)
def valid_pos(source, tag):
    if source == "de":
        if tag in set(["NN", "ADJA", "ADJD", "VVFIN"]):
            return True
        else:
            return False
    elif source == "en":
        if tag in set(["NN", "JJ", "VB"]):
            return True
        else:
            return False
    else:
        return False

# gives ordered list. the nearest elements come first. penalty on same language
def get_best_translations(wformat, query_space, europarl_space, number_of_neighbours):
    try:
        nearest = europarl_space.get_neighbours(wformat, 10, CosSimilarity())
    except:
        nearest = query_space.get_neighbours(wformat, 10, CosSimilarity(), space2 = europarl_space)
    r = []
    for n, s in nearest:
        similarity = europarl_space.get_sim(n, wformat, CosSimilarity(), space2 = query_space)
        if n[-3:] == "_" + source_lang:
            similarity = 0
        elif n == wformat:
            similarity = 0
        r.append((n, similarity))
    best = sorted(r, key=lambda m: m[1], reverse=True)
    return best

def format_best_translations(wformat, best_translations, number_of_translations):
    r = wformat + "\t\t"
    for i in range(number_of_translations):
        r += best_translations[i][0]
        r += " "
        r += str(best_translations[i][1])
        r += "\t"
    return r.rstrip()

# arguments: 1. inputfile - 2. source language
if len(sys.argv) > 2:
    sentences = open(sys.argv[1], "r")
    source_lang = sys.argv[2]
else:
    sentences = sys.stdin

# vector dimension/columns for input matrix and matrix per sentence
space_cols_fileobject = open(space_cols_file, "r")
space_cols = space_cols_fileobject.readlines()
space_cols_fileobject.close()

# load the space
europarl_space = io_utils.load(loaded_space_file)

# work on input file
while True:
    line = sentences.readline()
    words = [] # words in sentence
    pos = [] # part-of-speech tags per word in sentence
    freq = defaultdict(lambda: defaultdict(int)) # matrix for sentence

    # Stop when file is entirely read
    if not line:
        break

    # collect words in sentence until sentence end (now in mockup mode about pos)
    while not line.startswith("."):
        cleaned = line.rstrip()
        #ipos = line.split("\t")[1]
        ipos = "NN"
        if valid_pos(source_lang, ipos):
            words.append(tuple(cleaned.split("\t") + [source_lang]))
            pos.append(ipos)
        line = sentences.readline()
        if not line:
            break

    # fill matrix for sentence
    for i in words:
        for j in words:
            if valid_dimension(dimensionformat(j)):
                freq[lemmaformat(i)][dimensionformat(j)] += 1

    # bild unique list of the words in this sentence for the rows
    uniqwords = set()
    for w in words:
        uniqwords.add(lemmaformat(w))
    query_rows = list(uniqwords) # rows for sentence matrix

    # dissect compatible matrix
    m = np.mat(np.zeros(shape=(len(query_rows), len(space_cols))))

    # convert sentence matrix to compatible matrix
    for i in range(len(query_rows)):
        for j in range(len(space_cols)):
            m[i, j] = freq[query_rows[i]][space_cols[j]]

    # build dissect matrix
    query_space = Space(DenseMatrix(m), query_rows, space_cols)

    # for every word print neighbours (yet no fancy format and language selection)
    for w in words:
        wformat = lemmaformat(w)
        best_translations = get_best_translations(wformat, query_space, europarl_space, 10)
        print format_best_translations(wformat, best_translations, 3)
    print line.rstrip()
