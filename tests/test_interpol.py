#!/usr/bin/env python
# simple test for different interpolation methods

import numpy as np
import sys
import os
# sys.path.append('/home/ralf/master/samt2')
sys.path.append(os.environ['SAMT2MASTER']+"/src")
import grid as samt2

inch   = 2.54      # cm
width  = 14.8      # cm postcard
height = 10.5      # cm postcard

res    = 300       # dots/inch
nrows  = int(height/inch*res)
ncols  = int(width/inch*res)

print('nrows:', nrows, 'ncols:', ncols)
size=25           # random points

# define the grid
gx=samt2.grid(nrows,ncols)
# generate random points x,y,z
x=np.random.randint(ncols,size=size)
y=np.random.randint(nrows,size=size)
z=np.random.rand(size)
# interpolation
intmeth=['linear','cubic','thin_plate']
for method in intmeth:
    print(method)
    gx.interpolate(x,y,z,method=method)
    gx.show_contour()
