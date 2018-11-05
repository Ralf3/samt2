#!/usr/bin/env python3
import networkx as nx
import copy
# from inspect import getargspec
import math
from collections import defaultdict
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""
In order theory, a Hasse diagram is a type of mathematical diagram used to 
represent a finite partially ordered set, in the form of a drawing of its 
transitive reduction. Concretely, for a partially ordered set (S, <=) one 
represents each element of S as a vertex in the plane and draws a line segment 
or curve that goes upward from x to y whenever y covers x (that is, whenever 
x < y and there is no z such that x < z < y). These curves may cross each 
other but must not touch any vertices other than their endpoints. Such a 
diagram, with labeled vertices, uniquely determines its partial order.

wikipedia: https://en.wikipedia.org/wiki/Hasse_diagram
"""

# define a structure for hasse diagrams
# first define a sit (situation) to store the values and the pointers to 
# other sits
# remove equal sits

# some global constants 
EQ=0
GT=1
LT=-1
NC=2
OK=0
NN=1
RP=True    # switch report on or off
DELTA=0.0  # to distinguage between two values

class sit():
    """
    class sit implements a data structure to store nodes and their
    predesessors, successors, equivalent and not comparable
    """
    def __init__(self,_name,_feld):
        """
        add a new node 
        """
        self.name=_name # name of the node 
        self.feld=copy.copy(_feld) # data vector 
        self.rand=copy.copy(_feld)
        self.pred=[]    # set of predecessors
        self.succ=[]    # set of succsessors
        self.nc=[]      # set of not comparable sits
        self.eq=[]      # set of equal nodes
        self.level=[]   # set the level of the node 
    def add_succ(self,sitname):
        """
        add a node with the sitname as a succsessor
        """
        if(not sitname in self.succ):
            self.succ.append(sitname)
    def add_pred(self,sitname):
        """
        add a node with the sitname as a predecessor
        """
        if(not sitname in self.pred):
            self.pred.append(sitname)
    def add_nc(self,sitname):
        """
        add a node with the sitname as a non comparable node
        """
        if(not sitname in self.nc):
            self.nc.append(sitname)
    def add_eq(self,sitname):
        """ 
        add a node with the sitname as a equivalent node
        """
        if(not sitname in self.eq):
            self.eq.append(sitname)
    def get_succ(self):
        return self.succ
    def get_pred(self):
        return self.pred
    def get_nc(self):
        return self.nc
    def get_eq(self):
        return self.eq
    def get_feld(self):
        return self.feld
    def get_name(self):
        return self.name
    def erase_pred(self,sitp):
        """
        erase the node sitp from the predecessor list
        """
        if(sitp in self.pred):
            self.pred.remove(sitp)
    def erase_eq(self,sitp):
        """
        erase the node sitp from the list of equivalence node 
        """
        if(sitp in self.eq):
            self.eq.erase(sitp)
    def erase_succ(self,sitp):
        """
        erase the node sitp from the successor list
        """
        if(sitp in self.succ):
            self.succ.remove(sitp)
    def clear_succ(self):
        self.succ=[]
    def clear_pred(self):
        self.pred=[]
    def clear_nc(self):
        self.nc=[]
    def clear_eq(self):
        self.eq=[]
    def rand_uniform(self,p):  # p=percentage of change
        """
        create a random change of the data vector according to p/100
        """
        for i in range(len(self.rand)):
            self.rand[i]=self.feld[i]+\
                          self.feld[i]*p/100.0*(0.5-np.random.rand())
    def rand_normal(self,sd):  # sd=standard deviation
        """
        create a random change of the data vector using a normal distribution
        with the standard deviation sd
        """
        for i in range(len(self.rand)):
            self.rand[i]=np.random.normal(self.feld[i],sd)
    def rand_triangular(self,p,left,mode,right):
        """
        create a random change of the data vector using a triangular 
        distribution with p/100 and left mode right
        """
        for i in range(len(self.rand)):
            self.rand[i]=self.feld[i]+\
                          self.feld[i]*p/100.0*(0.5-np.random.triangular(
                              left,mode,right))
   
def hasse_comp(s1,s2):
    """ defines the normally used hasse compare function
        used by the generic hasse.compare(sit1,sit2,fx=hasse_comp)
        returns NC, GT, LT, EQ
    """
    if(s1.name==s2.name):
        return EQ
    feld1=s1.get_feld()
    feld2=s2.get_feld()
    if(len(feld1)!=len(feld2)):
        return NC
    l=len(feld1)
    gt=0
    lt=0
    eq=0
    for i,j in zip(feld1,feld2):
        if(i>=j):
            gt+=1
        if(i<=j):
            lt+=1
        if(np.fabs(i-j)<=DELTA):
            eq+=1
    
    if(eq==l):
        return EQ
    if(gt==l):
        return GT
    if(lt==l):
        return LT
    return NC

def majo_comp(s1,s2):
    """ defines a compare function wich it gt if more than half was gt
        used by the generic hasse.compare(sit1,sit2,fx=hasse_comp)
        returns NC, GT, LT, EQ
    """
    feld1=s1.get_feld()
    feld2=s2.get_feld()
    if(len(feld1)!=len(feld2)):
        return NC
    l=len(feld1)
    gt=0
    lt=0
    eq=0
    for i,j in zip(feld1,feld2):
        if(i>j):
            gt+=1
        if(i<j):
            lt+=1
        if(np.fabs(i-j)<=DELTA):
            eq+=1
    if(eq==l):
        return EQ
    if(gt>lt):
        return GT
    if(lt>gt):
        return LT
    return NC

def majo1_comp(s1,s2):
    """ defines a compare function wich it gt if maximum one is smaller
        used by the generic hasse.compare(sit1,sit2,fx=hasse_comp)
        returns NC, GT, LT, EQ
    """
    feld1=s1.get_feld()
    feld2=s2.get_feld()
    if(len(feld1)!=len(feld2)):
        return NC
    l=len(feld1)
    gt=0
    lt=0
    eq=0
    for i,j in zip(feld1,feld2):
        if(i>j):
            gt+=1
        if(i<j):
            lt+=1
        if(np.fabs(i-j)<=DELTA):
            eq+=1
    if(eq==l):
        return EQ
    if(gt>=l-1)or (eq==l-1 and gt==1):
        return GT
    if(lt>=l-1 or (eq==l-1 and lt==1)):
        return LT
    return NC

def m2_comp(s1,s2):
    """ defines a compare which simplyfies to a two dimensional vector: 
        v=[min(q1,q2,...,qn), max(q1,q2,...,qn)]
        returns NC,GT,LT,EQ
    """
    feld1=s1.get_feld()
    feld2=s2.get_feld()
    if(len(feld1)!=len(feld2)):
        return NC
    l=2
    gt=0
    lt=0
    eq=0
    vs1=[np.min(feld1),np.max(feld1)]
    vs2=[np.min(feld2),np.max(feld2)]
    for i,j in zip(vs1,vs2):
        if(i>j):
            gt+=1
        if(i<j):
            lt+=1
        if(np.fabs(i-j)<DELTA):
            eq+=1
    if(eq==l):
        return EQ
    if(gt>lt):
        return GT
    if(lt>gt):
        return LT
    return NC

def ms_comp(s1,s2):
    """ uses the mean and the std for compare """
    feld1=s1.get_feld()
    feld2=s2.get_feld()
    if(len(feld1)!=len(feld2)):
        return NC
    vs1=[np.mean(feld1),np.std(feld1)]
    vs2=[np.mean(feld2),np.std(feld2)]
    gt=0
    lt=0
    eq=0
    l=2
    for i,j in zip(vs1,vs2):
        if(i>j):
            gt+=1
        if(i<j):
            lt+=1
        if(np.fabs(i-j)<=DELTA):
            eq+=1
    if(eq==l):
        return EQ
    if(gt==l):
        return GT
    if(lt==l):
        return LT
    return NC

    
def majorization_comp(s1,s2):
    """ defines the compare function uses majorization
        normalizes the rows to sum=1.0 and sortes the felds
        before applying the compare
    """
    if(s1==s2):
        return EQ
    feld1=np.copy(s1.get_feld())  # use a copy 
    feld2=np.copy(s2.get_feld())
    if(len(feld1)!=len(feld2)):
        return NC
    f1=feld1
    f2=feld2
    f1=np.sort(f1)[::-1]     # sort it in decending order
    f2=np.sort(f2)[::-1]     # sort it in decending order
    f1=np.cumsum(f1)         # calc the cumsum
    f2=np.cumsum(f2)         # calc the cumsum
    f1/=f1[-1]
    f2/=f2[-1]
    l=len(f1)
    gt=0
    lt=0
    eq=0
    for i,j in zip(f1,f2):
        if(i>j):
            gt+=1
        if(i<j):
            lt+=1
        if(np.fabs(i-j)<=DELTA):
            eq+=1
    #rint s1.name, f1,gt,lt,eq
    #rint s2.name, f2,gt,lt,eq
    if(eq==l):
        return EQ
    if(gt+eq==l):
        return GT
    if(lt+eq==l):
        return LT
    return NC
    
class hassetree():
    """
    the class hassetree uses elements of the class sit to build a partial 
    ordered set
    """
    def __init__(self,fx=hasse_comp):
        """ 
        init the hassetree with empty elements
        and the compare function byx default hasse_comp
        """ 
        self.liste=[]   # list of all sits
        self.eq={}      # equivalence class
        self.fx=fx      # compare function can be provided by user
        self.norm=False # indicates the col_norm
        self.matrix = None  # Adjacent matrix to store the GT:1 NC:0 LT:-1
        self.levels=defaultdict()  # dict of all levels
        self.eqs=[]     # list of euq pairs
        
    def print_eq(self):
        """ 
        help function to print equivalent nodes
        """
        for i in self.eqs:
            print(i[0].get_name(), ': ', i[1].get_name())
    
    def print_succ(self):
        for i in self.liste:
            print(i.get_name(), ': ', end='')
            for j in i.succ:
                print(j.get_name(),' ',end='')
            print()

    def print_pred(self):
        for i in self.liste:
            print(i.get_name(), ': ', end='')
            for j in i.pred:
                print(j.get_name(),' ',end='')
            print()        
            
            
    def print_nc(self):
        for i in self.liste:
            print(i.get_name(), ': ', end='')
            for j in i.nc:
                print(j.get_name(),' ',end='')
            print()   
            
    def print_levels(self):
        for key in self.levels.keys():
            print(key,': ',end='')
            for j in self.levels[key]:
                print(j,' ',end='')
            print() 
            
    def compare(self,sit1,sit2):
        """ 
        help function to compare two nodes
        """
        res=self.fx(sit1,sit2)
        return res
    
    def insert(self,sitp):
        """ 
        most important function to insert a new node sitp
        it takes care for ordering the node in the eq,nc,succ or pred
        -------------------------------------------------------------
        The new version is splitted in a simple append to the 
        of each sitp to self.liste.
        After all sitps are included a general run to sort the 
        elements of the self.list accroding to the used compare has to be made. 
        """
        for i in range(len(self.liste)): 
            x=self.compare(self.liste[i],sitp)
            if(x==EQ):
                self.eqs.append((self.liste[i], sitp))
                return False
        self.liste.append(sitp)
        return True
    
    def insert1(self):
        """
        most important second part of the insert procedure
        it takes care for ordering the node in the eq,nc,succ or pred
        """
        self.matrix=np.zeros((len(self.liste),len(self.liste))) # define the adjacent matrix
        for i in range(len(self.liste)): 
            for j in range(len(self.liste)):
                if(i==j):
                    continue
                x=self.compare(self.liste[i],self.liste[j])
                if(x==LT):
                    self.matrix[i,j]=-1
                if(x==GT):
                    self.matrix[i,j]=1
                if(x==NC):
                    self.matrix[i,j]=0 # is not necessary to set 
        return True
    
#    def clean_edge(self):
#        self.insert1()
#        """ fill the sitp with values from the adjacent matrix """
#        for i in range(len(self.liste)): 
#            self.levels[np.sum(self.matrix[i,:])]=[] # define the lists in self.level
#            
#        for i in range(len(self.liste)):
#            """ set the level for the sitp and for the self.level """
#            self.liste[i].level=np.sum(self.matrix[i,:])
#            self.levels[np.sum(self.matrix[i,:])].append(i)    
#            
#        """ fill the sitp accroding to the level """  
#        klist=list(self.levels.keys())
#        for k in range(len(klist)-1):
#            for i in self.levels[klist[k]]:
#                for j in self.levels[klist[k+1]]:
#                    if(i==j):
#                        continue
#                    # print(k,i,j)
#                    if(self.matrix[i,j]==0):
#                        self.liste[i].nc.append(self.liste[j])
#                    if(self.matrix[i,j]==-1):
#                        self.liste[i].succ.append(self.liste[j])
#                    if(self.matrix[i,j]==1) :
#                        self.liste[i].pred.append(self.liste[j])
#
#        # save the object into the level dict
#        
#        return True
    
    def clean_edge(self):
        self.insert1()
        """ fill the sitp with values from the adjacent matrix """
        for i in range(len(self.liste)): 
            self.levels[np.sum(self.matrix[i,:])]=[] # define the lists in self.level
            
        for i in range(len(self.liste)):
            """ set the level for the sitp and for the self.level """
            self.liste[i].level=np.sum(self.matrix[i,:])
            self.levels[np.sum(self.matrix[i,:])].append(i)    
            
        """ collect all nc from the matrix
        """
        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                if(self.matrix[i,j]==0):
                    self.liste[i].nc.append(self.liste[j])
        """
        A set is used to remove the transitivity - a great idea after Massimo Santini
        We have used the matrix as the basic data structure.
        """
        E=set()
        for i in range(len(self.liste)):
            for j in range(len(self.liste)):
                if(i==j):
                    continue
                if(self.matrix[i,j]==1):
                    E.add((i,j))
        """
        now we have all edges we have to remove the transitiv in E2
        """
        E2=set()
        for e0 in E:
            for e1 in E:
                if e0[1] == e1[0]:
                    E2.add((e0[0], e1[1]))
        E=E-E2 # this is great!
        """
        now we use the edges E to fill the sitp in liste
        """
        for e0 in E:
            self.liste[e0[0]].pred.append(self.liste[e0[1]])
            self.liste[e0[1]].succ.append(self.liste[e0[0]])
        
        
        return True
    def col_norm(self):
        """
        help function which normalizes the columns between 0..1
        set the variable self.norm=True
        returns True if norm was made else False
        """
        if(self.norm==False):
            self.norm=True
            div=np.zeros(len(self.liste[0].feld))
            for sitp in self.liste:
                div+=sitp.feld
            for sitp in self.liste:
                sitp.feld/=div
            return True
        return False

    def gen_report(self):
        """ writes all sits of self.liste according to EQ, NC, GT and LT
        """
        f=open('report.txt','w')
        for i in range(len(self.liste)):
            s=str(self.liste[i].name)+"\n"
            f.write(s)
            s='Pred:'
            for j in self.liste[i].pred:
                s+=str(j.name)
                s+=" "
            s+="\n"
            f.write(s)
            s='Succ:'
            for j in self.liste[i].succ:
                s+=str(j.name)
                s+=" "
            s+="\n"
            f.write(s)
            s='EQ:'
            for j in self.liste[i].eq:
                s+=str(j.name)
                s+=" "
            s+="\n"
            f.write(s)
            s='NC:'
            for j in self.liste[i].nc:
                s+=str(j.name)
                s+=" "
            s+="\n"
            f.write(s)
            s=70*'_'
            s+="\n"
            f.write(s)
        f.close()
        return

    def draw_simple(self,title,color):
        """ draws a simple graph without levels for an overview """
        self.clean_edge()                # make the succ minimal
        G=nx.DiGraph()                      # define a digraph
        for i in self.liste:
            G.add_node(i.name)  # add all sits to graph as nodes
        for i in self.liste:
            for j in i.succ:
                G.add_edge(i.name,j.name)
        print()
        # fill the labels with default values
        labels={}
        for l in G.nodes():
            labels[l]=str(l)
        # pos=nx.spring_layout(G)
        # pos=nx.spectral_layout(G)
        # pos=nx.random_layout(G)
        pos=nx.shell_layout(G)

        if(color==True):
            nx.draw_networkx_nodes(G,pos,node_color='g',node_size=800)
        else:
            nx.draw_networkx_nodes(G,pos,node_color='w',node_size=800)
        nx.draw_networkx_edges(G,pos)
        nx.draw_networkx_labels(G,pos)
        plt.title('SIMPLE: '+title)
        plt.axis('on')
        plt.show()
        
    def make_graph(self):
        """
        make_graph based on networkx and uses Digraphs
        it fills beginning from succ==0 and returns the data 
        structure for a graph;
        all values in hassetree and stored sits will be destroid
        """
        G=nx.DiGraph()                      # define a digraph
        for i in self.liste:
            G.add_node(i.name)  # add all sits to graph as nodes
        for i in self.liste:
            for j in i.succ:
                G.add_edge(i.name,j.name)
        print()
        # fill the labels with default values
        labels={}
        for l in G.nodes():
            labels[l]=str(l)
        alevel={}
        k=0
        for key in self.levels.keys():
            alevel[k]=[self.liste[i].get_name() for i in self.levels[key]]
            k+=1
        return G, alevel

    def make_graphs(self):
        """
        make_graph based on networkx and uses Digraphs
        it fills beginning from succ==0 and returns the data structure 
        for a graph; all values in hassetree and stored sits will be destroid
        """
        self.clean_edge()                # make the succ minimal
        if(RP==True):
            self.gen_report()            # prints a large rport
        
        G=nx.DiGraph()                   # define a digraph
        for sitp in self.liste:
            G.add_node(sitp.name)  # add all sits to graph as nodes
        level=0
        alevel={}
        lold=len(self.liste)
        while(len(self.liste)!=0):
            xlist=[]
            llevel=[]
            for i in self.liste:         # find all sitp with empty succ
                if(len(i.succ)==0):
                    xlist.append(i)
            for i in xlist:              # remove sitp from listp
                self.liste.remove(i)
            for i in self.liste:         # remove all succ in liste
                for j in xlist:          # which are in xlist
                    i.erase_succ(j)
            for i in xlist:
                llevel.append(i.name)
                for j in i.get_pred():
                    G.add_edge(j.name,i.name)
            alevel[level]=llevel
            level+=1
            if(lold==len(self.liste)):
               print('error in  make_graph ===> exit')
               sys.exit(1)
            lold=len(self.liste)
        return G, alevel
        
def print_hd(gx,level,title,dir='succ',color=True):
    """
    function for drawing a Hasse diagram with:
    gx=networkX structure which was returned by hassetree.make_graph()
    level=list of level which was returned by hassetree.make_graph()
    title=string title of the chart
    """
    nodes=1200 # size of the nodes
    gruen=[]
    rot=[]
    # print(level.values()[-1])
    #print gx.edges()
    for l in level[0]:
        for paar in gx.edges():
            if(l==paar[0]):
                gruen.append(l)
    gruen=set(gruen)
    for l in level[0]:
        if(not l in gruen):
            rot.append(l)
    # fill the labels with default values
    labels={}
    for l in gx.nodes():
        labels[l]=str(l)
    # generate the pos of the HD from level 
    pos={}
    ilevel=0
    if(dir=='succ'):
        lll=list(level.values())[::-1]
    else:
        lll=level.values()
    for l in lll:
        dx=1.0/(len(l)+1)
        x=dx
        for node in l:
            pos[node]=(x,ilevel)
            x+=dx
        ilevel+=1
    # print(pos)
    # draw it
    # print(level)
    if(color==False):
        for l in range(len(level)):
            if l==0:
                nx.draw_networkx_nodes(gx,pos,
                                       nodelist=gruen,
                                       node_color='lightgray',
                                       node_size=nodes)
                nx.draw_networkx_nodes(gx,pos,
                                       nodelist=rot,
                                       node_color='lightgray',
                                       node_size=nodes)
            else:
                nx.draw_networkx_nodes(gx,pos,
                                       nodelist=level[l],
                                       node_color='lightgray',
                                       node_size=nodes)
    else:
        for l in range(len(level)):
            if l==0:
                nx.draw_networkx_nodes(gx,pos,
                                       nodelist=gruen,
                                       node_color='g',
                                       node_size=nodes)
                nx.draw_networkx_nodes(gx,pos,
                                       nodelist=rot,
                                       node_color='r',
                                       node_size=nodes)
            else:
                nx.draw_networkx_nodes(gx,pos,
                                       nodelist=level[l],
                                       node_color='g',
                                       alpha=1.0-0.8*l/len(level),
                                       node_size=nodes)
  
    nx.draw_networkx_edges(gx,pos)
    nx.draw_networkx_labels(gx,pos,labels)
    plt.title('HD: '+title)
    plt.axis('on')
    plt.show()

def read_from_excel(filename, table, name, args):
    """ 
    reads from an excel file using column names in args 
    name is the name of the objects
    returns:
    numpy array mw[i,j]: rows=i cols=data vector[j]
    z_namen: object names according to the rows
    """
    data=pd.read_excel(filename, table)
    z_namen=data[name]
    mw=np.zeros((len(data),len(args)))
    # fille the mw
    for i in range(len(data)):
        for j,item in enumerate(args):
            mw[i,j]=data[item][i]
    return mw,z_namen

def read_data(filename):
    """
    reads a csv-file of the following structure:
    header: Name col1name col2name col3name
    rows:   rowname col1_value col1_value col1_value
    returns:
    numpy array mw[i,j]: rows=i cols=data vector[j]
    z_namen: object names according to the rows
    
    """
    f=open(filename) 
    zeilen=len(f.readlines())
    f.seek(1)    # go back to the beginning
    spalten=len(f.readline().split())
    zeilen-=1    # do not count the header
    spalten-=1   # do not count the id
    mw=np.zeros((zeilen,spalten))
    f.seek(1)
    sp_namen=f.readline().split()  # select the names from header
    print('zeilen:', zeilen, 'spalten:', spalten)
    zeile=[]
    z_namen=[]
    nr=0        # row counter
    for line in f.readlines():
        zeile=line.split()
        z_namen.append(zeile[0])
        for i in range(spalten):
            mw[nr,i]=float(zeile[i+1])
        nr+=1
    f.close()
    # generate a simple statistics the check the read in
    print('col-names:')
    print(sp_namen)
    print('row-names:')
    print(z_namen)
    print("min\tmean\tmax")
    for i in range(spalten):
        print(np.min(mw[:,i]),'\t',np.mean(mw[:,i]),'\t',np.max(mw[:,i]))
    return mw,z_namen

# pretty print of a matrix
def pprint(m,z_namen):
    (zeilen,spalten)=np.shape(m)
    typus=m.dtype.name
    for i in range(zeilen):
        print("%3d :" % i,end='')
        for j in range(spalten):
            if(typus=='int64' or typus=='int32'):
                print("%d" % (m[i,j]),end='')
            if(typus=='float64' or typus=='float32'):
                print("%3.2f" % (m[i,j]),end='')
        print(z_namen[i])



#""" simple tests to check the program """
#path='/datadisk/samt2/stats1/'
#testcase='adrian.csv'
#mw,z_namen=read_data(path+testcase)
#hasse1=hassetree(hasse_comp)
#for i in range(len(mw)):
#    sitp=sit(z_namen[i],mw[i])
#    hasse1.insert(sitp)
#    
#hasse1.clean_edge()
#hasse1.print_eq() 
#hasse1.print_succ()
#hasse1.print_pred()
#hasse1.print_nc()
#hasse1.print_levels()
#hasse1.draw_simple('Test',True)
#G,alevel=hasse1.make_graph()
#print_hd(G,alevel,'xhasse')  

"""
{'1': (0.5, 0), '2': (0.25, 1), '3': (0.5, 1), '4': (0.75, 1), '6': (0.25, 2), '7': (0.5, 2), '8': (0.75, 2), '9': (0.5, 3)}
{0: ['9'], 1: ['6', '7', '8'], 2: ['2', '3', '4'], 3: ['1']}
"""
