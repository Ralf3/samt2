#!/usr/bin/env python
"""
# -*- coding: utf-8 -*-  
"""
import numpy as np
import liblinear as ll
import liblinearutil as lu
import time
import sys
import re
import os
sys.path.append('../')
import grid

class linsvm(object):
    """
    defines an object oriented svm modul based on liblinear
    L2R_LR = 0 
    L2R_L2LOSS_SVC_DUAL = 1 
    L2R_L2LOSS_SVC = 2    
    L2R_L1LOSS_SVC_DUAL = 3 
    MCSVM_CS = 4 
    L1R_L2LOSS_SVC = 5 
    L1R_LR = 6 
    L2R_LR_DUAL = 7  
    L2R_L2LOSS_SVR = 11
    L2R_L2LOSS_SVR_DUAL = 12
    L2R_L1LOSS_SVR_DUAL = 13
    with:
     0 -- L2-regularized logistic regression (primal)
	 1 -- L2-regularized L2-loss support vector classification (dual)
	 2 -- L2-regularized L2-loss support vector classification (primal)
	 3 -- L2-regularized L1-loss support vector classification (dual)
	 4 -- support vector classification by Crammer and Singer
	 5 -- L1-regularized L2-loss support vector classification
	 6 -- L1-regularized logistic regression
	 7 -- L2-regularized logistic regression (dual)
          for regression
	11 -- L2-regularized L2-loss support vector regression (primal)
	12 -- L2-regularized L2-loss support vector regression (dual)
	13 -- L2-regularized L1-loss support vector regression (dual)
    """
    def __init__(self,name1,*args):
        """ set the names for the inputs 1,2,3 """
        self.names=[name1]  # collect the names of the inputs
        for ar in args:
            self.names.append(ar)
        self.model=None    # start with empty model
        self.L=0           # 0: L2R_LR
        self.c=1           # cost factor
        self.eps=0.001     # tolerance of termination criterion
        self.p=0.1         # epsilon in loss function of epsilon-SVR
        self.bias=0.5      # if bias >= 0, instance x becomes [x; bias]
        self.q=0           # quiet mode (no outputs) default no
        self.v=0           # -v n: n-fold cross validation mode
        return None
    # svm specific parameter with checking
    @property
    def L(self):
        return self._L
    @L.setter
    def L(self,nt):
        if((nt in [0,1,2,3,4,5,6,7]) or (nt in [11,12,13]) ):
            self._L=nt
        else:
            print 'warning: L must be in [0,1,2,3,4,5,6,7,11,12,13]'
    # read/write define model
    def read_model(self,filename):
        """ read a model an overwrites the old one """
        try:
            self.model=ul.load_model(filename)
        except IOError:
            print("Error in reading file: ", filename)
            return False
        m=re.search("(.*)\.(lin)",filename)   # read the names from npy
        basename=m.group(1)
        try:
            self.name=np.load(basename+".npy")
        except IOError:
            self.name=['x1','x2','x3']
        return True
    def write_model(self,filename):
        """ store a model and the names """
        if(self.model!=None):
            self.model.save_model(filename)
            m=re.search("(.*)\.(lin)",filename)   # write the names to npy
            basename=m.group(1)
            np.save(basename,self.name)
            return True
        return False
    # definition and training are combined; the result of a training
    # procedure is a model which can be stored and loaded
    def train(self,x,y):
        """
        training using y=list,x=dict
        parameter = string of parameters
        """
        prob=lu.problem(y,x)
        para=""
        para+= "-s %d -c %f -B %f -p %f -e %f" % (self.L,
                                                  self.c,
                                                  self.bias,
                                                  self.p,
                                                  self.eps)
        if(self.v!=0):
            para+=" -v %d" % self.v
        if(self.q!=0):
            para+= " -q"
        print para
        para1=lu.parameter(para)
        self.model=lu.train(prob,para1)
        return True
    def best_C(self,x,y):
        """
        training using y=list,x=dict
        parameter = string of parameters
        searches for best C
        """
        prob=lu.problem(y,x)
        para=""
        para+= "-s 2 -C -B %f -p %f -e %f" % (self.bias,
                                              self.p,
                                              self.eps)
        print para
        para1=lu.parameter(para)
        self.model=lu.train(prob,para1)
        best_C, best_rate = lu.train(y, x, para)
        return best_C, best_rate
    def evaluation(self,ty,pv):
        """
        ty: a list of true values.
        pv: a list of predict values.    
        calculates the
            ACC: accuracy.
            MSE: mean squared error.
            SCC: squared correlation coefficient.
        """
        return lu.evaluations(ty, pv)
    def predict(self,x,y=[]):
        """
        
        x: a list/tuple of l predicting instances. The feature vector of
          each predicting instance is an instance of list/tuple or dictionary.

        y: a list/tuple of l true labels (type must be int/double). It is used
           for calculating the accuracy. Use [] if true labels are
           unavailable.
        predicting_options: a string of predicting options in the same
        format as that of LIBLINEAR.
        p_acc: a tuple including accuracy (for classification), mean
               squared error, and squared correlation coefficient (for
               regression).

        p_vals: a list of decision values or probability estimates (if '-b 1'
                is specified). If k is the number of classes, for decision
                values, each element includes results of predicting k
                binary-class SVMs. If k = 2 and solver is not MCSVM_CS, only
                one decision value is returned. For probabilities, each
                element contains k values indicating the probability that the
                testing instance is in each class.
                Note that the order of classes here is the same as
                'model.label' field in the model structure.
        """
        p_labels, p_acc, p_vals = lu.predict(y, x, self.model)
        # print  p_labels, p_acc, p_vals
        return  p_labels, p_acc, p_vals
    def calc(self,g1,*args):
        """ takes an unlimited number of grids as inputs and
            produces a new grid with the result of the model 
        """
        if(self.model==None):
            return None
        g=[g1]                   # list of used grids
        gout=grid.copy_grid(g1)  # build an output grid
        nrows,ncols=gout.size()  # store the size of the output
        for ar in args:
            g.append(ar)
        res=self.model.get_decfun()
        w=np.transpose(res[0])
        b=res[1]
        inp=np.zeros(len(g))
        for i in xrange(nrows):
            for j in xrange(ncols):
                if(gout.get(i,j)==gout.get_nodata()):
                    continue
                for k in range(len(g)):
                    if(g[k].get(i,j)==g[k].get_nodata()):
                        gout.set(i,j,gout.get_nodata())
                        break
                    inp[k]=g[k].get(i,j)
                gout.set(i,j,np.dot(w,inp)+b)
        return gout


