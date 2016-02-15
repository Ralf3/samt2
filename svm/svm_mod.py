#!/usr/bin/env python
"""
# -*- coding: utf-8 -*-  
"""
import numpy as np
# import svm as sl
import svmutil as su
import time
import sys
import re
import os
sys.path.append('../')
import grid

class svm(object):
    """
    defines an object oriented svm modul based on libsvm
    -s svm_type : set type of SVM (default 0)
        0 -- C-SVC              (multi-class classification)
        1 -- nu-SVC             (multi-class classification)
        2 -- one-class SVM
        3 -- epsilon-SVR        (regression)
        4 -- nu-SVR             (regression)
    -t kernel_type : set type of kernel function (default 2)
        0 -- linear: u'*v
        1 -- polynomial: (gamma*u'*v + coef0)^degree
        2 -- radial basis function: exp(-gamma*|u-v|^2)
        3 -- sigmoid: tanh(gamma*u'*v + coef0)
        4 -- precomputed kernel (kernel values in training_set_file)
    -d degree : set degree in kernel function (default 3)
    -g gamma : set gamma in kernel function (default 1/num_features)
    -r coef0 : set coef0 in kernel function (default 0)
    -c cost : set the parameter C of C-SVC, epsilon-SVR, and nu-SVR (default 1)
    -n nu : set the parameter nu of nu-SVC,
            one-class SVM, and nu-SVR (default 0.5)
    -p epsilon : set the epsilon in loss function of epsilon-SVR (default 0.1)
    -m cachesize : set cache memory size in MB (default 100)
    -e epsilon : set tolerance of termination criterion (default 0.001)
    -h shrinking : whether to use the shrinking heuristics, 0 or 1 (default 1)
    -b probability_estimates :
       whether to train a SVC or SVR model for probability estimates,
       0 or 1 (default 0)
    -wi weight : set the parameter C of class i to weight*C, for C-SVC
        (default 1)
    -v n: n-fold cross validation mode
    -q : quiet mode (no outputs)
    """
    def __init__(self):
        self.model=None  # start with empty model
        self.type=0      # 0:C-SVC,nu-SVC,one-class,epsilon-SVR,nu-SVR
        self.kernel=0    # 0:linear,polynomial,radial basis,sigmoid,precomputed
        self.degree=3    # degree
        self.gamma=0.5   # 1/len(self.names) #
        self.coef0=0     # coef0 in kerne function
        self.c=1         # cost factor
        self.nu=0.5      # nu of nu-SVC, one-class SVM, and nu-SVR
        self.eps=0.001   # tolerance of termination criterion
        self.p=0.1       # epsilon in loss function of epsilon-SVR
        self.prob=0      # whether to train a SVC or SVR model for prob. est.
        self.weight=1    # weight*C, for C-SVC
        self.q=0         # quiet mode (no outputs) default no
        self.v=0         # -v n: n-fold cross validation mode
        self.names=None  # define the name list
        return None
    def set_names(self,name1,*args):
        """ set the names for the inputs 1,2,3 """
        self.names=[name1]  # collect the names of the inputs
        for ar in args:
            self.names.append(ar)
        self.gamma= 1.0/len(self.names) #
        return True
    # svm specific parameter with checking
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self,nt):
        if(nt in [0,1,2,3,4]):
            self._type=nt
        else:
            print 'warning: type must be in [0,1,2,3,4]'
    @property
    def kernel(self):
        return self._kernel
    @kernel.setter
    def kernel(self,nk):
        if(nk in [0,1,2,3,4]):
            self._kernel=nk
        else:
            print 'warning: kernel must be in [0,1,2,3,4]'
    # read/write define model
    def read_model(self,filename):
        """ read a model an overwrites the old one """
        try:
            self.model=su.svm_load_model(filename)
        except IOError:
            print("Error in reading file: ", filename)
            return False
        m=re.search("(.*)\.(svm)",filename)   # read the names from npy
        basename=m.group(1)
        try:
            self.names=np.load(basename+".npy")
        except IOError:
            self.names=['x1','x2','x3']
        return True
    def write_model(self,filename):
        """ store a model and the names """
        if(self.model!=None):
            su.svm_save_model(filename,self.model)
            m=re.search("(.*)\.(svm)",filename)   # write the names to npy
            basename=m.group(1)
            np.save(basename,self.names)
            return True
        return False
    # definition and training are combined; the result of a training
    # procedure is a model which can be stored and loaded
    def train(self,x,y):
        """
        training using y=list,x=dict
        parameter = string of parameters
        """
        prob=su.svm_problem(y,x)
        para=""
        para+= "-s %d -t %d -d %d -g %f -r %f -c %f -n %f -p %f -e %f -b %d" %\
            (
                self.type,
                self.kernel,
                self.degree,
                self.gamma,
                self.coef0,
                self.c,
                self.nu,
                self.p,
                self.eps,
                self.prob
            )
        if(self.v!=0):
            para+=" -v %d" % self.v
        if(self.q!=0):
            para+= " -q"
        print para
        para1=su.svm_parameter(para)
        self.model=su.svm_train(prob,para1)
        return True
    def evaluation(self,ty,pv):
        """
        ty: a list of true values.
        pv: a list of predict values.    
        calculates the
            ACC: accuracy.
            MSE: mean squared error.
            SCC: squared correlation coefficient.
        """
        return su.evaluations(ty, pv)
    def predict(self,x,y=None):
        """
        y: a list/tuple of l true labels (type must be int/double). It is used
           for calculating the accuracy. Use [0]*len(x) if true labels are
           unvailable.

        x: a list/tuple of l predicting instances. The feature vector of
           each predicting instance is an instance of list/tuple or dictionary.

        predicting_options: a string of predicting options in the same
        format as that of LIBSVM.

        model: an svm_model instance.

        p_labels: a list of predicted labels

        p_acc: a tuple including accuracy (for classification), mean
               squared error, and squared correlation coefficient (for
               regression).

        p_vals: a list of decision values or probability estimates (if '-b 1'
            is specified). If k is the number of classes in training data,
            for decision values, each element includes results of predicting
            k(k-1)/2 binary-class SVMs. For classification, k = 1 is a
            special case. Decision value [+1] is returned for each testing
            instance, instead of an empty list.
            For probabilities, each element contains k values indicating
            the probability that the testing instance is in each class.
            Note that the order of classes is the same as the 'model.label'
            field in the model structure.
       
        """
        if(y==None):
            y=[0]*len(x)
        p_labels, p_acc, p_vals = su.svm_predict(y, x, self.model)
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
        inp=np.zeros(len(g))
        inp=inp.tolist()
        for i in xrange(nrows):
            for j in xrange(ncols):
                if(gout.get(i,j)==gout.get_nodata()):
                    continue
                for k in range(len(g)):
                    if(g[k].get(i,j)==g[k].get_nodata()):
                        gout.set(i,j,gout.get_nodata())
                        break
                    inp[k]=g[k].get(i,j)
                inp1=[inp]
                l,acc,val=su.svm_predict([0]*len(inp1),inp1,self.model)
                gout.set(i,j,val[0][0])
        return gout


