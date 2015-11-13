#!/usr/bin/env python
"""
# -*- coding: utf-8 -*-  
"""
import numpy as np
import mlpy
import time
import sys
import re
import os
sys.path.append(os.environ['SAMTHOME2']+"/src/grid")
import grid

class svm:
    """
    defines an object oriented svm modul based on mlpy
    """
    def __init__(self,name1=None,name2=None,name3=None):
        """ set the names for the inputs 1,2,3 """
        self.name=[name1,name2,name3]
        self.model=None           # start with empty model
        self.type='epsilon_svr'   # start with regression
        self.kernel='rbf'         # start with rbf kernel
        self.degree=3             # default values
        self.gamma=0.001
        self.coef=0
        self.C=1
        self.nu=0.5
        self.eps=0.001
        self.p=0.1
        self.prop=False
        self.weight={}
        return None
    def set_names(self,names):
        self.name=names
    def get_name(self,nr):
        if(nr<0 or nr>=len(self.name)):
            return None
        return self.name[nr]
    def get_names(self):
        return self.name
    # svm specific parameter
    def set_type(self,type='epsilon_svr'):
        """ c_svc, nu_svc, one_class, epsilon_svr, nu_svr """
        check=['c_svc', 'nu_svc', 'one_class', 'epsilon_svr', 'nu_svr']
        if(type in check):
            self.type=type
            return True
        return False
    def set_kernel(self,type='rbf',coef0=0, degree=3):
        """ 'linear' (uT*v), 'poly' ((gamma*uT*v + coef0)^degree),
             'rbf' (exp(-gamma*|u-v|^2)),
             'sigmoid' (tanh(gamma*uT*v + coef0))
        """
        check=['rbf','linear','poly','sigmoid']
        if(type in check):
            self.kernel=type
            self.coef=coef0     # for poly, sigmoid kernel_type
            self.degree=degree  # for poly kernel_type
            return True
        return False
    def set_gamma(self,gamma=0.001):
        """ set gamma in kernel (e.g. 1 / number of features) """
        self.gamma=gamma
        return True
    def set_C(self,C):
        """ for 'c_svc', 'epsilon_svr', 'nu_svr'
            cost of constraints violation
        """
        self.C=C
        return True
    def set_nu(self,nu):
        """ for 'nu_svc', 'one_class', 'nu_svr' """
        self.nu=nu
        return True
    def set_eps(self,eps):
        """ stopping criterion, usually 0.00001 in nu-SVC, 0.001 in others """
        self.eps=eps
        return True
    def set_p(self,p):
        """ p is the epsilon in epsilon-insensitive loss function
            of epsilon-SVM regression
        """
        self.p=p
        return True
    def set_shrinking(self,s):
        """ use the shrinking heuristics bool """
        self.s=s
        return True
    def set_prop(self,p):
        """ predict probability estimates bool """
        self.prop=p
        return True
    def set_weight(self,dictw):
        """ changes the penalty for some classes
            (if the weight for a class is not changed, it is set to 1).
            For example, to change penalty for classes 1 and 2 to 0.5 and 0.8
            respectively set weight={1:0.5, 2:0.8}
        """
        self.dictw=dictw
        return True
    # read/write define model
    def read_model(self,filename):
        """ read a model an overwrites the old one """
        try:
	    self.model=mlpy.libsvm.LibSvm.load_model(filename)
        except IOError:
	    print("Error in reading file: ", filename)
	    return False
        m=re.search("(.*)\.(svm)",filename)   # read the names from npy
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
            m=re.search("(.*)\.(svm)",filename)   # write the names to npy
            basename=m.group(1)
            np.save(basename,self.name)
            return True
        return False
    def def_model(self):
        """ define a new model using the kernel, type and parameters
        """
        if(self.model!=None):
            del self.model     # remove an old model
        if(self.type==None or self.kernel==None):
            return None
        self.model=mlpy.LibSvm(svm_type=self.type,
                               kernel_type=self.kernel,
                               degree=self.degree,
                               gamma=self.gamma,
                               coef0=self.coef,
                               nu=self.nu,
                               eps=self.eps,
                               p=self.p,
                               probability=self.prop,
                               weight=self.weight)
        return True
    # calculus
    def train(self,x,y):
        """ x 2d numpy array with n inputs, y 1d numpy array with output """
        if(self.model==None):
            return False
        self.model.learn(x,y)
    def test(self,x,y):
        """ uses a trained svm with input x and given output y
            to calculate the:
            BIAS, RSME and R2
        """
        ym=self.model.pred(x)   # output of the SVM
        BIAS=np.mean(ym-y)
        RSME=np.sqrt(np.mean((ym-y)**2))
        R2 = np.corrcoef(y, ym)[0,1]
        R2 *= R2                # R^2
        return BIAS,RSME,R2
    def calc(self,g1,g2=None,g3=None):
        """ takes up to three grids to apply the model """
        if(self.model==None):
            return None
        gout=grid.copy_grid(g1)  # build an output grid
        nrows,ncols=gout.size()   # store the size of the output
        if(g2==None and g3==None):
            a=g1.get_matc()
            x=np.c_[a.flatten()]
        if(g2!=None and g3==None):
            a=g1.get_matc()
            b=g2.get_matc()
            x=np.c_[a.flatten(),b.flatten()]
        if(g2!=None and g3!=None):
            a=g1.get_matc()
            b=g2.get_matc()
            c=g3.get_matc()
            x=np.c_[a.flatten(),b.flatten(),c.flatten()]
        y=self.model.pred(x)
        gout.set_mat(np.float32(y.reshape(nrows,ncols)))
        gout.and_grid(g1)
        return gout

# test example
def test():
    #~ #define the grids
    bd=grid.grid()
    struktur=grid.grid()
    nahr=grid.grid()
    # load the grids
    bd.read_hdf('../../hdf/schreiadler_all.h5','bd_all')
    struktur.read_hdf('../../hdf/schreiadler_all.h5','struktur')
    nahr.read_hdf('../../hdf/schreiadler_all.h5','nahr_schreiadler')
    #~ # draw a sample of a size of 2000
    X,Y=grid.sample(g1=bd,g2=struktur,g4=nahr,n=2000,filename='s_nahr.csv')
    X=np.array(X)
    Y=np.array(Y)
    print(X.shape, Y.shape)
    # define the model
    t0=time.time()
    model=svm('bd','struktur')
    model.def_model()
    # train the model
    model.train(X,Y)
    # test model
    bias,rsme,r2=model.test(X,Y)
    print('Bias=', bias, 'RSME=', rsme, 'R^2=', r2)
    # write the model
    model.write_model('bd_struk.svm')
    print('after read:', model.get_names())
    # gen the output
    out=model.calc(bd,struktur)
    print('time=',time.time()-t0)
    out.show()

#test()
