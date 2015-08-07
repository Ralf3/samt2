#!/usr/bin/env python
import sys
# sys.path.append('os.environ["SAMTHOME2"]+"/src/grid"')
sys.path.append('/home/ralf/master/samt2')
import grid as samt2
import numpy as np
cimport numpy as np
import nlopt
import pylab as plt

DTYPE = np.float32
ctypedef np.float32_t DTYPE_t
ctypedef np.int_t ITYPE_t

# some constants for membership
cdef int DREIECK=0
cdef int TRAPEZ=1
cdef int LEFT=2
cdef int RIGHT=3
# fuzzy controls
cdef int FUZZYMIN=0
cdef int FUZZYMUL=1
cdef int FUZZYTRAIN=2
# state of parser for read_model
cdef int INPUT=1
cdef int OUTPUT=2
cdef int RULE=3

cdef class member:
    """ Central class for Pyfuzzy to implement the membership functions:
        left, triangular,trapeze,right
        has a flag
        has a name
    """
    cdef float lu
    cdef float lo
    cdef float ro
    cdef float ru
    cdef int   flag
    cdef bytes name
    def __init__(self,name, flag1, para):
        self.name=name
        if(flag1==LEFT):
            self.lu=-9999
            self.lo=-9999
            self.ro=para[0]
            self.ru=para[1]
            self.flag=LEFT
            return
        if(flag1==RIGHT):
            self.lu=para[0]
            self.lo=para[1]
            self.ro=-9999
            self.ru=-9999
            self.flag=RIGHT
            return
        if(flag1==TRAPEZ):
            if(para[0]>para[1] or para[1]>para[2] or para[2]>para[3]):
                print "error in member!"
                print "x1=", para[0], " x2=", para[1], " x3=", para[2],
                print " x4=", para[3], "not x1>x2>x3>x4"
                sys.exit()
            self.lu=para[0]
            self.lo=para[1]
            self.ro=para[2]
            self.ru=para[3]
            self.flag=TRAPEZ
            return
        if(flag1==DREIECK):
            if(para[0]>para[1] or para[1]>para[2]):
                print "error in member!"
                print "x1=", para[0], " x2=", para[1], " x3=", para[2],
                print "not x1>x2>x3"
                sys.exit()
            self.lu=para[0]
            self.lo=para[1]
            self.ro=para[1]
            self.ru=para[2]
            self.flag=DREIECK
            return
    def get_flag(self):
        return self.flag
    def get_lo(self):
        return self.lo
    def get_lu(self):
        return self.lu
    def get_ro(self):
        return self.ro
    def get_ru(self):
        return self.ru
    def get_name(self):
        return self.name
    def get(self, float x):
        if(self.flag==DREIECK):
            if(x<=self.lu):
                return 0.0
            if(x>=self.ru):
                return 0.0
            if(x>self.lu and x<=self.lo):
                return (x-self.lu)/(self.lo-self.lu)
            return (self.ru-x)/(self.ru-self.ro)
        if(self.flag==TRAPEZ):
            if(x<=self.lu):
                return 0.0
            if(x>=self.ru):
                return 0.0
            if(x>=self.lo and x<=self.ro):
                return 1.0
            if(x>self.lu and x<self.lo):
                return (x-self.lu)/(self.lo-self.lu)
            return (self.ru-x)/(self.ru-self.ro)
        if(self.flag==LEFT):
            if(x<=self.ro):
                return 1.0
            if(x>=self.ru):
                return 0.0
            return (self.ru-x)/(self.ru-self.ro)
        if(self.flag==RIGHT):
            if(x>=self.lo):
                return 1.0
            if(x<=self.lu):
                return 0.0
            return (x-self.lu)/(self.lo-self.lu)

class input:
    """ Collects the members for a input int the list member
        has the mu list for the input
        has a name
    """
    def __init__(self,name):
        self.member=[]
        self.mu=[]
        self.name=name
        m=None
    def set_member(self,name,flag,para):
        # print "set_member:" ,name, flag, para
        if(flag=='left'):
            mb=member(name,LEFT,para)
        if(flag=='trapez' or flag=='trapeze'):
            mb=member(name,TRAPEZ,para)
        if(flag=='triangular'):
            mb=member(name,DREIECK,para)
        if(flag=='right'):
            mb=member(name,RIGHT,para)
        self.member.append(mb)
        self.mu.append(0.0)
    def get(self,k,float x):
        return self.member[k].get(x)
    def get_name(self,int k):
        return self.member[k].get_name()
    def calc(self,float x):
        for i in range(len(self.member)):
            self.mu[i]=self.member[i].get(x)
        return
    def get_mu(self,int i):
        return self.mu[i]
    def get_len(self):
        return len(self.member)
    def get_member(self,int i):
        return self.member[i]
    def get_n(self):
        return self.name
 
cdef class output:
    """ Collects the output which are singletons
        has val
        has mu
        has name
    """
    cdef bytes name
    cdef float val
    cdef float mu 
    def __init__(self, bytes  name, float val):
        self.name=name
        self.val=val
        self.mu=0.0
    def get_name(self):
        return self.name
    def getv(self):
        return self.val
    def setv(self,x):
        self.val=x
        return
    def getm(self):
        return self.mu
    def setm(self,x):
        self.mu=x
        return
    
cdef class rule:
    """ Evaluates a rules of the fuzzy system
        codes the inputs and outputs with int
        has a cf
    """
    cdef int a      # input 1
    cdef int b      # input 2 or 0
    cdef int c      # input 3 or 0
    cdef int y1     # output
    cdef float cf   # cf value
    cdef int inpn   # number of inputs
    cdef float mu   # membershipfunction
    def __init__(self,para):
        if(len(para)==3):  # only one input
            self.a=para[0]
            self.b=0
            self.c=0
            self.y1=para[1]
            self.cf=para[2]
            self.inpn=1
        if(len(para)==4):  # two inputs
            self.a=para[0]
            self.b=para[1]
            self.c=0
            self.y1=para[2]
            self.cf=para[3]
            self.inpn=2
        if(len(para)==5):  # three inputs
            self.a=para[0]
            self.b=para[1]
            self.c=para[2]
            self.y1=para[3]
            self.cf=para[4]
            self.inpn=3
    def calc(self,inv,flag):  # inv list of inputs
        if(flag==FUZZYMUL):
            if(len(inv)==3):
                self.mu=inv[0].get_mu(self.a)*inv[1].get_mu(self.b)\
                    *inv[2].get_mu(self.c)*self.cf
                return
            if(len(inv)==2):
                self.mu=inv[0].get_mu(self.a)*inv[1].get_mu(self.b)*self.cf
                return
            if(len(inv)==1):
                self.mu=inv[0].get_mu(self.a)*self.cf
                return
        if(flag==FUZZYMIN):
            if(len(inv)==3):
                if(inv[0].get_mu(self.a)>inv[1].get_mu(self.b)):
                    self.mu=inv[1].get_mu(self.b)
                else:
                    self.mu=inv[0].get_mu(self.a)
                if(self.mu>inv[2].get_mu(self.c)):
                    self.mu=inv[2].get_mu(self.c)
                self.mu*=self.cf
                return
            if(len(inv)==2):
                if(inv[0].get_mu(self.a)>inv[1].get_mu(self.b)):
                    self.mu=inv[1].get_mu(self.b)
                else:
                    self.mu=inv[0].get_mu(self.a)
                self.mu*=self.cf
                return
            if(len(inv)==1):
                self.mu=inv[0].get_mu(self.a)*self.cf
                return
        if(flag==FUZZYTRAIN):
            if(len(inv)==3):
                mu=inv[0].get_mu(self.a)*inv[1].get_mu(self.b)\
                    *inv[2].get_mu(self.c)
                return mu
            if(len(inv)==2):
                mu=inv[0].get_mu(self.a)*inv[1].get_mu(self.b)
                return mu
            if(len(inv)==1):
                mu=inv[0].get_mu(self.a)
                return mu
    def get_rule(self):
        """ returns a (i1,[i2],[i3], o, cf) """
        if(self.inpn==1):
            return (self.a, self.y1,self.cf)
        if(self.inpn==2):
            return (self.a, self.b, self.y1,self.cf)
        if(self.inpn==3):
            return (self.a, self.b, self.c, self.y1,self.cf)
    def geto(self):
        return self.y1
    def seto(self,y1):
        self.y1=y1
        return 
    def getm(self):
        return self.mu
    def get_cf(self):
        return self.cf
    def set_cf(self, x):
        self.cf=x
        return

class fuzzy:
    """ Main class of Pyfuzzy
        operates over inputs, outputs, rules
        has list of inputs:  inputs
        has list of outputs: outputst
        has list of rules:   rules
    """
    
    def __init__(self,flag=FUZZYMUL):
        self.flag=flag
        self.inputs=[]       # store the input
        self.outputs=[]      # store the outputs
        self.rules=[]        # store the rules
        self.ruleList=[]     # debug 
        self.muList=[]       # debug
        self.outputList=[]   # debug
        self.X=None          # empty training data
        self.Y=None          # empty training data
        self.d0=[]           # difference between the outputs
        self.w=0             # rsme weight before training
        self.res=None
        self.name=None       # name of the model
        return
    def set_name(self,name):
        self.name=name
    def add_input(self,inp):
        self.inputs.append(inp)
        return
    def get_number_of_inputs(self):
        return len(self.inputs)
    def get_input_name(self,int i):
        if(i<len(self.inputs)):
            return self.inputs[i].name
        return None
    def get_min_input(self,int i):
        if(i>=len(self.inputs)):
            return None
        lo=self.inputs[i].member[0].get_lo()
        if(lo!=-9999):
            return lo
        return self.inputs[i].member[0].get_ro()
    def get_max_input(self,int i):
        if(i>=len(self.inputs)):
            return None
        sel=len(self.inputs[i].member)
        ro=self.inputs[i].member[sel-1].get_ro()
        if(ro!=-9999):
            return ro
        return self.inputs[i].member[sel-1].get_lo()
    def get_output_name(self):
        return 'Output'
    def add_output(self,out):
        self.outputs.append(out)
        return
    def add_rule(self,rule):
        self.rules.append(rule)
        return
    def set_flag(self,int flag):
        self.flag=flag
        return
    def get_len_output(self):
        return len(self.outputs)
    def set_output(self,int i,float val):
        if(len(self.outputs)>i):
            self.outputs[i].setv(val)
            return
    def get_output(self,int i):
        return self.outputs[i].getv()
    def calc1(self,float x):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        self.inputs[0].calc(x)   # calc the membership of input 1
        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
        for i in range(len(self.outputs)):
            if(self.outputs[i].getm()>0):
                su1+=self.outputs[i].getm()*self.outputs[i].getv()
                tmu+=self.outputs[i].getm()
                self.outputs[i].setm(0.0)
        if(tmu==0):
            return -9999
        return su1/tmu
    # same as calc1 but returns the membership of the outputs
    def calc1_r(self,float x):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        # define the self.res
        if(self.res==None):
            self.res=np.zeros(len(self.outputs))
        self.inputs[0].calc(x)   # calc the membership of input 1
        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
            self.outputs[self.rules[i].geto()].setm(0.0)
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
        for i in range(len(self.outputs)):
            self.res[i]=self.outputs[i].getm()
            # print i, res[i],self.outputs[i].getm()
            self.outputs[i].setm(0.0)
        return self.res
    # same as calc1 but with debugging
    def get_ruleList(self):
        return self.ruleList
    def get_muList(self):
        return self.muList
    def get_outputList(self):
        return self.outputList
    def calct1(self,float x):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        del self.ruleList[:]     # empty the debug
        del self.muList[:]       # empty the debug
        del self.outputList[:]   # empty the debug
        self.inputs[0].calc(x)   # calc the membership of input 1
        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
            
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
        for i in range(len(self.rules)): # debug part
             if(np.around(self.outputs[self.rules[i].geto()].getm(),5)==
                np.around(self.rules[i].getm(),5)
                and
                self.rules[i].getm()>0.001):
                self.ruleList.append(i)    # append the rule number
                self.muList.append(self.rules[i].getm()) # add the mu
                self.outputList.append(self.outputs[self.rules[i].geto()].getv())
        for i in range(len(self.outputs)):
            if(self.outputs[i].getm()>0):
                su1+=self.outputs[i].getm()*self.outputs[i].getv()
                tmu+=self.outputs[i].getm()
                self.outputs[i].setm(0.0)
        if(tmu==0):
            return -9999
        return su1/tmu
    def calc2(self,float x1,float x2):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        self.inputs[0].calc(x1)   # calc the membership of input 1
        self.inputs[1].calc(x2)   # calc the membership of input 2
        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
            
            # print i,self.rules[i].getm()
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
        for i in range(len(self.outputs)):
            if(self.outputs[i].getm()>0):
                su1+=self.outputs[i].getm()*self.outputs[i].getv()
                tmu+=self.outputs[i].getm()
                self.outputs[i].setm(0.0)
        if(tmu==0):
            return -9999
        return su1/tmu
    # same as calc2 but returns the membership of the outputs
    def calc2_r(self, float x1, float x2):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        # define the self.res
        if(self.res==None):
            self.res=np.zeros(len(self.outputs))
        self.inputs[0].calc(x1)   # calc the membership of input 1
        self.inputs[1].calc(x2)   # calc the membership of input 2
        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
            
            # print i,self.rules[i].getm()
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
        for i in range(len(self.outputs)):
            self.res[i]=self.outputs[i].getm()
            self.outputs[i].setm(0.0)
        return self.res
    # same as calc2 but with debugging
    def calct2(self,float x1,float x2):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        del self.ruleList[:]     # empty the debug
        del self.muList[:]       # empty the debug
        del self.outputList[:]   # empty the debug
        self.inputs[0].calc(x1)   # calc the membership of input 1
        self.inputs[1].calc(x2)   # calc the membership of input 2
        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
            
            # print i,self.rules[i].getm()
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
        for i in range(len(self.rules)): # debug part
            if(np.around(self.outputs[self.rules[i].geto()].getm(),5)==
                np.around(self.rules[i].getm(),5)
                and
                self.rules[i].getm()>0.001):
                self.ruleList.append(i)    # append the rule number
                self.muList.append(self.rules[i].getm()) # add the mu
                self.outputList.append(self.outputs[self.rules[i].geto()].getv())
        for i in range(len(self.outputs)):
            if(self.outputs[i].getm()>0):
                su1+=self.outputs[i].getm()*self.outputs[i].getv()
                tmu+=self.outputs[i].getm()
                self.outputs[i].setm(0.0)
        if(tmu==0):
            return -9999
        return su1/tmu  
    def calc3(self,float x1,float x2,float x3):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        self.inputs[0].calc(x1)   # calc the membership of input 1
        self.inputs[1].calc(x2)   # calc the membership of input 2
        self.inputs[2].calc(x3)   # calc the membership of input 3
        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
            
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
        for i in range(len(self.outputs)):
            if(self.outputs[i].getm()>0):
                su1+=self.outputs[i].getm()*self.outputs[i].getv()
                tmu+=self.outputs[i].getm()
                self.outputs[i].setm(0.0)
        if(tmu==0):
            return -9999
        return su1/tmu
    #same as calc2 but returns the membership of the outputs
    def calc3_r(self,float x1,float x2,float x3):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        del self.ruleList[:]     # empty the debug
        del self.muList[:]       # empty the debug
        del self.outputList[:]   # empty the debug
        self.inputs[0].calc(x1)   # calc the membership of input 1
        self.inputs[1].calc(x2)   # calc the membership of input 2
        self.inputs[2].calc(x3)   # calc the membership of input 3
        # define the self.res
        if(self.res==None):
            self.res=np.zeros(len(self.outputs))

        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
            
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
                # print 'calct3:', i, self.rules[i].getm()
        for i in range(len(self.rules)): # debug part
            if(np.around(self.outputs[self.rules[i].geto()].getm(),5)==
                np.around(self.rules[i].getm(),5)
                and
                self.rules[i].getm()>0.001):
                self.ruleList.append(i)    # append the rule number
                self.muList.append(self.rules[i].getm()) # add the mu
                self.outputList.append(self.outputs[self.rules[i].geto()].getv())
        for i in range(len(self.outputs)):
            self.res[i]=self.outputs[i].getm()
            self.outputs[i].setm(0.0)
        return self.res
    # same as calc3 but with debugging
    def calct3(self,float x1,float x2,float x3):
        cdef float su1=0.0
        cdef float tmu=0.0
        cdef int i
        del self.ruleList[:]     # empty the debug
        del self.muList[:]       # empty the debug
        del self.outputList[:]   # empty the debug
        self.inputs[0].calc(x1)   # calc the membership of input 1
        self.inputs[1].calc(x2)   # calc the membership of input 2
        self.inputs[2].calc(x3)   # calc the membership of input 3
        for i in range(len(self.rules)): # calc the membership of all rules
            self.rules[i].calc(self.inputs,self.flag)
            
        for i in range(len(self.rules)): # set the membership to the outputs
            if(self.outputs[self.rules[i].geto()].getm()<self.rules[i].getm()):
                self.outputs[self.rules[i].geto()].setm(self.rules[i].getm())
                # print 'calct3:', i, self.rules[i].getm()
        for i in range(len(self.rules)): # debug part
            if(np.around(self.outputs[self.rules[i].geto()].getm(),5)==
                np.around(self.rules[i].getm(),5)
                and
                self.rules[i].getm()>0.001):
                self.ruleList.append(i)    # append the rule number
                self.muList.append(self.rules[i].getm()) # add the mu
                self.outputList.append(self.outputs[self.rules[i].geto()].getv())
        for i in range(len(self.outputs)):
            if(self.outputs[i].getm()>0):
                su1+=self.outputs[i].getm()*self.outputs[i].getv()
                tmu+=self.outputs[i].getm()
                self.outputs[i].setm(0.0)
        if(tmu==0):
            return -9999
        return su1/tmu
    # grip operations based on samt2
    def grid_calc1(self, g1):
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef np.ndarray[DTYPE_t,ndim=2] matx=g1.get_matc()
        cdef int ii,jj
        (ii,jj)=g1.size()
        for i in range(ii):
            for j in range(jj):
                if(int(mat1[i,j])!=g1.get_nodata()):
                    matx[i,j]=self.calc1(mat1[i,j])
        gx=samt2.grid()
        (nrows,ncols,x,y,csize,nodata)=g1.get_header()
        gx.set_header(nrows,ncols,x,y,csize,nodata)
        gx.set_mat(matx)
        return gx
    def grid_calc2(self, g1,g2):
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef np.ndarray[DTYPE_t,ndim=2] mat2=g2.get_matp()
        cdef np.ndarray[DTYPE_t,ndim=2] matx=g1.get_matc()
        cdef int ii1,jj1, ii2,jj2
        (ii1,jj1)=g1.size()
        (ii2,jj2)=g2.size()
        if(ii1!=ii2 or jj1!=jj2):
            return None
        for i in range(ii1):
            for j in range(jj1):
                if(int(mat1[i,j])==g1.get_nodata() or
                   int(mat2[i,j])==g2.get_nodata()):
                    matx[i,j]=g1.get_nodata()
                else:
                    matx[i,j]=self.calc2(mat1[i,j],mat2[i,j])
        gx=samt2.grid()
        (nrows,ncols,x,y,csize,nodata)=g1.get_header()
        gx.set_header(nrows,ncols,x,y,csize,nodata)
        gx.set_mat(matx)
        return gx
    def grid_calc3(self, g1,g2,g3):
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef np.ndarray[DTYPE_t,ndim=2] mat2=g2.get_matp()
        cdef np.ndarray[DTYPE_t,ndim=2] mat3=g3.get_matp()
        cdef np.ndarray[DTYPE_t,ndim=2] matx=g1.get_matc()
        cdef int ii1,jj1, ii2,jj2,ii3,jj3
        (ii1,jj1)=g1.size()
        (ii2,jj2)=g2.size()
        (ii3,jj3)=g3.size()
        if(ii1!=ii2 or jj1!=jj2 or ii1!=ii3 or jj1!=jj3):
            return None
        for i in range(ii1):
            for j in range(jj1):
                if(int(mat1[i,j])==g1.get_nodata() or
                   int(mat2[i,j])==g2.get_nodata() or
                   int(mat3[i,j])==g3.get_nodata()):
                    matx[i,j]=g1.get_nodata()
                else:
                    matx[i,j]=self.calc3(mat1[i,j],mat2[i,j],mat3[i,j])
        gx=samt2.grid()
        (nrows,ncols,x,y,csize,nodata)=g1.get_header()
        gx.set_header(nrows,ncols,x,y,csize,nodata)
        gx.set_mat(matx)
        return gx

    # genral function to read training data for ruletraining and
    # for output adaptation
    def read_training_data(self,filename,header=0,sep=' '):
        """ reads a table of training data with header lines
            and a separator in a numpy array
            The table consists of x1,y or x1,x2,y or x1,x2,x3,y
        """
        ts=np.loadtxt(filename, skiprows=header,delimiter=sep)
        if(ts.shape[1]!=len(self.inputs)+1):
            print "error in read_trainig_data:", ts.shape, "!=",
            print len(self.inputs)+1
            return False
        sl=len(self.inputs)
        self.X=ts[:,0:sl]
        self.Y=ts[:,sl]
        return self.X, self.Y
    def get_rsme(self):
        """ takes the training data and calulates the rmse
            inherits from myfunc
        """
        cdef int i
        cdef float y, error=0.0, rsme=0.0, reg=0.0
        if(self.X==None or self.Y==None):
            print 'error in get_rsme: X or Y are not defined'
            return -9999.0
        # evaluate the fuzzy model using training data
        for i in range(self.X.shape[0]):
            if(self.X.shape[1]==1):
                y=self.calc1(self.X[i,0])
            if(self.X.shape[1]==2):
                y=self.calc2(self.X[i,0],self.X[i,1])
            if(self.X.shape[1]==3):
                y=self.calc3(self.X[i,0],self.X[i,1],self.X[i,2])
            error+=(self.Y[i]-y)**2
        rsme=np.sqrt(error)/self.X.shape[0]
        return rsme
        
    # help function for output adaptation
    def myfunc(self,x,grad):
        """ this is the fit function for opimization
            it consists of the RSME part for accuracy of training
            and the regularization part to avoid overlapping of yi
        """
        cdef int i
        cdef float y, error=0.0, rsme=0.0, reg=0.0
        # print 'len(x):',len(x),'x',x
        for i in range(len(x)-1):
            if(x[i]>=x[i+1]):     # check an overlaypping
                return np.inf     # punish it
        # set the x as output
        for i in range(len(x)):
            self.set_output(i,x[i])
        # evaluate the fuzzy model using training data
        for i in range(self.X.shape[0]):
            if(self.X.shape[1]==1):
                y=self.calc1(self.X[i,0])
            if(self.X.shape[1]==2):
                y=self.calc2(self.X[i,0],self.X[i,1])
            if(self.X.shape[1]==3):
                y=self.calc3(self.X[i,0],self.X[i,1],self.X[i,2])
            error+=(self.Y[i]-y)**2
        rsme=np.sqrt(error)/self.X.shape[0]
        if(self.w==0):
            self.w=rsme/(len(x)*100.0)
            for i in range(1,len(x)):
                self.d0.append(x[i]-x[i-1])
        # add the regularization
        for i in range(1,len(x)):
            reg+=1.0/((x[i]-x[i-1])**2/self.d0[i-1]+0.01)
        # print 'rsme:',rsme,'reg:',reg
        return rsme+self.w*reg

    # write routine to store modified models
    def store_model(self, name):
        """ writes a model to the harddisk
            extension  .fis will be added
        """
        file=open(name+'.fis','w')
        # print out the inputs and the members for each input
        for inp in self.inputs:
            s="input %s %d\n" % (inp.get_n(), inp.get_len())
            file.write(s)
            for j in range(inp.get_len()):
                mem = inp.get_member(j)
                if(mem.get_flag()==LEFT):
                    s="member %s left\n" % mem.get_name()
                    file.write(s)
                    s="%f %f\n" % (mem.get_ro(),mem.get_ru())
                    file.write(s)
                if(mem.get_flag()==RIGHT):
                    s="member %s right\n" % mem.get_name()
                    file.write(s)
                    s="%f %f\n" % (mem.get_lu(),mem.get_lo())
                    file.write(s)
                if(mem.get_flag()==TRAPEZ):
                    s="member %s trapez\n" % mem.get_name()
                    file.write(s)
                    s="%f %f %f %f\n" % (mem.get_lu(),mem.get_lo(),
                                         mem.get_ro(),mem.get_ru())
                    file.write(s)
                if(mem.get_flag()==DREIECK):
                    s="member %s triangular\n" % mem.get_name()
                    file.write(s)
                    s="%f %f %f\n" % (mem.get_lu(),mem.get_lo(),mem.get_ru())
                    file.write(s)
        # print out the output and their values
        s="outputs Output %d\n" % len(self.outputs)
        file.write(s)
        for out in self.outputs:
            s="output %s %f\n" % (out.get_name(),out.getv())
            file.write(s)
        # print the rules as a table
        s="rules %d\n" % len(self.rules)
        file.write(s)
        for rule in self.rules:
            if(len(self.inputs)==1):
                s="%d %d %f\n" % (rule.get_rule())
            if(len(self.inputs)==2):
                s="%d %d %d %f\n" % (rule.get_rule())
            if(len(self.inputs)==3):
                s="%d %d %d %d %f\n" % (rule.get_rule())
            file.write(s)
        file.close()
        return True

    # rule training as replacement of C++ code in the fuzzy generator
    def train_rules(self, patterns, targets, alpha=0.75):
        """ fuzzy rule training:
            starts with a fuzzy model and set all cf=0
            and remove all outputs from the rules
            
            iterates over all rule inputs:
               iterates over all patterns (targets):
                  select all rules > alpha 

               determines the mean of all matching patterns/targets
                   using: tsum/musum
            
               selects the ouput with the minimal distance to the targets
               
               determines the cf values:
                  cf=musum/rulecount
               
            alpha is used as a cut off value to eleminate small mu
        """   
        cdef int i,j, rulecount, selector, ninputs
        cdef float musum, tsum, delta, mu, outputval, a=alpha
        cdef np.ndarray[np.float_t,ndim=2] pat=np.array(patterns)
        cdef np.ndarray[np.float_t,ndim=1] tar=np.array(targets)
        # check if target and pattern have the same size
        if(pat.shape[0]!=tar.shape[0]):
            print "error in train_rules: target", tar.shape[0],
            print " and pattern", pat.shape[1]
            print "do not match!"
            return False
        # check if the pattern do match with the fuzzy model
        if(len(self.inputs)!=pat.shape[1]):
            print "error in train_rules: pattern:",pat.shape[0]
            print "\tdo not match with the defined inputs:", len(self.inputs)
            return False
        ninputs=pat.shape[1]
        # remove the outputs from the rules
        for rule in self.rules:
            rule.set_cf(0.0)
            rule.seto(0)
        # iterate over all rules
        for rule in self.rules:
            musum=0.0
            tsum=0.0
            rulecount=0
            for i in range(tar.shape[0]):
                self.inputs[0].calc(pat[i,0])
                if(ninputs==2 or ninputs==3):
                    self.inputs[1].calc(pat[i,1])
                if(ninputs==3):
                    self.inputs[2].calc(pat[i,2])
                mu=rule.calc(self.inputs,flag=FUZZYTRAIN)
                # print i,mu,pat[i,:],tar[i]
                if(mu>a):  # > alpha
                    tsum+=tar[i]*mu
                    musum+=mu
                    rulecount+=1
            if(rulecount>0):  # did we find a matching rule?
                rule.set_cf(musum/float(rulecount))
                delta=np.finfo(np.float64).max
                tsum=tsum/musum
                for s in range(len(self.outputs)):
                    if(np.fabs(self.outputs[s].getv()-tsum)<delta):
                        output_val=self.outputs[s].getv()
                        delta=np.fabs(self.outputs[s].getv()-tsum)
                        selector=s
                rule.seto(selector)

        return True
    
    def show_model(self, tag1=2, default1=-9999):
        """ visualize a fuzzy model up to three inputs
            - for a one dimensional model it uses the range of the input
              and plots it against the model output
            - for a two dimensional model it uses the range of both inputs
              and plots a two dimenional colored picture of it.
            - three inputs are more difficult:
              it uses the input with the 1 in the 'tag1:  0,1,2'
              for example"and uses the given default1 value for it,
              the plot it like this for the two dimensional case
        """
        cdef int i,j, res=100 # resolution of the plots
        cdef int sel1,sel2,seld # for three inputs select two of them + default
        cdef int ninputs=len(self.inputs)
        cdef float a,b,c      # the range for the inputs
        cdef np.ndarray[np.float_t,ndim=1] y=np.zeros(res)
        cdef np.ndarray[np.float_t,ndim=2] z=np.zeros((res,res))

        cdef np.ndarray[np.float_t,ndim=1] r1=None
        cdef np.ndarray[np.float_t,ndim=1] r2=None
        cdef np.ndarray[np.float_t,ndim=2] X=None
        cdef np.ndarray[np.float_t,ndim=2] Y=None
        if(ninputs==1):
            # define the paramters for input1
            a=self.inputs[0].get_member(0).get_lu()
            if(np.isclose(a,-9999.0)):
                a=self.inputs[0].get_member(0).get_ro()
            b=self.inputs[0].get_member(-1).get_ru()
            if(np.isclose(b,-9999.0)):
                b=self.inputs[0].get_member(-1).get_lo()
            # print "a0:", a, "b0:",b
            if(a>=b):  # check the input range
                return False
            r1=np.linspace(a,b,res)
            # plot the on dimensional model simulation
            for i in np.arange(res):
                y[i]=self.calc1(r1[i])
            plt.plot(r1,y)
            plt.grid(True)
            plt.xlabel(self.inputs[0].get_n())
            plt.ylabel('y')
            plt.title('plot: ' + self.name)
            plt.show()
            return True
        if(ninputs==2):
            # define the paramters for input1
            a=self.inputs[0].get_member(0).get_lu()
            if(np.isclose(a,-9999.0)):
                a=self.inputs[0].get_member(0).get_ro()
            b=self.inputs[0].get_member(-1).get_ru()
            if(np.isclose(b,-9999.0)):
                b=self.inputs[0].get_member(-1).get_lo()
            #print "a0:", a, "b0:",b
            if(a>=b):  # check the input range
                return False
            r1=np.linspace(a,b,res)   
            # fill the input2
            a=self.inputs[1].get_member(0).get_lu()
            if(np.isclose(a,-9999.0)):
                a=self.inputs[1].get_member(0).get_ro()
            b=self.inputs[1].get_member(-1).get_ru()
            if(np.isclose(b,-9999.0)):
                b=self.inputs[1].get_member(-1).get_lo()
            #print "a0:", a, "b0:",b
            if(a>=b):  # check the input range
                return False
            r2=np.linspace(a,b,res)
            for i in np.arange(res):
                for j in np.arange(res): 
                    z[j,i]=self.calc2(r1[i],r2[j])
                       # contour range
            a=0.2*np.max(z)
            b=0.8*np.max(z)
            if(np.max(z)==0.0):
               a=0.2*np.min(z)
               b=0.8*np.min(z)
               
            #print 'contour:',a,b
            im = plt.imshow(z,cmap=plt.cm.RdBu,
                            extent=(r1[0],r1[-1],r2[-1],r2[0]),
                            aspect='auto') # drawing the function
            cset = plt.contour(z,
                                np.linspace(a,b,4),
                                extent=(r1[0],r1[-1],r2[0],r2[-1]),
                                linewidths=1,colors='k')
            plt.clabel(cset,inline=True,fmt='%1.3f',fontsize=10)
            plt.colorbar(im) # adding the colobar on the right
            plt.xlabel(self.inputs[0].get_n())
            plt.ylabel(self.inputs[1].get_n())
            plt.grid(True)
            plt.title('plot: ' + self.name)
            plt.show()
            return True
        if(ninputs==3):
            # define the selectors
            if(tag1==0):
                sel1=1
                sel2=2
                seld=0
            if(tag1==1):
                sel1=0
                sel2=2
                seld=1
            if(tag1==2):
                sel1=0
                sel2=1
                seld=2
            # define the ranges
            # define the paramters for input1
            a=self.inputs[sel1].get_member(0).get_lu()
            if(np.isclose(a,-9999.0)):
                a=self.inputs[sel1].get_member(0).get_ro()
            b=self.inputs[sel1].get_member(-1).get_ru()
            if(np.isclose(b,-9999.0)):
                b=self.inputs[sel1].get_member(-1).get_lo()
            #print "a0:", a, "b0:",b
            if(a>=b):  # check the input range
                return False
            r1=np.linspace(a,b,res)
            # define the paramters for input1   
            a=self.inputs[sel2].get_member(0).get_lu()
            if(np.isclose(a,-9999.0)):
                a=self.inputs[sel2].get_member(0).get_ro()
            b=self.inputs[sel2].get_member(-1).get_ru()
            if(np.isclose(b,-9999.0)):
                b=self.inputs[sel2].get_member(-1).get_lo()
            #print "a1:", a, "b1:",b
            if(a>=b):  # check the input range
                return False    
            r2=np.linspace(a,b,res)
            # the default value c is used when given or the half of the range
            if(default1!=-9999):
                c=np.float(default1)
            else:
                a=self.inputs[seld].get_member(0).get_lu()
                if(np.isclose(a,-9999.0)):
                    a=self.inputs[seld].get_member(0).get_ro()
                b=self.inputs[seld].get_member(-1).get_ru()
                if(np.isclose(b,-9999.0)):
                    b=self.inputs[seld].get_member(-1).get_lo()
                c=(b-a)/2.0    
            #print "a1:", a, "b1:",b, "c:", c
            if(a>=b):  # check the input range
                return False
            for i in np.arange(res):
                for j in np.arange(res):
                    if(tag1==2): 
                        z[j,i]=self.calc3(r1[i],r2[j],c)
                        continue
                    if(tag1==1):
                        z[j,i]=self.calc3(r1[i],c,r2[j])
                        continue
                    if(tag1==0):
                        z[j,i]=self.calc3(c,r1[i],r2[j])
                        continue
            # contour range
            a=0.2*np.max(z)
            b=0.8*np.max(z)
            if(np.max(z)==0.0):
               a=0.2*np.min(z)
               b=0.8*np.min(z)
            im = plt.imshow(z,cmap=plt.cm.RdBu,
                            extent=(r1[0],r1[-1],r2[-1],r2[0]),
                            aspect='auto') # drawing the function
            cset = plt.contour(z,
                                np.linspace(a,b,4),
                                extent=(r1[0],r1[-1],r2[0],r2[-1]),
                                linewidths=1,colors='k') 
            plt.clabel(cset,inline=True,fmt='%1.3f',fontsize=10)
            plt.colorbar(im) # adding the colobar on the right
            plt.xlabel(self.inputs[sel1].get_n())
            plt.ylabel(self.inputs[sel2].get_n())
            plt.grid(True)
            s="plot: %s %s = %3.3f" % (self.name,self.inputs[tag1].get_n(),c)
            plt.title(s)
            plt.show()
            return True

# an external function for output adaptation based on nlopt
def start_training(f):
    """ define the training parameters
    """
    opt=nlopt.opt(nlopt.GN_DIRECT_L,f.get_len_output())
    # build the boundaries
    minout=[]
    maxout=[]
    startout=[]
    for i in range(f.get_len_output()-1):
        minout.append(f.get_output(i))
    for i in range(1,f.get_len_output()):
        maxout.append(f.get_output(i))
    for i in range(f.get_len_output()):
        startout.append(f.get_output(i))
    minout.insert(0,minout[0]-(minout[1]-minout[0]))
    maxout.append(maxout[-1]+(maxout[-1]-maxout[-2]))
    print 'minout:',minout
    print 'maxout:',maxout
    print 'start:', startout
    opt.set_lower_bounds(np.array(minout))
    opt.set_upper_bounds(np.array(maxout))
    opt.set_initial_step((f.get_output(1)-f.get_output(0))/500.)
    opt.set_min_objective(f.myfunc)
    opt.set_ftol_rel((f.get_output(1)-f.get_output(0))/100000.)
    opt.set_maxtime(60)  # 60 s
    xopt=opt.optimize(np.array(startout))
    opt_val=opt.last_optimum_value()
    result=opt.last_optimize_result()
    print ' *************Result of Optimization*****************'
    print 'max:', opt_val
    print 'parameter:', xopt
    # set the best values
    for i in range(f.get_len_output()):
        f.set_output(i,xopt[i])

# read in of a model in Python code
def read_model(modelname, DEBUG=0):
    f1=fuzzy()
    try:
        f = open(modelname, 'r')
    except IOError:
        print 'error in read_model: can not open file: ', modelname
        return None
    f1.set_name(modelname.split('/')[-1])
    s=f.readline().rstrip()
    line=1
    sl=s.rsplit(' ')
    if(sl[0]!='input'):
        print "error in line:",line, 
        print "file should start with input"
        sys.exit()
    inputname=sl[1]
    members=int(sl[2])
    state=INPUT
    if(DEBUG==1):
        print line, inputname,members
    while(state==INPUT):
        ip=input(inputname)
        for i in range(members):  # collect members
            s=f.readline().rstrip()
            sl=s.rsplit(' ')
            line+=1
            mname=sl[1]
            mtag=sl[2]
            if(DEBUG==1):
                print line, 'member',mname,mtag
            s=f.readline().rstrip()
            line+=1
            sl=s.rsplit(' ')
            para=[]
            for i in sl:
                para.append(float(i))
            if(DEBUG==1):
                print line, para
            ip.set_member(mname,mtag,para)
        f1.add_input(ip)  # store the input in the fuzzy
        s=f.readline().rstrip()
        sl=s.rsplit(' ')
        line+=1
        inputname=sl[1]
        members=int(sl[2])
        if(DEBUG==1):
            print line,inputname,members
        if(sl[0]!='input'):
            state=OUTPUT
            oname=sl[1]
            omembers=int(sl[2])
    # new state OUTPUT must follow state INPUT
    for i in range(omembers):
        s=f.readline().rstrip()
        sl=s.rsplit(' ')
        line+=1
        oname=sl[1]
        oval=float(sl[2])
        if(DEBUG==1):
            print line, oname,oval
        out=output(oname,oval)
        f1.add_output(out)
    state=RULE  # state RULE must follow n outputs
    s=f.readline().rstrip()
    sl=s.rsplit(' ')
    line+=1
    rulenumbers=int(sl[1])
    if(DEBUG==1):
        print line,'rules:',rulenumbers
    for i in range(rulenumbers):
        s=f.readline().rstrip()
        sl=s.rsplit(' ')
        line+=1
        para=[]
        for i in range(len(sl)-1):
            para.append(int(sl[i]))
        para.append(float(sl[-1]))
        if(DEBUG==1):
            print line, para
        rulex=rule(para)
        f1.add_rule(rulex)
    f.close()
    return f1


