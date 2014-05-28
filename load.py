#!/usr/bin/python
# -*- coding: utf-8 -*-

from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
from composes.semantic_space.space import Space
from composes.matrix.dense_matrix import DenseMatrix
from collections import defaultdict
import numpy as np
import sys

space_cols_file = "./europarl_space.cols"
loaded_space_file = "./europarl_space.pkl"
source_lang = "de"

# space lemma format
def lemmaformat(l):
    return l[0] + "_" + l[1] + "_" + l[2]

# space dimension format
def dimensionformat(l):
    return l[0] + "_" + l[1] + "_" + l[2]

# surrounding words can only be part of the vector, if they exist in the matrix
def valid_dimension(lemma, tag, source):
    if dimensionformat(lemma, tag, source) in set(space_cols):
        return True
    else:
        return False

# must be in relevant part of speech group
def valid_pos(source, tag):
    if source = "de":
        if tag in set(["NN", "ADJA", "ADJD", "VVFIN"]):
            return True
        else:
            return False
    elif source = "en":
        if tag in set(["NN", "JJ", "VB"]):
            return True
        else:
            return False
    else:
        return False

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

    # collect words in sentence until sentence end
    while not line.startswith("."):
        ipos = line.split("\t")[1]
        if valid_pos(source_lang, ipos):
            words.append([line.split("\t")[2], line.split("\t")[1], source_lang])
            pos.append(ipos)
        line = sentences.readline()

    # fill matrix for sentence
    for i in range(words):
        for j in range(words):
            if valid_dimension(dimensionformat(words[j])):
                freq[lemmaformat(i)][dimensionformat(j)] += 1

    uniqwords = list(set(words)) # rows for sentence matrix

    # dissect compatible matrix
    m = np.mat(np.zeros(shape=(len(uniqwords), len(space_cols), dtype=element_type))

    # convert sentence matrix to compatible matrix
    for i in range(uniqwords):
        for j in space_cols:
            m[lemmaformat(uniqwords[i]), j] = freq[lemmaformat(uniqwords[i])][space_cols[j]]

    # build dissect matrix
    query_space = Space(DenseMatrix(m), row, column)

    print query_space
    
    
    #for w in words:
        #wformat = lemmaformat(...)
        #query_space.get_neighbours(wformat, 3, CosSimilarity(), space2 = europarl_space)
        #list = ...
        #for c in list:
            #similarity
            #an string anfügen mit similarity
        #print whatever
        
        
        ###
    