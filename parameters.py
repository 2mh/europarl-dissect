# -*- coding: utf-8 -*-
from os import sep

### Parameters to change before running.

# This variable has to be changed accordingly to a path where the
# TreeTagger shell scripts reside. Also an absolute path can be set
# here.
TREETAGGER_BASE_PATH = "treetagger/"


### default parameters used in create_input_data.py 

# Both languages involved / default languages used
LANG_1 = 'de'
LANG_2 = 'en'

# Limit number of sentences to process (for testing purposes).
# For no limit, set None
SENTENCES_LIMIT = 10000

# Filter out sentences which are longer than this number, in one or
# the other language -- wherever first.
MAX_SENTENCE_LEN = 10000 

# Minimal number of occurrences wanted.
# For no threshold, set anything below 2
MIN_PAIR_OCC = 1

# Maximum length of a word.
MAX_WORD_LEN = 10000


### Default parameters used for besttranslations.py

DIFFERENT_POS_PUNISHMENT = 0.3
NUMBER_OF_NEIGHBOURS = 100
NUMBER_OF_TRANSLATIONS = 3
OVERALL_SIMILARITY_WEIGHT = 1
SENTENCE_SIMILARITY_WEIGHT = 3


### default parameters used in both program parts

# Location of data (to read from, to write to)
DATA_DIR = ''.join(['data', sep])
DATA_DIR_IN  = ''.join([DATA_DIR, 'in', sep])
DATA_DIR_OUT = ''.join([DATA_DIR, 'out', sep])

# Default encoding (for places where specification is necessary)
ENC = "utf8"
NO_POS_SYM = "0"
