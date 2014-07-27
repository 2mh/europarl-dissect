europarl-dissect
================

``europarl-dissect`` is an experimental toolset to play around with
distributional semantics. 

Its basic intuition is to provide the best translation candidates for
the words of a sentence (for *any* language direction we have training
material for), but not just considering global relatedness of words
in a training corpus, but also taking into account the concrete words
of the input sentence provided.

By principle the system can also be used to check for relatedness of
words in only *one* language, thus not giving translations, but more
of synsets or semantic nets -- still considering the local context of
the sentence provided.

The system consists of two programs, one for preparing and preprocessing the
input data, the other one to calculate the similarity of each input word
to other words in the local and global semantic spaces established by
training and show off the best candidates available:

- ``create_input_data.py`` processes (parallelized) training data available
- ``besttranslations.py`` shows candidates based on training data and input

Dependencies
------------
``europarl-dissect`` runs under Python versions >= 2.7.6.

It was tested with following additional Python libraries it externally
relies on:

- NLTK 2.0.4 
- SciPy 0.12.0

It comes shipped with following two frameworks in its ``lib/`` directory
already, to ensure better compatibility for the time being:

- `DISSECT 0.1.0 <http://clic.cimec.unitn.it/composes/toolkit/installation.html>`__
- `TreeTaggerWrapper <http://perso.limsi.fr/pointal/?id=dev:treetaggerwrapper>`__

Installation
------------


Usage
-----
TBD
