#!/usr/bin/env python
import sys
import csv
import random
# import required modules
import numpy as np
from scipy import signal
import pylab as plt

# ------------------------------------------------------------
# Some elementary functions
# ------------------------------------------------------------

def filter_nan(s,o):
    data = np.array([s,o])
    data = np.transpose(data)
    data = data[~np.isnan(data).any(1)]
    return data[:,0],data[:,1]

def pc_bias(s,o):
    s,o = filter_nan(s,o)
    return 100.0*sum(s-o)/sum(o)

def apb(s,o):
    s,o = filter_nan(s,o)
    return 100.0*sum(abs(s-o))/sum(o)

def rmse(s,o):
    s,o = filter_nan(s,o)
    return np.sqrt(np.mean((s-o)**2))

def mae(s,o):
    s,o = filter_nan(s,o)
    return np.mean(abs(s-o))

def bias(s,o):
    s,o = filter_nan(s,o)
    return np.mean(s-o)

def NS(s,o):
    s,o = filter_nan(s,o)
    return 1 - sum((s-o)**2)/sum((o-np.mean(o))**2)

def correlation(s,o):
    s,o = filter_nan(s,o)
    return np.corrcoef(o, s)[0,1]

def monoton_i(o,f=0.0):
    """ monotonically increasing, f is a noise redusing factor
    returns a list witn len(o)-1 members
    0 : non monoton ; 1 : monoton
    """
    res=np.ones(len(o)-1)
    for i in range(len(o)-1):
        if((o[i]-o[i+1])>f):
            res[i]=0
    return res

def monoton_d(o,f=0.0):
    """ monotonically decresing
    returns a list witn len(o)-1 members, f is a noise redusing factor
    0 : non monoton ; 1 : monoton
    """
    res=np.ones(len(o)-1)
    for i in range(len(o)-1):
        if((o[i+1]-o[i])>f):
            res[i]=0
    return res

# ------------------------------------------------------------
# Bootstrap as a method to estimate the mean and its 
# coinfidence; without Gaussian distribution 
# ------------------------------------------------------------

def resample(S,size=None):
    return [random.choice(S) for i in xrange(size or len(S))]

def bootstrap(x,coinfidence=0.95, nsample=100):
    """ Computes the bootstrap errors of an input list x """
    ns=len(x)
    if(len(x)<100):
        ns=100
    means=[np.mean(resample(x,ns)) for k in xrange(nsample)]
    means.sort()
    # print means
    left_tail=int(((1-0-coinfidence)/2)*nsample)
    right_tail=nsample-1-left_tail
    return means[left_tail],np.mean(x),means[right_tail]

# ------------------------------------------------------------
# Functions written by Rainer Bruggemann and supplemented using
# http://www.pisces-conservation.com/sdrhelp/index.html
# ------------------------------------------------------------

def pt_pr(o):
    """ calculates relative abundancies pr and sum of abundancies = pt
    """
    pt=float(sum(o))
    pr=np.array(o)
    if(pt==0):
        return pt,np.zeros(len(o))
    return pt,pr/pt

def simpson(o):
    """ calculates Simpson index
    """
    pt,x=pt_pr(o)
    s=float(sum(x*x))
    if(s>0):
        return 1.0/s   # 1.0-s see simvar
    return np.nan

def simvar(o):
    """ calculates Simpson-variante (see Salomon paper)
        o: population of algae, normalized (see pt_pr)
    """
    pt,x=pt_pr(o)
    return 1.0-sum(x*x)

def richness(o,limit):
    """ calculates from o the richness
        o: population of algae, normalized (see pt_pr)
        limit: if o<=limit, then this population will be ignored
    """
    pt,x=pt_pr(o)
    rc=0
    for i in x:
        if(i>limit):
            rc+=1
    return rc

def shannon(o):
    """ calculates Shannon index
        o: population of algae, normalized (see pt_pr)
    """
    pt,x=pt_pr(o)
    return sum(-x[x>0]*np.log(x[x>0]))

def margalefo(o):
    """ r is the number of species (richness)
        n is total of individuals
    """
    if(o==None):
        return 0
    r=len(o)
    n=sum(o)
    if(r==0 or n<=1):
        return 0
    return (r-1)/np.log(n)

def margalef(o):
    """ r is the number of species (richness)
        n is total of individuals
    """
    if(o==None):
        return 0
    r=richness(o,0.0001)
    n=sum(o)
    if(r==0 or n<=1):
        return 0
    return (r-1)/np.log(n)

def sheven(shact,richact):
    """ calculates the Shannon-eveness
        shact: Shannon-index
        richnact: richness index
    """
    if(richact<=1.0):
        return 0.0
    return shact/(np.log(float(richact)))

def partial_sum(o):
    """ 
    uses a numpy array and constructs an array with
    partial sum of the ordered array
    """
    o.sort()
    o=o[::-1]
    part=np.zeros(len(o))
    for i in np.arange(len(o)):
        part[i]=np.sum(o[0:i+1])
    return part

def berger_parker(o):
    """
    This surprisingly simple index was considered by May (1975)
    to be one of the best. It is simple measure of the numerical
    importance of the most abundant species.
    """
    return float(np.max(o))/np.sum(o)

def McIntosh(o):
    """
    Proposed by McIntosh (1967) as:
    D=(N-U)/(N-sqrt(N))
    with U=sum(ni**2)
    """
    N=float(np.sum(o))
    U=np.sqrt(float(np.sum(o**2)))
    return (N-U)/(N-np.sqrt(N))


def menhinick(o):
    """
    Menhinick's index, Dmn (Whittaker, 1977) is calculated using:
    D=S/sqrt(N)
    where N is the total number of individuals in the sample and S
    the species number. 
    """
    return float(len(o))/np.sqrt(np.sum(o))

def strong(o):
    """
    Strong's dominance index, Dw (Strong, 2002), is calculated using:
    D=max_i((bi/Q)-i/R)
    where:
    bi is the sequential cumulative totaling of the ith species abundance
    values ranked from largest to smallest;
    Q is the total number of individuals in the sample;
    R is the number of species in the sample
    maxi is the largest calculated ith values 
    """
    o.sort()      # sort it 
    o[:]=o[::-1]  # reverse it
    b=np.cumsum(o)
    Q=float(np.sum(o))
    R=float(len(o))
    maxi=0.0
    for i in range(len(o)):
        d=(b[i]/Q-i/R)
        if(maxi<d):
            maxi=d
    return maxi

# Evenness

def simpson_e(o):
    """
    This index is based on Simpson's diversity index, D and is defined as:
    E=1/D/S
    where D is Simpson's diversity index and
    S is the number of species.
    """
    return (1.0/simpson(o))/float(len(o))

def McIntosh_e(o):
    """
    This is an equitability measure based on the McIntosh dominance index.
    McIntosh E is defined as (Pielou, 1975):
    D=(N-U)/(N-N/sqrt(s))
    where N is the total number of individuals in the sample and
    S is the total number of species in the sample.
    """
    N=float(np.sum(o))
    U=np.sqrt(float(np.sum(o**2)))
    S=float(len(o))
    return (N-U)/(N-N/np.sqrt(S))
    
def camargo_e(o):
    """
    The Camargo evenness index (Camargo, 1993) is defined as:
    E=1-(sum_i(sum_j=i+1((pi-pj)/S)))
    where
    pi is the proportion of species i in the sample;
    pj is the proportion of species j in the sample and
    S is the total number of species.
    """
    S=float(len(o))
    U=float(np.sum(o))
    s=0.0
    for i in range(len(o)):
        for j in range(i,len(o)):
            s+=(o[i]/U-o[j]/U)/S
    return 1-s

def smith_wilson1_e(o):
    """
    Smith and Wilson's evenness index 1-D (Smith & Wilson, 1996) is defined as:
    E=(1-D)/(1-1/S)   ??? 1-D
    where
    D is Simpson's diversity index and
    S is the total number of species.
    """
    D=simpson(o)
    return (D-1.0)/(1.0-1.0/len(o))
    
def smith_wilson2_e(o):
    """
    Smith and Wilson's evenness index 1/D (Smith & Wilson, 1996) is defined as:
    E=-ln(D)/ln(S)    ??? -
    where
    D is Simpson's diversity index and
    S is the total number of species.
    """
    D=simpson(o)
    return np.log(D)/np.log(float(len(o)))

def gini(o):
    sorted_list = sorted(o)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(o) / 2
    return (fair_area - area) / fair_area

# ------------------------------------------------------------
# some function for Mixin and Complexity added by William Seitz
# ------------------------------------------------------------
class complexity(object):
    def __init__(self,n=30,delta=0.001):
        """ generates the partion for a given number n=30
        """
        if(n<5 or n>30):
            print 'error in complexity nmust be 5>= n <=30'
            return None
        self.n=n
        self.delta=delta
        self.trys={5 : 7,
                   6 : 11,
                   7 : 15,
                   8 : 22,
                   9 : 30,
                   10: 42,
                   11: 56,
                   12: 77,
                   13: 101,
                   14: 135,
                   15: 176,
                   16: 231,
                   17: 297,
                   18: 385,
                   19: 490,
                   20: 627,
                   21: 792,
                   22: 1002,
                   23: 1255,
                   24: 1575,
                   25: 1958,
                   26: 2436,
                   27: 3010,
                   28: 3718,
                   29: 4565,
                   30: 5604}
        self.partition=np.zeros((self.trys[n],n))
        a=[0 for i in range(n)]
        self.counter=0    # counter to fill the self.partition
        self.gen_partition(n,a,0)
        print self.partition
        self.mixin1=None
    def gen_partition(self,n,a,level):
        """ recurrent implementation for partition of a given number
        """
        # print 'gen:',n,level,a
        a=np.copy(a)
        if(n<1):
            return
        a[level]=n
        swp=np.zeros(self.n)
        swp[0:(level+1)]=(a[::-1])[(self.n-level-1):self.n]
        self.partition[self.counter]=np.cumsum(swp)
        self.counter+=1
        if(level==0):
            first=1
        else:
            first=a[level-1]
        for i in xrange(first,int(n/2+1.0)):
            a[level]=i
            self.gen_partition(n-i,a,level+1)
    def histogram(self,mx):
        """ uses the self.n as bins 
            uses int values after normalization
        """
        m=np.array(mx)          # transform it to an ndarray
        m=m.astype(float)       # make sure that is float
        # normalize it check max!=min
        if(float(np.max(m)-np.min(m))!=0):
            m=(m-float(np.min(m)))/(float(np.max(m)-np.min(m)))
        else:
            print 'error in histogram: Min==Max'
        m*=(self.n-1)           # put in range 0..self.n-1
        m=m.astype(int)         # transform it to int
        h={}                    # generates the hist
        for i in xrange(len(m)):
            if m[i] in h:
                h[m[i]]+=1
            else:
                h[m[i]]=1
        
        return h.values()
    def mixin(self,mx):
        """ takes a data set mx and generates a historgram
        """
        #h=np.histogram(mx, bins=self.n)  # build an histogram
        #d1=h[0]                          # extract the data
        d1=self.histogram(mx)              # build an histogram
        d1=np.array(d1)
        d1=d1.astype(float)
        d1.sort()                          # sort the float 
        d1=d1[::-1]                        # sort from high to low
        d1/=np.sum(d1)                     # normalze the data
        d1*=self.n                          
        d1=np.cumsum(d1)                   # cumsum as result
        d2=np.ones(self.n)                 # normalize the length
        d2*=self.n
        d2=d2.astype(float)
        d2[0:len(d1)]=d1
        self.mixin1=d2
        return d2
    def comp(self,mx):
        """ calculates the complexity by comparison the 
            mixin with all possible
            the mixin will be caculated using the gen_mixin(mx) 
        """
        self.mixin(mx)
        comp_counter=0
        for i in xrange(self.trys[self.n]):
            flow=0
            fhigh=0
            for j in xrange(self.n):
                if(self.partition[i,j]<self.mixin1[j]-self.delta):
                    fhigh=1
            if fhigh==0:
                comp_counter+=1
        return float(self.trys[self.n]-comp_counter)/float(self.trys[self.n])
    def plot(self,data,ws=32):
        """ plot the function, calcs the complexity and a continous wavelet """
        N=len(data)
        x=np.arange(N)
        # wavelet part
        widths = np.arange(1, ws)
        cwtmatr = signal.cwt(data, signal.ricker, widths)
        # define the multiple plot
        plt.subplot(2,1,1)
        c=self.comp(data)
        plt.title('Signal complexity='+str(c))
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid(True)
        plt.plot(x,data)
        plt.subplot(2,1,2)
        cax=plt.imshow(cwtmatr,aspect='auto')
        cbar = plt.colorbar(cax)
        plt.xlabel('dt')
        plt.ylabel('dF')
        plt.grid(True)
        plt.show()

def majorization(l1,l2):
    """ defines the majorizatiin between two lists
    a_1 >= b_1
    a_1 + a_2 >= b_1 + b_2
    a_1 + a_2 + a_3 >= b_1 + b_2 + b_3
    ...
    a_1 + a_2 + ... + a_n-1 >= b_1 + b_2 + ... + b_n-1
    a_1 + a_2 + ... + a_n-1 + a_n >= b_1 + b_2 + ... + b_n-1 + b_n
    """
    a=0
    b=0
    r={0}
    for (x,y) in zip(l1,l2):
        a+=x
        b+=y
        r|={cmp(a,b)}
    return sum(r)

# ------------------------------------------------------------
# some functions added by Ralf Wieland
# ------------------------------------------------------------

def fivenum(v):
    """Returns Tukey's five number summary (minimum, lower-hinge,
       median, upper-hinge, maximum) for the input vector,
       a list or array of numbers based on 1.5 times the
       interquartile distance
    """
    try:
        np.sum(v)
    except TypeError:
        print('Error: you must provide a list or array of only numbers')
    q1 = scoreatpercentile(v,25)
    q3 = scoreatpercentile(v,75)
    iqd = q3-q1
    md = np.median(v)
    whisker = 1.5*iqd
    return np.min(v), md-whisker, md, md+whisker, np.max(v)

def sensitivity(TP,FN):
    """ also called TPR = TruePositives/(TruePositives+FalseNegatives)
    """
    if(TP+FN>0):
        return TP/(TP+FN)
    return np.nan

def specificity(FP,TN):
    """ also called TNR = TrueNegatives/(TrueNegatives+FalsePositives)
    """
    if(FP+TN>0):
        return TN/(TN+FP)
    return np.nan

def accuracy(TP,TN,FP,FN):
    if(TP+TN+FP+FN>0):
        return (TP+TN)/(TP+TN+FP+FN)

# after:  benhamner:
# https://github.com/benhamner/Metrics/blob/master/Python/ml_metrics/auc.py
def tied_rank(x):
    """
    Computes the tied rank of elements in x.
    This function computes the tied rank of elements in x.
    Parameters
    ----------
    x : list of numbers, numpy array
    Returns
    -------
    score : list of numbers
            The tied rank f each element in x
    """
    sorted_x = sorted(zip(x,range(len(x))))
    r = [0 for k in x]
    cur_val = sorted_x[0][0]
    last_rank = 0
    for i in range(len(sorted_x)):
        if cur_val != sorted_x[i][0]:
            cur_val = sorted_x[i][0]
            for j in range(last_rank, i): 
                r[sorted_x[j][1]] = float(last_rank+1+i)/2.0
            last_rank = i
        if i==len(sorted_x)-1:
            for j in range(last_rank, i+1): 
                r[sorted_x[j][1]] = float(last_rank+i+2)/2.0
    return r

def auc(actual, posterior):
    """
    Computes the area under the receiver-operater characteristic (AUC)
    This function computes the AUC error metric for binary classification.
    Parameters
    ----------
    actual : list of binary numbers, numpy array
             The ground truth value
    posterior : same type as actual
                Defines a ranking on the binary numbers, from most likely to
                be positive to least likely to be positive.
    Returns
    -------
    score : double
            The mean squared error between actual and posterior
    """
    r = tied_rank(posterior)
    num_positive = len([0 for x in actual if x==1])
    num_negative = len(actual)-num_positive
    sum_positive = sum([r[i] for i in range(len(r)) if actual[i]==1])
    auc = ((sum_positive - num_positive*(num_positive+1)/2.0) /
           (num_negative*num_positive))
    return auc
    

# ------------------------------------------------------------
# some useful definitions from pyeeg
# ------------------------------------------------------------

# definition of the hurst exponent
def hurst(p):
    """ alternative implementation from pyeeg
        trendy      H > 0.5
        jumping     H < 0.5
        determine   H ~ 1.0
        oszilating  H ~ 0.5
        random      H ~ 0.5
    """
    N = len(p)
    T = np.array([float(i) for i in xrange(1,N+1)])
    Y = np.cumsum(p)
    Ave_T = Y/T
	
    S_T = np.zeros((N))
    R_T = np.zeros((N))
    for i in xrange(N):
        S_T[i] = np.std(p[:i+1])
        X_T = Y - T * Ave_T[i]
        R_T[i] = np.max(X_T[:i + 1]) - np.min(X_T[:i + 1])
    # print R_T, S_T
    R_S = R_T / S_T
    R_S = np.log(R_S)
    n = np.log(T).reshape(N, 1)
    H = np.linalg.lstsq(n[1:], R_S[1:])[0]
    return H[0]


def embed_seq(X,Tau,D):
    """
    Examples
	---------------
	>>> import pyeeg
	>>> a=range(0,9)
	>>> pyeeg.embed_seq(a,1,4)
	array([[ 0.,  1.,  2.,  3.],
	       [ 1.,  2.,  3.,  4.],
	       [ 2.,  3.,  4.,  5.],
	       [ 3.,  4.,  5.,  6.],
	       [ 4.,  5.,  6.,  7.],
	       [ 5.,  6.,  7.,  8.]])
	>>> pyeeg.embed_seq(a,2,3)
	array([[ 0.,  2.,  4.],
	       [ 1.,  3.,  5.],
	       [ 2.,  4.,  6.],
	       [ 3.,  5.,  7.],
	       [ 4.,  6.,  8.]])
	>>> pyeeg.embed_seq(a,4,1)
	array([[ 0.],
	       [ 1.],
	       [ 2.],
	       [ 3.],
	       [ 4.],
	       [ 5.],
	       [ 6.], 
               [ 7.],
	       [ 8.]])
    """
    N =len(X)
    if D * Tau > N:
        print "Cannot build such a matrix, because D * Tau > N" 
        exit()
    if Tau<1:
        print "Tau has to be at least 1"
        exit()
    Y=np.zeros((N - (D - 1) * Tau, D))
    for i in xrange(0, N - (D - 1) * Tau):
        for j in xrange(0, D):
            Y[i][j] = X[i + j * Tau]
    return Y

def first_order_diff(X):
    """
    X = [x(1), x(2), ... , x(N)]
    Y = [x(2) - x(1) , x(3) - x(2), ..., x(N) - x(N-1)]
    """
    D=[]
    for i in xrange(1,len(X)):
        D.append(X[i]-X[i-1])
    return D

def pfd(X):
    """
    Compute Petrosian Fractal Dimension of a time series
    """
    D=first_order_diff(X)
    N_delta=0
    for i in xrange(1,len(D)):
        if D[i]*D[i-1]<0:
            N_delta += 1
    n = len(X)
    return np.log10(n)/(np.log10(n)+np.log10(n/n+0.4*N_delta))

def hfd(X, Kmax):
    """ Compute Hjorth Fractal Dimension of a time series X, 
    kmax is an HFD parameter
    """
    L = []
    x = []
    N = len(X)
    for k in xrange(1,Kmax):
        Lk = []
        for m in xrange(0,k):
            Lmk = 0
            for i in xrange(1,int(np.floor((N-m)/k))):
                Lmk += np.abs(X[m+i*k] - X[m+i*k-k])
                Lmk = Lmk*(N - 1)/np.floor((N - m) / float(k)) / k
        Lk.append(Lmk)
        L.append(np.log(np.mean(Lk)))
        x.append([np.log(float(1) / k), 1])
	
    (p, r1, r2, s)=np.linalg.lstsq(x, L)
    return p[0]

def hjorth(X, D = None):
    """ 
    Compute Hjorth mobility and complexity of a time series
    """
    if D is None:
        D = first_order_diff(X)
    D.insert(0, X[0]) # pad the first difference
    D = np.array(D)
    n = len(X)
    M2 = float(np.sum(D ** 2)) / n
    TP = np.sum(np.array(X) ** 2)
    M4 = 0;
    for i in xrange(1, len(D)):
        M4 += (D[i] - D[i - 1]) ** 2
    M4 = M4 / n
    return np.sqrt(M2 / TP), np.sqrt(float(M4) * TP / M2 / M2)

# ------------------------------------------------------------
# Apen after Pinucs
# ------------------------------------------------------------

def apen(x, mm=2, r=1.0):
    """
    x=vector of data
    mm=patter deep 1,2,3,...
    r=thresh
    """
    lll=x.shape[0]-mm+1
    phi1=phi2=0
    # print lll,mm,r
    for i in range(lll):
        v=0
        for j in range(i,lll):
            v1=0
            for p in range(mm):
                v1+=np.abs(x[i+p]-x[j+p])
            if(r>v1):
                v1=1.0
            else:
                v1=0.0
            v+=v1
        phi1-=v/(lll*(lll-1)/2)*np.log(v/(lll*(lll-1)/2))
    mm+=1
    lll-=1
    for i in range(lll):
        v=0
        for j in range(i,lll):
            v1=0
            for p in range(mm):
                v1+=np.abs(x[i+p]-x[j+p])
            if(r>v1):
                v1=1.0
            else:
                v1=0.0
            v+=v1
        phi2-=v/(lll*(lll-1)/2)*np.log(v/(lll*(lll-1)/2))
    return(phi1-phi2)


def main1():
    
    #  Different types of time series for testing
    #p = np.log10(np.cumsum(np.random.randn(50000)+1)+1000) 
    # trending, hurst ~ 1
    #p = np.log10((np.random.randn(50000))+1000)   
    # mean reverting, hurst ~ 0
    #p = np.log10(np.cumsum(np.random.randn(50000))+1000) 
    # random walk, hurst ~ 0.5
    p=np.random.rand(2000)
    print 'rand', hurst(p), pfd(p), hfd(p,5), hjorth(p)[1]
    p=np.zeros(2000)
    for i in range(2000):
        p[i]=np.random.normal()
    print 'norm', hurst(p), pfd(p), hfd(p,5), hjorth(p)[1]
    p=np.zeros(2000)
    p[0]=np.random.rand()-0.5
    for i in range(2000-1):
        x=np.random.rand()-0.5
        p[i+1]=x+p[i]
    print 'walk', hurst(p), pfd(p), hfd(p,5), hjorth(p)[1]
    p=np.zeros(2000)
    for i in range(2000):
        if(i%2==0):
            p[i]=1+0.1*np.random.rand()
        else:
            p[i]=-1+0.1*np.random.rand()
    print 'jump', hurst(p), pfd(p), hfd(p,5), hjorth(p)[1]
    p=np.arange(2000)
    # print p
    print 'ramp', hurst(p), pfd(p), hfd(p,5), hjorth(p)[1]

# main1()

def test():
    o=np.random.rand(10)
    print 'o=', o
    pt,pr =pt_pr(o)
    print 'pt=', pt 
    print 'pr=', pr
    print 'simpson(o)=', simpson(o)
    print 'simpson(pr)=', simpson(pr)
    print 'simvar(pr)=', simvar(pr)
    rich=richness(pr,0.1)
    print 'richness(pr,0.1)=',rich
    shan=shannon(pr)
    print 'shannon(pr)=', shan
    print 'sheven(shan,rich)=',sheven(shan,rich)
    print '****** test after Bruggemann ******'
    o=[0.1,0.2,0,0,0.3,0,2,0.1]
    print 'o=', o
    pt,pr =pt_pr(o)
    print 'pt=', pt 
    print 'pr=', pr
    print 'simpson(o)=', simpson(o)
    print 'simpson(pr)=', simpson(pr)
    print 'simvar(pr)=', simvar(pr)
    rich=richness(pr,0.05)
    print 'richness(pr,0.05)=',rich
    shan=shannon(pr)
    print 'shannon(pr)=', shan
    print 'sheven(shan,rich)=',sheven(shan,rich)
    print '*************partial sum*******************'
    np.random.seed(None)
    x=np.random.normal(0.5,1.0/12,1000)
    left,m,right=bootstrap(x,nsample=100)
    print "bootstrap normal:", left,m, right
    x=np.random.rand(1000)
    left,m,right=bootstrap(x,nsample=100)
    print "bootstrap uniform:", left,m, right
    t=np.arange(20)
    for i in range(5):
        leg=np.random.rand()
        # leg=1.0
        sleg=str(round(leg,3))
        o=leg*np.random.rand(20)
        o/=np.sum(o)        
        o1=partial_sum(o)
        plt.plot(t,o1,label=sleg)
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.xlabel('samples')
    plt.ylabel('partial sum')
    plt.show()


