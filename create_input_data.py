#!/usr/bin/python2
# -*- coding: utf-8 -*-

'''
TODO:
- Make system more flexible / variable (to use with other languages).
- Allow proper use of single language (-s option) data creation.
- Increase speed of TreeTagger usage (-l option).
- Make again use of standard TreeTagger programs
  (no use of -new versions).
- Transfer code to helpers.py or parameters.py.
'''

from argparse import ArgumentParser
from collections import defaultdict
from itertools import combinations
from os import sep, makedirs
from os.path import exists
import subprocess
from sys import exit

from nltk.corpus import stopwords
from nltk import word_tokenize

from lib.dissect.composes.semantic_space.space import Space
from lib.dissect.composes.utils import io_utils
from lib.ttpw.treetaggerwrapper import TreeTagger

from helpers import DATA_DIR, DATA_DIR_IN, DATA_DIR_OUT, LONG_LANGTAG
from helpers import getTag
from helpers import Suffixes
from parameters import LANG_1, LANG_2, SENTENCES_LIMIT, \
                       MAX_SENTENCE_LEN, PAIR_OCC_THRESHOLD, \
                       TREETAGGER_BASE_PATH

# Input files (col file, row files and sparse matrix files) for DISSECT
OUTPUT_FILE_DE_DE_EN_SM = ''.join([DATA_DIR_OUT, 'de_de-en.sm'])
OUTPUT_FILE_EN_EN_DE_SM = ''.join([DATA_DIR_OUT, 'en_en-de.sm'])
OUTPUT_FILE_DE_EN_WORDS_COL = ''.join([DATA_DIR_OUT, 'de_en-words.col'])
OUTPUT_FILE_DE_WORDS_ROW = ''.join([DATA_DIR_OUT, 'de-words.row'])
OUTPUT_FILE_EN_WORDS_ROW = ''.join([DATA_DIR_OUT, 'en-words.row'])
OUTPUT_FILE_DE_DE_EN_PKL = ''.join([DATA_DIR_OUT, 'de_de-en.pkl'])
OUTPUT_FILE_EN_EN_DE_PKL = ''.join([DATA_DIR_OUT, 'en_en-de.pkl'])

# Single language output files (despite *_ROW files)
# (Despite that: a *_ROW file *is* a *_COL file)
OUTPUT_FILE_DE_SM = ''.join([DATA_DIR_OUT, 'de.sm'])
OUTPUT_FILE_EN_SM = ''.join([DATA_DIR_OUT, 'en.sm'])
OUTPUT_FILE_DE_PKL = ''.join([DATA_DIR_OUT, 'de.pkl'])
OUTPUT_FILE_EN_PKL = ''.join([DATA_DIR_OUT, 'en.pkl'])
OUTPUT_FILE_DE_WORDS_COL = ''.join([DATA_DIR_OUT, 'de-words.col'])
OUTPUT_FILE_EN_WORDS_COL = ''.join([DATA_DIR_OUT, 'en-words.col'])

# Symbols to ignore (besides stopwords)
IGNORE_LIST = ['.', ',', ';', '(', ')', '-', ':', '!', '?', '\'']

# Treetagger location
TREETAGGER_DIR = ''.join(['treetagger', sep, 'cmd', sep])

suffixes = Suffixes(LANG_1, LANG_2)

# Global variables for command-line control.
global single_language, use_treetagger, sentences_limit, lang_1, \
       lang_2, treetagger_path
language_used  = False
use_treetagger = False
sentences_limit = SENTENCES_LIMIT # Assign default number
lang_1 = LANG_1 # Default lang 1
lang_2 = LANG_2 # Default lang 2
# Default path; should be changed in parameters.py file, or at least
# set by --treetagger-path parameter option.
treetagger_path = TREETAGGER_BASE_PATH

# Parallalized sentences of europarl
# Input data gotten from here: http://www.statmt.org/europarl/
europarl_files = \
{
    lang_1 : suffixes.europarl_filepaths()[0],
    lang_2 : suffixes.europarl_filepaths()[1]
}

class AlignedSentences:
    
    def __init__(self, sentences_1, sentences_2, 
                 filter_sentences=False):
        ''' 
        XXX: Some sanity should be done here to ensure
             the number of sentences match.
        '''
        self.sentences_1 = sentences_1
        self.sentences_2 = sentences_2
        self.number_sentences = sentences_1.sentences.keys()[-1]
        self.pairs_combined = defaultdict(int)
        self.no_sentences_filtered = 0
        
        # In parallel throw out sentences which are considered too long.
        if filter_sentences == True:
            self._filter_sentences()
        
    def _filter_sentences(self):
        '''Filter sentences upon criteria of word length. The idea is
           to not compare too long sentences with each other.
        '''
        for sentence_no, sentence in self.sentences_1.sentences.items():
            if len(sentence) > MAX_SENTENCE_LEN or \
            len(self.sentences_2.sentences[sentence_no]) > \
            MAX_SENTENCE_LEN:
                self.no_sentences_filtered += 1
                self.sentences_1.sentences[sentence_no] = ['DELETED']
                self.sentences_2.sentences[sentence_no] = ['DELETED']
                
        print(str(self.no_sentences_filtered) + " sentences emptied, " \
              + "because of word length higher than " \
              + str(MAX_SENTENCE_LEN) + ".")
        
    def combine_words(self):
        # Iterate through sentence numbers
        for i in range(1, self.number_sentences + 1):
            bilingual_sentence = self._get_bilingual_sentence(i)
            # complexity: quadratic
            pairs = combinations(bilingual_sentence, 2)
            for pair in pairs:
                self.pairs_combined[pair] += 1
                
        print(len(self.pairs_combined))

    def _write_sparse_matrix(self, output_file, lang):
        """Write out pairs in a sparse matrix format for DISSECT
           cf. 
           http://clic.cimec.unitn.it/composes/toolkit/ex01input.html
        """
        f = open(output_file, 'w')
        
        if lang == lang_1:
            for pair, count in self.pairs_combined.items():
                if count >= PAIR_OCC_THRESHOLD:
                    # We only want lang_1-lang_1 and lang_1-lang_2
                    # combinations.
                    if ''.join(['_', lang_1]) in pair[0]:
                        f.write(''.join([pair[0], ' ', pair[1], 
                            ' ', str(count), '\n']))
        # Assume lang_2 is meant.
        else:
            for pair, count in self.pairs_combined.items():
                if count >= PAIR_OCC_THRESHOLD:
                    # We only want lang_2-lang_2 and lang_2-lang_1
                    # combinations.
                    if ''.join(['_', lang_2]) in pair[1]:
                        f.write(''.join([pair[1], ' ', pair[0], 
                            ' ', str(count), '\n']))
        
        print('SM file written out: ' + output_file)
        
        f.close()
        
    def write_sparse_matrices(self):
        """ Write sm matrices."""
        
        # E. g. de-en
        self._write_sparse_matrix(OUTPUT_FILE_DE_DE_EN_SM, lang_1)
        
        # E. g. en-de
        self._write_sparse_matrix(OUTPUT_FILE_EN_EN_DE_SM, lang_2)
        
    def write_col(self):
        """Write out col of words (all words in both languages)
        """
        col = set()
        for pair, count in self.pairs_combined.items():
            if count >= PAIR_OCC_THRESHOLD:
                col.add(pair[0])
                col.add(pair[1])
        
        f = open(OUTPUT_FILE_DE_EN_WORDS_COL, 'w')
        for token in col:
            f.write(''.join([token, '\n']))
        f.close()
        
        print('Col file written out: ' + OUTPUT_FILE_DE_EN_WORDS_COL)
        
    def write_row(self):
        """Write out row of words (language dependent each)
        """
        row_1 = set()
        row_2 = set()
        
        for pair, count in self.pairs_combined.items():
            if count >= PAIR_OCC_THRESHOLD:
                # Collect lang 1 words
                if ''.join(['_', lang_1]) in pair[0]:
                    row_1.add(pair[0])
                else:
                    row_2.add(pair[0])
                # Collect lang 2 words
                if ''.join(['_', lang_1]) in pair[1]:
                    row_1.add(pair[1])
                else:
                    row_2.add(pair[1])
        
        f = open(OUTPUT_FILE_DE_WORDS_ROW, 'w')
        for token in row_1:
            f.write(''.join([token, '\n']))
        f.close()
        
        print('Row file written out: ' + OUTPUT_FILE_DE_WORDS_ROW)
        
        f = open(OUTPUT_FILE_EN_WORDS_ROW, 'w')
        for token in row_2:
            f.write(''.join([token, '\n']))
        f.close()
        
        print('Row file written out: ' + OUTPUT_FILE_EN_WORDS_ROW)
        
    def write_pkl(self):
        """
        Create spaces from co-occurrence counts in sparse format (.sm)
        """
        
        # For direction DE-EN
        my_space_1 = Space.build(data = OUTPUT_FILE_DE_DE_EN_SM ,
                       rows = OUTPUT_FILE_DE_WORDS_ROW,
                       cols = OUTPUT_FILE_DE_EN_WORDS_COL,
                       format = "sm")
        
        # For direction EN-DE   
        my_space_2 = Space.build(data = OUTPUT_FILE_EN_EN_DE_SM,
                       rows = OUTPUT_FILE_EN_WORDS_ROW,
                       cols = OUTPUT_FILE_DE_EN_WORDS_COL,
                       format = "sm")
        
        # Save the space objects in pickle format
        io_utils.save(my_space_1, OUTPUT_FILE_DE_DE_EN_PKL)
        io_utils.save(my_space_2, OUTPUT_FILE_EN_EN_DE_PKL)
        
        print('Pickle file written out: ' + OUTPUT_FILE_DE_DE_EN_PKL)
        print('Pickle file written out: ' + OUTPUT_FILE_EN_EN_DE_PKL)
        
    def _get_bilingual_sentence(self, counter):
        """Get a sentence with united tokens."""
        marked_sentence_1 = self._mark_tokens_by_lang(self.sentences_1.\
                            sentences[counter], self.sentences_1.lang)
        marked_sentence_2 = self._mark_tokens_by_lang(self.sentences_2.\
                            sentences[counter], self.sentences_2.lang)
        
        return marked_sentence_1 + marked_sentence_2
        
    def _mark_tokens_by_lang(self, tokens, lang):
        """Mark tokens with a language tag -- as suffix."""
        marked_tokens = []
        
        # Only do this when TreeTagger wasn't used.
        if not use_treetagger:
            for token in tokens:
                marked_tokens.append(token + '_' + lang)
        else:
            marked_tokens = tokens
            
        return marked_tokens
            
class Sentences:
    
    def __init__(self, lang):
        self.lang = lang
        self.sentences = {}
        
        if use_treetagger:
            self.treetagger = TreeTagger(TAGLANG=lang,
                                         TAGDIR=treetagger_base_path,
                                         TAGINENC="utf8",
                                         TAGOUTENC="utf8")
        
    def read_sentences(self):
        """Read in sentences from a file in a given language.
        """
        with open(europarl_files[self.lang], 'r') as f:
            i = 0
            for sentence in f:
                i += 1
                
                # Show some progress
                if self._is_sentence_to_print(i, 10):
                    print(i)
                    
                # Process sentence furtherly (tokenization & filtering)
                if use_treetagger:
                    self._process_sentence_tt(sentence.rstrip(), i)
                else:
                    self._process_sentence(sentence.rstrip(), i)
                
                # Eventually stop
                if sentences_limit == i:
                    break
                
            print('Number of sentences \'' + self.lang + '\' read in: ' 
                   + str(i))
                   
    def _process_sentence(self, sentence, counter):
        tokens = word_tokenize(sentence)
        tokens_filtered = self._filter_tokens(tokens)
        self.sentences[counter] = tokens_filtered
        
    def _process_sentence_tt(self, sentence, counter):
        """Process sentence with Treetagger"""
        tokens_pos_tagged = []
                        
        treetagger_tokens = self.treetagger.TagText(sentence)
        token_pos_tagged = None
        for token in treetagger_tokens:
            token_pos_tagged = token.split('\t')
            if len(token_pos_tagged) != 3:
                print "Caution -- broken TreeTagger case: ", \
                      token_pos_tagged, "(list)"
                continue # Skip it
            pos_tag = getTag(token_pos_tagged[1], lang_1)
            token = token_pos_tagged[2].lower()
            # Those cases we don't want.
            if not token in ["<unknown>", "@ord@", "@card@"] and \
               not pos_tag == "0":
                token +=  '_' + pos_tag + '_' + self.lang
                tokens_pos_tagged.append(token)

        self.sentences[counter] = tokens_pos_tagged
        
    def _filter_tokens(self, tokens):
        tokens_filtered = []
        
        for token in tokens:
            # Do not hold interpunctional signs and stopwords
            if token not in IGNORE_LIST and \
               token.lower() not in stopwords.\
               words(LONG_LANGTAG[self.lang]):
                # Add hold tokens in lowered form
                tokens_filtered.append(token.lower())
        
        return tokens_filtered
                
    def _is_sentence_to_print(self, counter, number):
        """Just the number of sentences to be read to display.
        counter: Number of sentences already processed.
        number:  Number of sentences that have to be processed.
        """
        if counter % number == 0:
            return True
        
        return False
        
def create_folder(dir_location, problem_str):
    """
    Create folders if not already done.
    @param dir_location: Concrete path to check and eventually create.
    @param  problem_str: String to indicate there's a folder missing.
    """
    if not exists(dir_location):
        print(problem_str + dir_location)
        makedirs(dir_location)
        print("Now created.")
    
def handle_arguments():
    """This function handles command-line options and arguments
       provided."""
    
    # Variables here are to be seen and set globally.
    global single_language, use_treetagger, sentences_limit, lang_1, \
           lang_2, treetagger_path
           
    argparser = ArgumentParser(description=\
                               'Create DISSECT input material.')
    argparser.add_argument('-s', '--single-language', 
                           help="Specifies that input material " + \
                                "only for specified language is " + \
                                "created.",
                           type=str)
    argparser.add_argument('-t', '--use-treetagger',
                           help="Make sure TreeTagger is used for " + \
                                "lemmatization and PoS tagging.",
                           action="store_true")
    argparser.add_argument('-l', '--sentences-limit',
                           help="Make sure there's a (low) maximum " + \
                                "number of sentences to read in.",
                           type=int)
    argparser.add_argument('-tp', '--treetagger-path',
                           help="Specifiy path where TreeTagger " + \
                                "cmd directory resides.",
                           type=str)
    argparser.add_argument('lang_1', nargs="?")
    argparser.add_argument('lang_2', nargs="?")
    pargs = argparser.parse_args()
    
    # User only wants a specific language, e. g. 'de' for German
    if(pargs.single_language):
        single_language = pargs.single_language.lower()
        print(single_language)
    else:
        single_language = None
        
    # User can decide to use TreeTagger (for lemmatization and PoS
    # tagging).
    if(pargs.use_treetagger):
        use_treetagger = True
    
    # Number of sentences we allow.
    if(pargs.sentences_limit):
        sentences_limit = pargs.sentences_limit
    
    # Check if any input data is missing
    for lang in europarl_files.keys():
        if not exists(europarl_files[lang]):
            print('Input data \'' + lang + '\' is missing.' +
                  ' (Check location: ' + europarl_files[lang] + ')'
                 )
   
    # Languages can be specified as arguments.
    if(pargs.lang_1):
        if (pargs.lang_2):
            lang_1, lang_2 = pargs.lang_1, pargs.lang_2
        else:
            argparser.print_help()
            exit(2)
            
    # Check if TreeTagger cmd path was specified.
    if(pargs.treetagger_path):
        treetagger_path = pargs.treetagger_path
        # Make sure there's a directory seperator at the end.
        if treetagger_path[-1] != sep:
            treetagger_path += sep

def create_bilingual_input():
    """Creates input material for two languages (bilingual input
       material), which is interesting to create translation
       candidates between two languages' words."""
    
    # Read first language's sentences
    sentences_1 = Sentences(lang_1)
    sentences_1.read_sentences()
    
    # Read second language's sentences
    sentences_2 = Sentences(lang_2)
    sentences_2.read_sentences()
    
    # Combine words on basis of their sentences after filtering out
    # long sentences.
    aligned_sentences = AlignedSentences(sentences_1, 
                                         sentences_2,
                                         filter_sentences=True)
    aligned_sentences.combine_words()
        
    # Write pairs in sparse matrix format
    aligned_sentences.write_sparse_matrices()
    
    # Write tokens to a col format
    aligned_sentences.write_col()
    
    # Write tokens to a row format
    aligned_sentences.write_row()
    
    # Write pickle files (for faster processing in 
    # besttranslations.py)
    aligned_sentences.write_pkl()
        
def create_singlelang_input():
    """Creates input material for a single language, which can be
       used to look for similarities between words."""
    sentences = Sentences(single_language)
    sentences.read_sentences()
    # XXX: Still not functional.
    
def main():
    # Handle command-line arguments and options.
    handle_arguments()
   
    # Create input and output folders if not the case already.
    create_folder(DATA_DIR_OUT, "Output dir not given: ")
    create_folder(DATA_DIR_IN, "Input dir not given: ")
   
    # single_language is None if not used.
    # Normal use is to work with two languages.
    if not single_language:
        create_bilingual_input()
    else:
        create_singlelang_input()
    
if __name__ == '__main__':

    main()
