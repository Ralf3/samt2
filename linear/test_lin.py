#!/usr/bin/env python

# some tests for liblinear training

import numpy as np
import linear_mod as lm
import sys
sys.path.append('../')
import grid as samt2
import pytest

class TestClass:
    def test_simple_1(self):
        size=5000      # training size
        x1=np.random.rand(size)
        y=np.where(x1>0.5,1,0) 
        m=lm.linsvm('x1') 
        m.C=1
        m.bias=0.5
        x1.shape=(size,1)
        inp=x1.tolist()
        for i in range(8):
            m.L=i
            m.train(inp,y)
            p_labels, p_acc, p_vals=m.predict(inp,y)
            print i, p_acc
            assert p_acc[0]>=99
    def test_simple_3(self):
        size=5000      # training size
        x1=np.random.rand(size)
        x2=np.random.rand(size)
        x3=np.random.rand(size)
        y=np.where(x1+x2+x3>1.0,1,0)
        m=lm.linsvm('x1','x2','x3')
        m.bias=0.5
        m.C=2.0
        inp=[]
        for i in range(len(x1)):
            inp.append([x1[i],x2[i],x3[i]])
        m.train(inp,y)
        p_labels, p_acc, p_vals=m.predict(inp,y)
        print p_acc
        assert p_acc[0]>=95
    def test_grid(self):
        """ A test for training sample data and apply it to the
            grid
        """
        # define the grids
        gwd=samt2.grid()
        rise=samt2.grid()
        ufc=samt2.grid()
        relyield=samt2.grid()
        # load the grids
        gwd.read_hdf('../data/training.h5','gwd')
        rise.read_hdf('../data/training.h5','rise')
        ufc.read_hdf('../data/training.h5','ufc')
        relyield.read_hdf('../data/training.h5','relyield')
        # normalize the inputs
        gwd.norm()
        rise.norm()
        ufc.norm()
        # generate the training sample
        size=500
        inp=[]
        y=np.zeros(size)     # outputs 1
        nrows,ncols=gwd.size()
        k=0                  # counter for the sample
        while(k<size):
            i=np.random.randint(nrows)
            j=np.random.randint(ncols)
            if(gwd.get(i,j)==gwd.get_nodata() or
                rise.get(i,j)==rise.get_nodata() or
                ufc.get(i,j)==ufc.get_nodata() or
                relyield.get(i,j)==relyield.get_nodata()):
                continue
            inp.append([gwd.get(i,j),rise.get(i,j),ufc.get(i,j)])
            y[k]=np.sign(relyield.get(i,j)-1.0)
            k+=1
        # start training
        m=lm.linsvm('gwd','rise','ufc')
        m.train(inp,y)
        res=m.calc(gwd,rise,ufc)
        assert res.corr(relyield)>0.6
        

pytest.main()
