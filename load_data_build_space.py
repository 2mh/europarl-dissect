#!/usr/bin/python2
# -*- coding: utf-8 -*-

from composes.semantic_space.space import Space
from composes.utils import io_utils

#create a space from co-occurrence counts in sparse format
my_space = Space.build(data = "./data/out/europarl.sm",
                       rows = "./data/out/europarl.row",
                       cols = "./data/out/europarl.row",
                       format = "sm")

#save the Space object in pickle format
io_utils.save(my_space, "./data/out/europarl.pkl")
