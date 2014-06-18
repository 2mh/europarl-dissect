#!/usr/bin/python2
# -*- coding: utf-8 -*-
import re

def getTag(tag, lang):
    if lang == "en":
        if tag in set(["NN", "NNS"]):
            return "N"
        elif tag in set(["NP", "NPS"]):
            return "P"
        elif re.match(r"V.*", tag):
            return "V"
        elif re.match(r"JJ.*", tag):
            return "J"
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
            return "J"
        else:
            return "0"
        
    else:
        return "0"