#!/usr/bin/python2
# -*- coding: utf-8 -*-

### Parameters to change before running.

# This variable has to be changed accordingly to a path where the
# TreeTagger shell scripts reside. Also an absolute path can be set
# here.
TREETAGGER_PATH = "treetagger/cmd/"
TREETAGGER_BASE_PATH = "treetagger/"

DATA_DIR_OUT = './data/out/'


### default parameters used in create_input_data.py 

# Both languages involved / default languages used
LANG_1 = 'de'
LANG_2 = 'en'

# Limit number of sentences to process (for testing purposes).
# For no limit, set None
SENTENCES_LIMIT = 1000000

# Filter out sentences which are longer than this number, in one or
# the other language -- wherever first.
MAX_SENTENCE_LEN = 10000 

# Minimal number of occurrences wanted.
# For no threshold, set anything below 2
PAIR_OCC_THRESHOLD = 1


### Default parameters used for besttranslations.py

DIFFERENT_POS_PUNISHMENT = 0.3
NUMBER_OF_NEIGHBOURS = 100
NUMBER_OF_TRANSLATIONS = 3
OVERALL_SIMILARITY_WEIGHT = 1
SENTENCE_SIMILARITY_WEIGHT = 3
