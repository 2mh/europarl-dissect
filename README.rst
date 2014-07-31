**Table of Contents**

.. contents::
    :local:
    :depth: 2
    :backlinks: none

europarl-dissect
================

Introduction
------------

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
``europarl-dissect`` runs under Python versions >= 2.6.6.

It was tested with following additional Python libraries it externally
relies on:

- `DISSECT 0.1.0 <http://clic.cimec.unitn.it/composes/toolkit/installation.html>`__ is used for creating the semantic spaces and calculate all similarities involved.
- `NLTK 2.0.4 <http://www.nltk.org/>`__
- `SciPy 0.12.0 <http://sourceforge.net/projects/scipy/>`__

The following program is included inside the ``lib/`` directory to ensure better compatibility for the time being (as the package
doesn't appear packaged by operating systems or e. g. pip2):

- `TreeTaggerWrapper <http://perso.limsi.fr/pointal/?id=dev:treetaggerwrapper>`__  allows to efficiently access the `TreeTagger <http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/>`__  program for POS tagging and lemmatization of the input material in various languages.

Installation
------------

Resolving the dependencies
**************************

The three libraries required as stated above can either be installed from operating system package systems (as this is the case for
SciPy) or from pip2.

On a Debian operating system usually the following commands can be issued (as root) to bring these dependencies satisfied:

::

	apt-get install python-scipy
	pip2 install nltk
	pip2 install dissect


TreeTagger configuration
************************

After installing the TreeTagger package (cf. information on the project's home
given above) it is necessary to specify where its base directory can be found.

In fixed form this can be specified in the ``parameters.py`` file by setting
the ``TREETAGGER_BASE_PATH`` variable accordingly. The path can be
specified either relatively to the project's directory or in absolute
terms.

Installation of europarl training data
**************************************

There is a ``README.rst`` file in ``data/in/`` giving more information
on where to find the europarl files we used to test the system.

Please note that by principle also other data material can be used
as long as long as it simple adheres to the format provided by the
europarl corpus (each language in plain text (UTF-8) with one sentence 
per line). 

Preparing a (small) set of testing data 
***************************************

Example input material to test ``europarl-dissect`` for its disambiguation 
capabilities and example usage can be found in the files ``data/eval-de.txt``
and ``data/eval-en.txt`` for some German and English sentences, respectively.

More sentences in the same text domain can be found in ``data/europarl_2014_de.txt``
and ``data/europarl_2014_en.txt``. It is also possible to use input material in
the TreeTagger outpout format -- this is exemplified by ``europarl/europarl_2014_de_tagged.txt``
and ``europarl_2014_en_tagged.txt``.

Most important thing to note is of course to not use sentences which are
already part of the training material, as this would result in (clearly)
biased results.

Clone the source code
*********************

To download and test our code, simply issue the following command:

::
	
	git clone https://github.com/2mh/europarl-dissect.git

This will create the folder ``europarl-dissect`` from which on you can
work.

Usage
-----

Basic usage
***********

If you download the code and put in place some training data (assuming
the files ``data/in/europarl-v7.de-en.de`` and
``data/in/europarl-v7.de-en.de`` exist), you can immediately test the system, 
by the following commands:

::

	# Create training material with 1,000 sentences.
	./create_input_data.py -l 1000
	# Test with test input material provided.
	./show_candidates.sh de en # From DE to EN
	./show_candidates.sh en de # From EN to DE

To test the system with lemmatized training and input material, do the
following:

::
	
	# As above, but with lemmatization; -t meaning to use TreeTagger.
	./create_input_data.py -l 1000 -t
	# The -l option makes sure the system knows it deals with lemmatization.
	./show_candidates.sh de en -l # From DE to EN, lemmatized
	./show_candidates.sh de en -l # From DE to EN, lemmatized

Advanced usage
**************
To follow.
