#!/usr/bin/python2
# -*- coding: utf-8 -*-

from codecs import open
from collections import defaultdict
from itertools import combinations
from os import sep, makedirs
from os.path import exists

from nltk.corpus import stopwords
from nltk import word_tokenize

# Languages used
DE_LANG = 'de'
EN_LANG = 'en'

# Languages used (verbose)
LANG_LONG = \
{ 
    DE_LANG : 'german',
    EN_LANG : 'english' 
}

# Encoding used
ENC = 'utf-8'

# Symbols to ignore (besides stopwords)
IGNORE_LIST = ['.', ',', ';', '(', ')', '-', ':', '!', '?', '\'']

# Location of data (to read from, to write to)
DATA_DIR = ''.join(['data', sep])
DATA_DIR_IN  = ''.join([DATA_DIR, 'in', sep])
DATA_DIR_OUT = ''.join([DATA_DIR, 'out', sep])

# Parallalized sentences of europarl
# Input data gotten from here: http://www.statmt.org/europarl/
europarl_files = \
{
    DE_LANG : ''.join([DATA_DIR_IN, 'europarl-v7.de-en.de']),
    EN_LANG : ''.join([DATA_DIR_IN, 'europarl-v7.de-en.en'])
}

# Sparse matrix output file for feeding DISSECT
OUTPUT_FILE_SM  = ''.join([DATA_DIR_OUT, 'europarl.sm'])
OUTPUT_FILE_ROW = ''.join([DATA_DIR_OUT, 'europarl.row'])

# Limit number of sentences to process (for testing purposes).
# For no limit, set None
SENTENCES_LIMIT = 1000

# Filter out sentences which are longer than this number, in one or
# the other language -- wherever first.
MAX_SENTENCE_LEN = 1000000

# Minimal number of occurrences wanted.
# For no threshold, set anything below 2
PAIR_OCC_THRESHOLD = 0

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
                
    def write_sparse_matrix(self):
        """Write out pairs in a sparse matrix format for DISSECT
           cf. http://clic.cimec.unitn.it/composes/toolkit/ex01input.html
        """
        f = open(OUTPUT_FILE_SM, 'w', ENC)
        for pair, count in self.pairs_combined.items():
            if count >= PAIR_OCC_THRESHOLD: 
                f.write(''.join([pair[0], ' ', pair[1], 
                        ' ', str(count), '\n']).decode(ENC))
        f.close()
        
        print('SM file written out: ' + OUTPUT_FILE_SM)
        
    def write_row(self):
        """Write out row of words as given in the DISSECT tutorial
           cf. http://clic.cimec.unitn.it/composes/toolkit/ex01input.html
        """
        row = set()
        for pair, count in self.pairs_combined.items():
            if count >= PAIR_OCC_THRESHOLD:
                row.add(pair[0])
                row.add(pair[1])
        
        f = open(OUTPUT_FILE_ROW, 'w', ENC)
        for token in row:
            f.write(''.join([token, '\n']).decode(ENC))
        f.close()
        
        print('Row file written out: ' + OUTPUT_FILE_ROW)
            
            
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
        
        for token in tokens:
            marked_tokens.append(token + '_' + lang)
            
        return marked_tokens
            
class Sentences:
    
    def __init__(self, lang):
        self.lang = lang
        self.sentences = {}
        
    def read_sentences(self, limit=None):
        """Read in sentences from a file in a given language.
        limit: If provided with a number stop after given number of
               sentences.
        """
        with open(europarl_files[self.lang], 'r', ENC) as f:
            i = 0
            for sentence in f:
                i += 1
                
                # Show some progress
                if self._is_sentence_to_print(i, 1000):
                    print(i)
                    
                # Process sentence furtherly (tokenization & filtering)
                self._process_sentence(sentence.rstrip(), i)
                
                # Eventually stop
                if limit is not None:
                    if limit == i:
                        break
                
            print('Number of sentences \'' + self.lang + '\' read in: ' 
                   + str(i))
                   
    def _process_sentence(self, sentence, counter):
        tokens = word_tokenize(sentence.encode(ENC))
        tokens_filtered = self._filter_tokens(tokens)
        self.sentences[counter] = tokens_filtered
        
    def _filter_tokens(self, tokens):
        tokens_filtered = []
        
        for token in tokens:
            # Do not hold interpunctional signs and stopwords
            if token not in IGNORE_LIST and \
               token not in stopwords.words(LANG_LONG[self.lang]):
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
   
    
    # Read German sentences
    sentences_de = Sentences(DE_LANG)
    sentences_de.read_sentences(limit=SENTENCES_LIMIT)
    
    # Read English sentences
    sentences_en = Sentences(EN_LANG)
    sentences_en.read_sentences(limit=SENTENCES_LIMIT)

    '''
    # Example print out of german sentences read in
    for sentence_id in sentences_de.sentences.values():
        print sentence_id
    '''
    
    # Combine words on basis of their sentences after filtering out
    # long sentences.
    aligned_sentences = AlignedSentences(sentences_de, 
                                         sentences_en,
                                         filter_sentences=True)
    aligned_sentences.combine_words()
    
    '''
    # Show pairs
    for pair, count in aligned_sentences.pairs_combined.items():
        print(count, pair)
    '''
        
    # Write pairs in sparse matrix format
    aligned_sentences.write_sparse_matrix()
    
    # Write tokens to a row format
    aligned_sentences.write_row()
    
if __name__ == '__main__':
	main()
    
'''
TODO:
- Write out sm file in sorted form (by frequency)
- Remove _de _en pair entries in sm file
- Save temporary files to save time in further runs
'''
