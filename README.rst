europarl-dissect
================

``europarl-dissect`` is an experimental toolset to play around with
distributional semantics. 

Its basic intuition is to provide the best translation candidates for
the words of a sentence (for any language direction we have training
material for), but not just considering global relatedness of words
in a training corpus, but also taking into account the concrete words
of the input sentence provided.

By principle the system can also be used to check for relatedness of
words in only *one* language, thus not giving translations, but more
of synsets or semantic nets -- still considering the local context of
the sentence provided.

It consists of two programs, one for preparing and preprocessing the
input data, the other one to calculate the similarity of input material to 
the semantic space established and show off the candidates.

- ``create_input_data.py`` processes (parallelized) training data available
- ``besttranslations.py`` shows candidates based on training data and input

Dependencies
------------
TBD
