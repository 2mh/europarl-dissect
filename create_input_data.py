#!/usr/bin/python2
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from collections import defaultdict
from itertools import combinations
from os import sep, makedirs
from os.path import exists
import subprocess

from composes.semantic_space.space import Space
from composes.utils import io_utils
from nltk.corpus import stopwords
from nltk import word_tokenize

from helpers import DATA_DIR, DATA_DIR_IN, DATA_DIR_OUT, LONG_LANGTAG
from helpers import getTag
from helpers import Suffixes

# Both languages involved / default languages used
LANG_1 = 'de'
LANG_2 = 'en'

suffixes = Suffixes(LANG_1, LANG_2)

# Symbols to ignore (besides stopwords)
IGNORE_LIST = ['.', ',', ';', '(', ')', '-', ':', '!', '?', '\'']

# Treetagger location
TREETAGGER_DIR = ''.join(['treetagger', sep, 'cmd', sep])

# Parallalized sentences of europarl
# Input data gotten from here: http://www.statmt.org/europarl/
europarl_files = \
{
    LANG_1 : suffixes.europarl_filepaths()[0],
    LANG_2 : suffixes.europarl_filepaths()[1]
}

treetagger_paths = \
{
    LANG_1 : ''.join([TREETAGGER_DIR, 'tree-tagger-german-utf8-new']),
    LANG_2 : ''.join([TREETAGGER_DIR, 'tree-tagger-english-utf8-new'])
}

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

# Limit number of sentences to process (for testing purposes).
# For no limit, set None
SENTENCES_LIMIT = 1000000

# Filter out sentences which are longer than this number, in one or
# the other language -- wherever first.
MAX_SENTENCE_LEN = 100000

# Minimal number of occurrences wanted.
# For no threshold, set anything below 2
PAIR_OCC_THRESHOLD = 1

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

    def _write_sparse_matrix(self, output_file, primary_language):
        """Write out pairs in a sparse matrix format for DISSECT
           cf. 
           http://clic.cimec.unitn.it/composes/toolkit/ex01input.html
        """
        f = open(output_file, 'w')
        
        for pair, count in self.pairs_combined.items():
            if count >= PAIR_OCC_THRESHOLD:
                # We only want e. g.  '_de' -> '_de' and '_de' -> '_en'
                # combinations, given primary_language is 'de'.
                if ''.join(['_', primary_language]) in pair[0]:
                    f.write(''.join([pair[0], ' ', pair[1], 
                        ' ', str(count), '\n']))
        print('SM file written out: ' + output_file)
        
        f.close()
        
    def write_sparse_matrices(self):
        """ Write sm matrices."""
        
        # E. g. de-en
        self._write_sparse_matrix(OUTPUT_FILE_DE_DE_EN_SM, LANG_1)
        
        # E. g. en-de
        self._write_sparse_matrix(OUTPUT_FILE_EN_EN_DE_SM, LANG_2)
        
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
                if ''.join(['_', LANG_1]) in pair[0]:
                    row_1.add(pair[0])
                else:
                    row_2.add(pair[0])
                # Collect lang 2 words
                if ''.join(['_', LANG_1]) in pair[1]:
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
        
        treetagger = subprocess.Popen([treetagger_paths[self.lang]],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
        treetagger_out = treetagger.communicate(sentence)[0]
        treetagger_token = treetagger_out.split('\n')
        for token in treetagger_token:
            token_pos_tagged = token.split('\t')
            pos_tag = getTag(token_pos_tagged[0], LANG_1)
            if pos_tag != "0":
                token = token_pos_tagged[1].lower() +  '_' + pos_tag \
                + '_' + self.lang
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

def main():
    global language_used, use_treetagger, sentences_limit
    language_used  = False
    use_treetagger = False
    sentences_limit = SENTENCES_LIMIT # Assign default number

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
    pargs = argparser.parse_args()
    
    # User only wants a specific language, e. g. 'de' for German
    if(pargs.single_language):
        language_used = pargs.single_language.lower()
        print(language_used)
        
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
   
    # Create output folder if not done
    if not exists(DATA_DIR_OUT):
        print('Output dir not given: ' + DATA_DIR_OUT)
        makedirs(DATA_DIR_OUT)
        print('Now created.')
   
    if not language_used:
        # Read German sentences
        sentences_de = Sentences(LANG_1)
        sentences_de.read_sentences()
        
        # Read English sentences
        sentences_en = Sentences(LANG_2)
        sentences_en.read_sentences()
        
        # Combine words on basis of their sentences after filtering out
        # long sentences.
        aligned_sentences = AlignedSentences(sentences_de, 
                                             sentences_en,
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
    else:
        sentences = Sentences(language_used)
        sentences.read_sentences()
    
if __name__ == '__main__':

    main()
