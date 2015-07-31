#!/usr/bin/env python

# reads in a fuzzy model and generates a noisy set of data for
# training of it
import sys
sys.path.append('../')
import Pyfuzzy as fuzz
import numpy as np

# change this for different models

f1=fuzz.read_model('hab_schreiadler.fis',DEBUG=0)
datasize=500
x1min=0.0
x1max=1.0
x2min=0.0
x2max=1000.0
x3min=0.0
x3max=5000.0

# generate the training data
print 'x1,x2,x3,y'
for i in range(datasize):
    x1=(x1max-x1min)*np.random.rand()+x1min
    x2=(x2max-x2min)*np.random.rand()+x2min
    x3=(x3max-x3min)*np.random.rand()+x3min
    y=f1.calc3(x1,x2,x3)
    y=np.random.normal(y,0.1) # add some noise
    print x1,x2,x3,y
        
