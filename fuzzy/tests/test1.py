#!/usr/bin/env python

# reads a one dimensional fuzzy model and a training data set
# to train rules
# the result will be stored as fuzzy model

import sys
sys.path.append('../')
import Pyfuzzy as fuzz

# adapt this for different tests
f1=fuzz.read_model('gen_data1.fis',DEBUG=1)
x,y=f1.read_training_data('data1.csv', header=1)
f1.train_rules(x,y,0.75)  # check the influence of different alpha
f1.store_model('data1')
