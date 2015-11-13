# samt2
A Python3/Cython module for "Spatial Analysis and Modeling"


samt2.py relies on Cython and gcc which should be installed

SAMT2 is a toolbox, written in Cython (will be comiled to a grid.so) wich can be used to do some spatial operations.
SAMT2 can:
  define a grid (matrix with geographical location)
  IO: read/write ASCII-Grids from ARCGIS, load and store grids in a HDF
  Create Random Grids,
  Access to data in a grid,
  Visualize grids (bw, color, 3D, ...)
  Statistics: mean, std, info, ...
  Simple and complex grid operations
  Kernel techniques,
  Floodfill algorithm,
  Add and Mul with other grids,
  Point operations, ...
  
The main idea of SAMT2 is to apply spatial data to fuzzy models, SVMs and other. It uses a lot of open source 
libraries and is itself open source. SAMT2 is the basis library and contains a fuzzy toolbox, has a graphical user 
interface including a help. It can be downloaded ready to use as a virtualbox image from:
http://www.zalf.de/en/forschung/institute/lsa/forschung/methodik/samt/Pages/Download.aspx

It is quite handy for my applications and I hope it will be useful for other.

To compile grid.py to grid.so please preform the following steps:

make 

In an Python program can samt2.py be used with:

import grid as samt2
