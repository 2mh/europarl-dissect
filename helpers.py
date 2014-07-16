#!/usr/bin/python2
# -*- coding: utf-8 -*-
import re

def getTag(tag, lang):
    if lang == "en":
        if re.match(r"NN.*", tag):
            return "N"
        elif re.match(r"NP.*", tag):
            return "P"
        elif re.match(r"V.*", tag):
            return "V"
        elif re.match(r"JJ.*", tag):
            return "A"
        else:
            return "0"
            
    elif lang == "de":
        if tag == "NN":
            return "N"
        elif tag == "NE":
            return "P"
        elif re.match(r"V.*", tag):
            return "V"
        elif re.match(r"ADJ.", tag):
            return "A"
        else:
            return "0"
        
    else:
        return "0"
    
# space dimension format
def dimensionformat(word, tag, lemma, lang, use_lemmatization):
    if use_lemmatization:
        return lemma.lower() + "_" + tag + "_" + lang
    else:
        return word.lower() + "_" + lang

# must be in relevant part of speech group (not yet completed)
def valid_pos(tag):
    if tag in ["N", "P", "V", "A"]:
        return True
    else:
        return False