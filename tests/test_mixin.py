#!/usr/bin/env python
# simple test for different interpolation methods

import numpy as np
import sys
import os
# sys.path.append('/home/ralf/master/samt2')
sys.path.append(os.environ['SAMT2MASTER']+"/src")
import grid as samt2


gx=samt2.grid()
gx.read_hdf('/home/ralf/master/samt2/data/ziethen.hdf','zie_dgm')

for i in xrange(5,31):
    print  gx.complexity(i)

    
