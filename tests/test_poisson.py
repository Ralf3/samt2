#!/usr/bin/env python


import numpy as np
import time
import sys
sys.path.append('/home/ralf/master/samt2')
import grid as samt2

# test the poisson solver using random distributed values

nsamples=50        # number of random samples
xsize=100          # size of the grid, can be slow if xsize>100
ysize=100
maxiter=100000     # maximum number of iterations


# define the grid and the random inputs
gx=samt2.grid(ysize,xsize)
x=np.random.randint(0,xsize,nsamples)
y=np.random.randint(0,ysize,nsamples)
z=np.ones(nsamples)

# activate the poisson solver
t0=time.time()
gx.poisson(y,x,z,0.001*nsamples,maxiter)
print "t=",time.time()-t0

gx.show_contour()
