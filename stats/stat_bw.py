#!/usr/bin/env python
import sys
import csv
import random
# import required modules
import numpy as np
import pylab as plt

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
# Functions written by Rainer Bruggemann
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

# ------------------------------------------------------------
# some new functions added by Ralf Wieland
# ------------------------------------------------------------

def gini(o):
    sorted_list = sorted(o)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(o) / 2
    return (fair_area - area) / fair_area

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


