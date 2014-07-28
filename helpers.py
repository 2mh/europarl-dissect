# -*- coding: utf-8 -*-

from os import sep
import re

from parameters import DATA_DIR_IN, NO_POS_SYM

# Conversion between names for languages 
LONG_LANGTAG =  {"nl":"dutch",
                 "fi":"finnish",
                 "de":"german",
                 "it":"italian",
                 "pt":"portuguese",
                 "es":"spanish",
                 "tr":"turkish",
                 "da":"danish",
                 "en":"english",
                 "fr":"french",
                 "hu":"hungarian",
                 "no":"norwegian",
                 "ru":"russian",
                 "sv":"swedish"}

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
            return NO_POS_SYM
            
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
            return NO_POS_SYM
        
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
        
class Filenames():
    def __init__(self):
        self.lang_1 = ""
        self.lang_2 = "" # Might not be used in single language runs.
        
class InputFilenames(Filenames):
    """Class to handle input files from europarl (currently: v7)."""
    
    def __init__(self):
        pass

class OutputFilenames(Filenames):
    """Class to handle output files which are used as input material
       for the DISSECT library."""
    
    def __init__(self):
        pass

# XXX: Will supposedly substituted by InputFilenames.
class Suffixes:
    """ This class provides suffixes for being more flexible with
        language pairs supported.
    """
    
    def __init__(self, lang_1, lang_2):
        """
        Initalized class with both languages used. If both languages
        provided are the same, just the first argument provided is
        used.
        @param lang1
        @param lang2
        """
        single_language = False
        if lang_1 == lang_2:
            single_language = True

        self.lang_1 = lang_1.lower()
        self.lang_2 = lang_2.lower()
        self.europarl_prefix = 'europarl-v7.'

    def lang_to_lang_infix(self):
        """Return infixes like 'de-en' and 'en-de' as tuple. """
        return self.lang_1 + '-' + self.lang_2, \
               self.lang_2 + '-' + self.lang_1
        
    def europarl_filepaths(self, randfile=False):
        """Get europarl file suffix, e. g. 'europarl-v7.de-en.de' 
           and europarl-v7.de-en.en"""
        randfile_suffix = ""
        if randfile:
               randfile_suffix = "_rand"
               
        return DATA_DIR_IN + sep + self.europarl_prefix + \
               self.lang_to_lang_infix()[0] + \
               '.' + self.lang_1 + randfile_suffix, \
               DATA_DIR_IN + sep + self.europarl_prefix + \
               self.lang_to_lang_infix()[0] + \
               '.' + self.lang_2 + randfile_suffix
