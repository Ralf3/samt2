#!/usr/bin/env python
import networkx as nx
import copy
import math
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
DELTA=0.001  # to distinguage between two values
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
   

class hassetree():
    """
    the class hassetree uses elements of the class sit to build a partial 
    ordered set
    """
    def __init__(self):
        """ init the hassetree with empty elements
        """ 
        self.liste=[]   # list of all sits
        self.eq={}      # equivalence class
    def print_eq(self):
        """ 
        help function to print equivalent nodes
        """
        for i in self.liste:
            if(i.get_eq()!=[]):
                print i.get_name(),':',i.get_eq()
    def compare(self,sit1,sit2):
        """ 
        help function to compare two nodes
        """
        feld1=sit1.get_feld()
        feld2=sit2.get_feld()
        if(len(feld1)!=len(feld2)):
            return NC
        val,valk,valg=0,0,0
        for i in range(len(feld1)):
            if(math.fabs(feld1[i]-feld2[i])>DELTA):
                val=1
                if(feld1[i]<feld2[i]): 
                    valk=1
                if(feld1[i]>feld2[i]): 
                    valg=1;
        if(val==0):
            if(sit1.get_name()!=sit2.get_name()):
                print 'eq:',sit1.get_name(),sit2.get_name()
            return EQ
        if(valk==1 and valg==1): 
            return NC  # not comparable
        if(valk==0 and valg==1): 
            return GT  # return GT
        if(valk==1 and valg==0):
            return LT  # return LT
        return NC      # default return not comparable
    def insert(self,sitp):
        """ 
        most important function to insert a new node sitp
        it takes care for ordering the node in the eq,nc,succ or pred
        """
        if(len(self.liste)==0): # add sitp as first element
            self.liste.append(sitp)
            return
        eq_flag=False
        for i in self.liste  :  # sort out all sit which are alredy in 
            x=self.compare(i,sitp)
            if(x==EQ):
                i.add_eq(sitp)
                sitp.add_eq(i)
                self.eq[sitp.get_name()]=i.get_name()
                eq_flag=True
        if(eq_flag==True):
            return
        for i in self.liste:    # insert sitp and add all succ, pred, nc
            x=self.compare(sitp,i)
            if(x==LT):
                i.add_pred(sitp)
                sitp.add_succ(i)
            if(x==GT):
                sitp.add_pred(i)
                i.add_succ(sitp)
            if(x==NC):
                i.add_nc(sitp)
                sitp.add_nc(i)
        self.liste.append(sitp) # insert sitp itself
    def clean_edge(self):
        """
        help function for cleaning 
        """
        for i1 in self.liste:
            xlist=[]
            for i2 in i1.get_succ():
                zwsp=i2
                for i3 in i1.get_succ():
                    x=self.compare(zwsp,i3) # find the smallest sit over i1
                    if(x==GT):
                        zwsp=i3
                xlist.append(zwsp)
            i1.clear_succ()
            for xi in xlist:
                i1.add_succ(xi)
    def make_graph(self):
        """
        make_graph based on networkx and uses Digraphs
        it fills and returns the data structure for a graph
        all values in hassetree and stored sits will be destroid
        """
        self.clean_edge()                # make the succ minimal
        G=nx.DiGraph()                   # define a digraph
        for sitp in self.liste:
            G.add_node(sitp.get_name())  # add all sits to graph as nodes
        level=0
	alevel={}
        while(len(self.liste)!=0):
            xlist=[]
	    llevel=[]
            for i in self.liste:         # find all sitp with empty pred 
                if(len(i.get_pred())==0):
                    xlist.append(i)
            for i in xlist:              # remove sitp from listp
                self.liste.remove(i)
            for i in self.liste:         # remove all pred in liste
                for j in xlist:          # which are in xlist
                    i.erase_pred(j)
    
            for i in xlist:
		llevel.append(i.get_name())
                for j in i.get_succ():
                    G.add_edge(i.get_name(),j.get_name())
	    alevel[level]=llevel
	    level+=1
        return G, alevel
    
def print_hd(gx,level,title):
    """
    function for drawing a Hasse diagram with:
    gx=networkX structure which was returned by hassetree.make_graph()
    level=list of level which was returned by hassetree.make_graph()
    title=string title of the chart
    """
    gruen=[]
    rot=[]
    #print level
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
    for l in level.values():
        dx=1.0/(len(l)+1)
        x=dx
        for node in l:
            pos[node]=(x,ilevel)
            x+=dx
        ilevel+=1
    # draw it
    for l in range(len(level)):
        if l==0:
            nx.draw_networkx_nodes(gx,pos,
                                   nodelist=gruen,
                                   node_color='g',
                                   node_size=500)
            nx.draw_networkx_nodes(gx,pos,
                                   nodelist=rot,
                                   node_color='r',
                                   node_size=500)
        else:
            nx.draw_networkx_nodes(gx,pos,
                                   nodelist=level[l],
                                   node_color='g',
                                   alpha=1.0-0.8*l/len(level),
                                   node_size=500)
  
    nx.draw_networkx_edges(gx,pos)
    nx.draw_networkx_labels(gx,pos,labels)
    plt.title('HD: '+title)
    plt.axis('off')
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
    print 'zeilen:', zeilen, 'spalten:', spalten
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
    print 'col-names:'
    print sp_namen
    print 'row-names:'
    print z_namen
    print "min\tmean\tmax"
    for i in range(spalten):
        print np.min(mw[:,i]),'\t',np.mean(mw[:,i]),'\t',np.max(mw[:,i])
    return mw,z_namen

# pretty print of a matrix
def pprint(m,z_namen):
    (zeilen,spalten)=np.shape(m)
    typus=m.dtype.name
    for i in range(zeilen):
        print "%3d :" % i,
        for j in range(spalten):
            if(typus=='int64' or typus=='int32'):
                print "%d" % (m[i,j]),
            if(typus=='float64' or typus=='float32'):
                print "%3.2f" % (m[i,j]),
        print z_namen[i]

