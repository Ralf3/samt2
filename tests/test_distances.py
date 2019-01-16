#!/usr/bin/env python3
# simple test for voronoi maps

import numpy as np
import time
import sys
import os
sys.path.append(os.environ['SAMT2MASTER']+"/src")
import grid as samt2

xsize=500          # size of the grid, can be slow if xsize>100
ysize=500
nsamples=50        # number of random samples

# define the grid and the random inputs
gx=samt2.grid(ysize,xsize)
x=np.random.randint(0,xsize,nsamples)
y=np.random.randint(0,ysize,nsamples)

# activate the poisson solver
t0=time.time()
gx.distance(y,x)
print "t=",time.time()-t0 

gx.show_contour()
