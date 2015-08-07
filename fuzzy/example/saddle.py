#!/usr/bin/env python

# prints threedimensional the saddle function:
# F(x,y)=x^2 -4*y^2
# and generates a sample data set from it

import pylab as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def saddle(x,y):
    return x**2-4*y**2

def make_data(nx=100,ny=100, xmin=-3,xmax=3,ymin=-2,ymax=2):
    """ nx=number of x values
        ny=number of y values
        min and max for both varibles
        returns X,Y,Z for plotting
    """
    x=np.linspace(xmin,xmax,nx)
    y=np.linspace(ymin,ymax,ny)
    (X,Y)=np.meshgrid(x,y)
    Z=saddle(X,Y)
    return X,Y,Z

def sample(n,X,Y,Z,nx=100,ny=100,filename="saddle.dat"):
    """ generates a sample of data from the saddle function:
        X,Y,Z data from make_data
        n=number of data, nx and ny
        filename: file to store the data
    """
    f=open(filename,"w")
    for i in range(n):
        xi=np.random.randint(nx)
        yi=np.random.randint(ny)
        s="%f %f %f\n" % (X[xi,yi],Y[xi,yi],Z[xi,yi])
        # print i, s
        f.write(s)
    f.close()
    
# plot it 3D

(X,Y,Z)=make_data()
sample(200,X,Y,Z)
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot_wireframe(X, Y, Z, rstride=1, cstride=1)
ax.set_xlabel('X')
ax.set_ylabel('Y')
plt.show()
