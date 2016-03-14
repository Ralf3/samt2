#!/usr/bin/env python
import sys
import os
sys.path.append(os.environ['SAMT2MASTER']+"/src")
import grid as samt2
import pytest
import numpy as np
import math

# Test the simple functions of SAMT2


class TestClass:
    gx=samt2.grid(500,500)
    def test_gengrid(self):
        """ tests the grid generation """
        sx,sy=self.gx.size()
        assert sx==500 and sy==500
    def test_write(self):
        """ tests the read write of ASCII files """
        self.gx.write_ascii('xxx.asc')
        g1=samt2.grid()
        g1.read_ascii('xxx.asc')
        os.system('rm xxx.asc')
        sx,sy=g1.size()
        print sx,sy
        assert sx==500 and sy==500
    def test_random1(self):
        """ test the float random number generation """
        self.gx.randfloat()
        m,s=self.gx.mean_std()
        mean=0.5
        sigma=math.sqrt(1.0/12.0)
        assert math.fabs(m-sigma)<5*sigma   # otherwise bad random number
    def test_random2(self):
        """ randint using znorm """
        self.gx.randint()
        self.gx.znorm()
        m,s=self.gx.mean_std()
        assert math.fabs(m)<1.0e-5 and math.fabs(1.0-s) < 1.0e-3 
    def test_log(self):
        """ test simple numerik """
        self.gx.set_all(10.0)
        self.gx.log(0)
        m,s=self.gx.mean_std()
        assert m==1 and s==0
    def test_classify(self):
        """ test classify and unique """
        self.gx.randint(0,100)
        self.gx.classify()
        u=self.gx.unique()
        assert len(u)==10
    def test_cond(self):
        """ test a condition for a random grid """
        self.gx.randint(0,100)
        self.gx.cond(20,80)
        min=self.gx.get_min()[2]
        max=self.gx.get_max()[2]
        assert min==20 and max==80
    def test_cut_off(self):
        """ test the cut_off for removing a range """
        self.gx.randint(0,100)
        self.gx.cut_off(0,20,20)
        self.gx.cut_off(80,100,80)
        min=self.gx.get_min()[2]
        max=self.gx.get_max()[2]
        assert min==20 and max==80
        
pytest.main()
