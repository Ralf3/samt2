# SAMT2 and SAMT2FUZZY

## SAMT2 and SAMT2FUZZY are Python2/Cython module for 
"Spatial Analysis and Modeling". 


**samt2.py** relies on Cython and gcc which should be installed

**SAMT2** is a toolbox, written in Cython (will be comiled to a grid.so) wich can be used to do some spatial operations.

The main idea of SAMT2 is to apply spatial data to fuzzy models, SVMs and others. It uses a variety of open source libraries and is itself open source. SAMT2 is the base library and includes a fuzzy toolbox. However, it can also be used for convenient handling of spatial grid data. This makes SAMT2 suitable for integration into own Python programs.

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
  
It is quite handy for my applications and I hope it will be useful for other.

In a Python program **samt2.py** can be used with:

- import grid as samt2
- This is even possible for an ipython notebook, please test the examples.

