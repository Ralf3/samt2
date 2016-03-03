#!/usr/bin/env python

# some tests for fuzzy toolbox

import numpy as np
import sys
sys.path.append('../src')
import Pyfuzzy as fuzz
sys.path.append('../../src')
import grid as samt2
import pytest

class TestClass:
    def test_calc2(self):
        """ check the calc2 """
        f1=fuzz.read_model('nahr_schreiadler.fis')
        data=np.genfromtxt('train_nahr_leer.csv', delimiter=' ', skiprows=1)
        val=0
        count=data.shape[0]
        for i in range(count):
            val+=f1.calc2(data[i,0],data[i,1])
        val/=count
        assert(val>0.55 and val<0.59)
    def test_calc3(self):
        """ check the calc3 """
        f1=fuzz.read_model('hab_schreiadler.fis')
        data=np.genfromtxt('train_hab_leer.csv', delimiter=' ', skiprows=1)
        val=0
        count=data.shape[0]
        for i in range(count):
            val+=f1.calc3(data[i,0],data[i,1],data[i,2])
        val/=count
        assert(val>0.4 and val<0.5)
    def test_train(self):
        """ check the fuzzy  output training based on regularization """
        f1=fuzz.read_model('hab_schreiadler.fis')
        f1.read_training_data('train_hab_leer.csv', header=1)
        rmse1=f1.get_rmse()
        fuzz.start_training(f1)
        rmse2=f1.get_rmse()
        assert(rmse2<rmse1)
    def test_train_rules(self):
        """ check a simple rule training """
        f1=fuzz.read_model('gen_data1.fis',DEBUG=0)
        f1.read_training_data('data1.csv', header=1)
        f1.train_rules(0.75)  # check the influence of different alpha
        f1.store_model('data1')
        rules=f1.get_rules()
        s=0.0
        for rule in rules:
            s+=rule.get_cf()
        assert(s<len(rules))
    
pytest.main()
