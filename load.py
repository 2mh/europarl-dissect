#!/usr/bin/python2
# -*- coding: utf-8 -*-

#from codecs import open
from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
from composes.semantic_space.space import Space
from composes.matrix.dense_matrix import DenseMatrix
from collections import defaultdict
import numpy as np
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords as stw
import re, sys

# use this program like
# python load.py inputfile inputlanguage outputlanguage
# inputfile: word per line

space_cols_file = "./data/out/europarl.row"
loaded_space_file = "./data/out/europarl.pkl"
source_lang = "de" # default
target_lang = "en" # default
langtag = {"nl":"dutch","fi":"finnish","de":"german","it":"italian","pt":"portuguese","es":"spanish","tr":"turkish","da":"danish","en":"english","fr":"french","hu":"hungarian","no":"norwegian","ru":"russian","sv":"swedish"}
stopwords = {}
input_is_tokenized = False
ENC = "utf-8"

# space lemma format
def lemmaformat(l):
    if input_is_tokenized:
        return l[0].lower() + "_" + l[1]
    else:
        return l[0].lower() + "_" + l[1]
        #return l[2] + "_" + l[1] + "_" + l[3]

# space dimension format
def dimensionformat(l):
    if input_is_tokenized:
        return l[0].lower() + "_" + l[1]
    else:
        return l[0].lower() + "_" + l[1]
        #return l[2] + "_" + l[1] + "_" + l[3]

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
def get_best_translations(w, query_space, europarl_space, number_of_neighbours):
    wformat = lemmaformat(w)
    try:
        nearest = europarl_space.get_neighbours(wformat, 10, CosSimilarity())
    except:
        nearest = query_space.get_neighbours(wformat, 10, CosSimilarity(), space2 = europarl_space)
    r = []
    for n, s in nearest:
        similarity = europarl_space.get_sim(n, wformat, CosSimilarity(), space2 = query_space)
        if n[-3:] != "_" + target_lang:
            similarity = 0.0
        elif n == wformat:
            similarity = 0.0
        r.append((n, similarity))
    best = sorted(r, key=lambda m: m[1], reverse=True)
    return best

def format_best_translations(w, best_translations, number_of_translations):
    if w[0].lower() not in stopwords[source_lang] and not re.match(r'(\W|\d)', w[0]):
        r = w[0] + "\t\t"
        for i in range(number_of_translations):
            r += best_translations[i][0][:-3]
            r += " "
            r += str(best_translations[i][1])
            r += "\t"
        return r.rstrip()
    else:
        return w[0]

# arguments: 1. inputfile - 2. source language
if len(sys.argv) > 3:
    sentences = open(sys.argv[1], "r")#, ENC)
    source_lang = sys.argv[2].lower()
    target_lang = sys.argv[3].lower()
else:
    sentences = sys.stdin

stopwords[source_lang] = set(stw.words(langtag[source_lang]))
stopwords[target_lang] = set(stw.words(langtag[target_lang]))

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
    if input_is_tokenized:
        while not re.match(r'[.:?!]', line):
            cleaned = line.rstrip()
            #ipos = line.split("\t")[1]
            ipos = "NN"
            if valid_pos(source_lang, ipos):
                words.append(tuple(cleaned.split("\t") + [source_lang]))
                pos.append(ipos)
            line = sentences.readline()
            if not line:
                break
    else:
        tokenized = TreebankWordTokenizer().tokenize(line)
        for t in tokenized:
            pos.append("NN")
            words.append([t, source_lang])

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

    # for every word print neighbours with similarity
    for w in words:
        best_translations = get_best_translations(w, query_space, europarl_space, 20)
        print format_best_translations(w, best_translations, 3)

    if input_is_tokenized:
        print line.rstrip()
