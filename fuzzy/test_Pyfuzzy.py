#!/usr/bin/env python

# some tests for fuzzy toolbox

import numpy as np
import Pyfuzzy as fuzz
import sys
sys.path.append('../')
import grid as samt2
import pytest

class TestClass:
    def test_calc3(self):
        f1=fuzz.read_model('hab_schreiadler.fis')
        data=np.genfromtxt('hab_leer.txt', delimiter=' ', skiprows=1)
        val=0
        count=data.shape[0]
        for i in range(count):
            val+=f1.calc3(data[i,0],data[i,1],data[i,2])
        val/=count
        assert(val>0.34 and val<0.35)
    def test_train(self):
        f1=fuzz.read_model('hab_schreiadler.fis')
        f1.read_training_data('train_hab_leer.csv', header=1)
        rmse1=f1.get_rmse()
        fuzz.start_training(f1)
        rmse2=f1.get_rmse()
        assert(rmse2<rmse1)

pytest.main()
