**Table of Contents**

.. contents::
    :local:
    :depth: 2
    :backlinks: none

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

- `NLTK 2.0.4 <http://www.nltk.org/>`__
- `SciPy 0.12.0 <http://sourceforge.net/projects/scipy/>`__

The following two frameworks are included inside the ``lib/`` directory,
to ensure better compatibility for the time being:

- `DISSECT 0.1.0 <http://clic.cimec.unitn.it/composes/toolkit/installation.html>`__ is used for creating the semantic spaces and calculate all similarities involved.
- `TreeTaggerWrapper <http://perso.limsi.fr/pointal/?id=dev:treetaggerwrapper>`__  allows to efficiently access the `TreeTagger <http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/>`__  program for POS tagging and lemmatization of the input material in various languages.

Installation
------------

### TreeTagger installation

TBD

### TreeTagger configuration

TBD

### Installation of europarl training data

TBD

### Preparing a (small) set of testing data 

TBD

### Clone the source code

TBD

Usage
-----
TBD
