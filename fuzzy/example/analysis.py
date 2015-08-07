#!/usr/bin/env python

# a simple statistical analysis for demo only

import numpy as np
import pandas as pd
import sys

if(len(sys.argv)!=2):
    print 'usage analysis with a filename with the data'
    sys.exit(1)
try:
    my_data=np.genfromtxt(sys.argv[1], delimiter=' ')   
except IOError:
    print 'error in read_data: can not open file: ', filename
    sys.exit(2)
data=pd.DataFrame(my_data)
print data.describe()    
sys.exit(0)
    
