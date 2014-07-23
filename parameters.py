#!/usr/bin/python2
# -*- coding: utf-8 -*-
import re

TREETAGGER_PATH = "/home/hernani/uzh/master/statsem/europarl-dissect/treetagger/cmd/"
DATA_DIR_OUT = './data/out/'

DIFFERENT_POS_PUNISHMENT = 0.3
NUMBER_OF_NEIGHBOURS = 100
NUMBER_OF_TRANSLATIONS = 3
OVERALL_SIMILARITY_WEIGHT = 1
SENTENCE_SIMILARITY_WEIGHT = 3
