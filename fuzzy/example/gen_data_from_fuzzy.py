#!/usr/bin/env python

import numpy as np
import sys
import os
sys.path.append(os.getenv("SAMT2MASTER")+"/fuzzy/src")
import Pyfuzzy as fuzz

# The function gen(n,sep) is used to generate a CSV data set with n-lines
# and a speparator sep from a fuzzy system

def gen(n,sep=" "):
    f=fuzz.read_model('hab_schreiadler.fis') # please adapt this
    # f=fuzz.read_model('circle.fis') # please adapt this
    m=f.get_number_of_inputs()
    inputs={}
    # sample the min and max for each input
    s=""
    for i in range(m):
        min=f.get_min_input(i)
        max=f.get_max_input(i)
        inputs[f.get_input_name(i)]={'min': min, 'max' : max}
        s+=(f.get_input_name(i)+sep)
    s+=f.get_output_name()
    # generate the sample as CSV
    # print header
    print s
    for i in range(n):
        s=""
        for j in range(m):
            x=(inputs[f.get_input_name(j)]['max']-
                inputs[f.get_input_name(j)]['min'])*np.random.rand()+\
                inputs[f.get_input_name(j)]['min']
            if(j==0):
                x1=x
            if(j==1):
                x2=x
            if(j==2):
                x3=x
            s+="%f%s" % (x,sep)
        if(m==2):
            y=f.calc2(x1,x2)*(1+0.1*np.random.rand())
        if(m==3):
            y=f.calc3(x1,x2,x3)*(1+0.1*np.random.rand())
        s+="%f%s" % (y,sep)
        s=str(s[:-1])
        # s+='\n'
        print s
gen(500,' ')
