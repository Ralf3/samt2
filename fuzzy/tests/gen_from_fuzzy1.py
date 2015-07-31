#!/usr/bin/env python

# reads in a fuzzy model and generates a noisy set of data for
# training of it
import sys
sys.path.append('../')
import Pyfuzzy as fuzz
import numpy as np

# change this for different models

f1=fuzz.read_model('gen_data1.fis',DEBUG=0)
datasize=200
x1min=0
x1max=10

# generate the training data
print 'x,y'
for i in range(datasize):
    x=(x1max-x1min)*np.random.rand()+x1min
    y=f1.calc1(x)
    y=np.random.normal(y,0.1) # add some noise
    print x,y
        
