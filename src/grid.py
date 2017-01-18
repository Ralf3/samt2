import cython
cimport cython
import numpy as np
cimport numpy as np
import csv
import re
import h5py
import pywt
import pylab as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.signal as signal
from scipy.interpolate import Rbf
from scipy.interpolate import RectBivariateSpline
import scipy.ndimage
import datetime
import os.path, time
import operator

# SAMT2 uses a np.float32 as data type for the grid values.
# This comes from ARCGIS and saves memory compared to double

DTYPE = np.float32
ctypedef np.float32_t DTYPE_t
ctypedef np.int_t ITYPE_t
ctypedef np.double_t DOUBLE_t

cdef class rect(object):
    """ an implementation of a rectangular region with
        i1:i2 and j1:j2
    """
    cdef int ii1,ii2,jj1,jj2
    def __init__(self,int i1, int i2, int j1, int j2):
        self.ii1=i1
        self.jj1=j1
        self.ii2=i2
        self.jj2=j2
    def i1(self):
        return self.ii1
    def i2(self):
        return self.ii2
    def j1(self):
        return self.jj1
    def j2(self):
        return self.jj2
    #def __repr__(self):
    #    return "%d %d : %d %d" % (self.ii1,self.jj1,self.ii2,self.jj2)

cdef class grid(object):
    """ implementation of a grid class in cython """
    cdef int nrows          # number of rows
    cdef int ncols          # number of columns
    cdef double x           # x of lower left corner
    cdef double y           # y of lower left corner
    cdef double csize       # resolution of the grid
    cdef int nodata         # exclude from calculation
    cdef np.ndarray mat     # storage for the data
    cdef np.ndarray d4_mat  # store the result of d4 
    cdef np.ndarray d8_mat  # store the result of d8 
    cdef int x1,x2          # help for kadane
    cdef np.ndarray sub     # maximum subarray
    cdef str time1          # time and date of a grid
    cdef str date1
    cdef np.ndarray partition # used to calculate the complexity
    cdef int counter          # used to calculate the complexity
    def __init__(self,int nrows=0, int ncols=0,
                 double x=0.0, double y=0.0,
                 double csize=1.0,int nodata=-9999):
        self.nrows=nrows
        self.ncols=ncols
        self.x=x
        self.y=y
        self.csize=csize
        self.nodata=nodata
        self.x1=0    # some stuff for kadane
        self.x2=0
        self.mat=None
        self.d4_mat=None
        self.d8_mat=None
        self.time1=str('\0')
        self.date1=str('\0')
        self.partition=None
        self.counter=0
        # create a empty grid if the nrows and ncols are given 
        if(self.nrows!=0 and self.ncols!=0):
            self.mat=np.zeros((self.nrows,self.ncols),dtype=DTYPE)
            self.nodata=-9999
            self.csize=1.0
            self.x=0.0
            self.y=0.0
        self.sub=None
    # read and write a grid =============================================
    def read_csv(self, str filename):
        """ read a csv and fill the mat with it """
        cdef int i
        cdef int j
        try:
            f=open(filename)
        except IOError:
            print("count not open:", filename)
            return False
        x=f.readlines()
        self.nrows=len(x)
        self.ncols=len(x[0].rsplit())
        if(self.nrows>0 and self.ncols>0):
            self.mat=np.zeros((self.nrows,self.ncols),dtype=DTYPE)
            for i in xrange(self.nrows):
                line=x[i].rsplit()
                for j in xrange(len(line)):
                    self.mat[i,j]=np.float32(line[j])
        f.close()
        self.csize=1.0
        self.x=0.0
        self.y=0.0
        self.nodata=-9999
        return True
    def read_ascii(self,str filename, int DEBUG=0):
        """ read a grid from the GIS """
        try:
            f=open(filename)
        except IOError:
            print("count not open:", filename)
            return False
        (mode,ino,dev,nlink,uid,gid,size,atime,mtime,ctime) = os.stat(filename)
        s=time.localtime(ctime)
        time1= "%02d:%02d:%02d" % (s.tm_hour, s.tm_min, s.tm_sec)
        self.time1= <str> time1
        date1= "%04d-%02d-%02d" % (s.tm_year, s.tm_mon, s.tm_mday)
        self.date1= <str> date1
        # read header using re
        m=re.match('(\w*)\s+(\d*)',f.readline())
        self.ncols=int(m.group(2))
        m=re.match('(\w*)\s+(\d*)',f.readline())
        self.nrows=int(m.group(2))
        s=f.readline()
        m=re.match('(\w*)\s+(.\d*\.\d*)',s)
        if m is None:
            m=re.match('(\w*)\s+(.\d*)',s)
        self.x=float(m.group(2))
        s=f.readline()
        m=re.match('(\w*)\s+(.\d*\.\d*)',s)
        if m is None:
            m=re.match('(\w*)\s+(.\d*)',s)
        self.y=float(m.group(2))
        s=f.readline()
        m=re.match('(\w*)\s+(-*\d*\.\d*)',s)
        if m is None:
            m=re.match('(\w*)\s+(-*\d*)',s)    
        self.csize=float(m.group(2))
        m=re.match('(\w*)\s+(.\d*)',f.readline())
        self.nodata=int(m.group(2))
        if(DEBUG==1):
            print("nrows\t", self.nrows)
            print("ncols\t", self.ncols)
            print("xllcorner\t", self.x)
            print("yllcorner\t", self.y)
            print("cellsize\t", self.csize)
            print("nodata\t", self.nodata)
        reader=csv.reader(f,delimiter=' ')
        f.close()
        self.mat=np.loadtxt(filename, dtype=np.float32, skiprows=6)
        return True
    def write_ascii(self, str filename):
        """ stores a ascii file and the header as export to the GIS """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        f=open(filename,'w')
        f.write('ncols\t'+str(self.ncols)+'\n')
        f.write('nrows\t'+str(self.nrows)+'\n')
        f.write('xllcorner\t'+str(self.x)+'\n')
        f.write('yllcorner\t'+str(self.y)+'\n')
        f.write('cellsize\t'+str(self.csize)+'\n')
        f.write('NODATA_value\t'+str(self.nodata)+'\n')
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(j<self.ncols-1):
                    s="%f " % mx[i,j]
                else:
                    s="%f\n" % mx[i,j]
                f.write(s)
        f.close()
        return True
    def list_hdf(self, str filename):
        """ list all datasets from a hdf """
        try:
            hdf=h5py.File(filename,'r')
        except IOError:
            print("count not open:", filename)
            return None
        names=[]
        for data in hdf.keys():
            names.append(data)
        hdf.close()
        return names
    def read_hdf(self,str filename,str dataset, int DEBUG=0):
        """ read a dataset from a hdf and return a grid """
        try:
            hdf=h5py.File(filename,'r')
        except IOError:
            print("count not open:", filename)
            return False
            # sys.exit(1)
        data=hdf[dataset]
        attr=data.attrs
        self.nrows=int(attr['nrows'])
        self.ncols=int(attr['ncols'])
        self.x=float(attr['xcorner'])
        self.y=float(attr['ycorner'])
        self.nodata=int(attr['nodata'])
        self.csize=float(attr['csize'])
        self.mat=np.reshape(data.value,(self.nrows,self.ncols))
        hdf.close()
        if(DEBUG==1):
            print("nrows\t", self.nrows)
            print("ncols\t", self.ncols)
            print("xllcorner\t", self.x)
            print("yllcorner\t", self.y)
            print("cellsize\t", self.csize)
            print("nodata\t", self.nodata)
        return True
    def write_hdf(self,str filename,str dataset,str model, str author):
        """ write an grid to a hdf """
        cdef str s
        f = h5py.File(filename, 'a', libver='earliest')
        field=np.reshape(self.mat,self.nrows*self.ncols)
        data=f.create_dataset(dataset,data=field)
        attr=data.attrs
        attr['nrows']=int(self.nrows)
        attr['ncols']=int(self.ncols)
        attr['xcorner']=self.x
        attr['ycorner']=self.y
        attr['csize']=np.float32(self.csize)
        attr['nodata']=self.nodata
        s=self.date1
        if(s==str('\0')):
            s=datetime.date.today().isoformat()
        attr['date']= <str> s
        s=self.time1
        if(s==str('\0')):
            t=t=datetime.datetime.now()
            s=datetime.time(t.hour,
                            t.minute,
                            t.second).isoformat()
        attr['time']= <str> s
        attr['Author']=author
        attr['Modell']=model
        f.flush()
        f.close()
        return True
    # create random arrays as additional input method ======================
    def randfloat(self):
        """ generates a random mat using float32 numbers """
        self.mat=np.float32(np.random.rand(self.nrows,self.ncols))
        return True
    def randint(self, int min=0, int max=10):
        """ generate a random mat using int numbers """
        self.mat=np.float32(np.random.randint(min,max,size=
                                              (self.nrows,self.ncols)))
        return True
    def randn(self):
        """ generates a random N(0,1) array """
        self.mat=np.float32(np.random.randn(self.nrows,self.ncols))
        return True
    def resize(self,int nrows, int ncols):
        """ resizes a grid to the new nrows and ncols using a
            spline interpolation
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mx=self.mat
        cdef np.ndarray[DTYPE_t,ndim=1] x=np.arange(self.nrows).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=1] y=np.arange(self.ncols).astype(np.float32)
        if(nrows<=2 or ncols<=2):
            return False
        if(nrows<self.nrows or ncols<self.ncols):
            iter=RectBivariateSpline(x, y, mx,kx=2,ky=2)
        else:
            iter=RectBivariateSpline(x, y, mx)
        x=np.linspace(0,self.nrows,nrows).astype(np.float32)
        y=np.linspace(0,self.ncols,ncols).astype(np.float32)
        mx=(iter.__call__(x,y)).astype(np.float32)
        self.csize*=float(self.nrows)/nrows
        self.nrows=nrows
        self.ncols=ncols
        self.mat=mx
        return True
    # access to a grid for print or as copy ================================
    def print_mat(self, int i0=0, int i1=0, int j0=0, int j1=0):
        """ print a selected part of the matrix """
        if(i0==0 and i1==0 and j0==0 and j1==0):
            print(self.mat)
            return True
        else:
            if(not (i0>=0 and i1<=self.nrows and j0>=0 and j1<=self.ncols)):
                return False
            print(self.mat[i0:i1,j0:j1])
            return True
    def save_color(self, str name):
        """ save the matrix as color image """
        cdef int i,j
        cdef double gridmin, gridmax
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        if(self.nrows<=0 or self.ncols<=0):
            return False
        gridmax=-np.finfo(np.double).max
        gridmin=np.finfo(np.double).max
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])!=self.nodata and mx[i,j]<gridmin):
                    gridmin=mx[i,j]
                if(int(mx[i,j])!=self.nodata and mx[i,j]>gridmax):
                    gridmax=mx[i,j]
        print('show:', gridmin, gridmax, self.nodata)
        fig1 = plt.figure()
        cmap = plt.get_cmap('jet', 500)
        cmap.set_under('white')
        img=plt.imshow(mx,cmap=cmap)
        img.set_clim(gridmin,gridmax)
        plt.colorbar(cmap=cmap)
        plt.axis('off')
        fig1.savefig(name,bbox_inches='tight')
        del mx
        return True
    def save_bw(self, str name):
        """ save the matrix as black and white image """
        cdef int i,j
        cdef double gridmin, gridmax
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        if(self.nrows<=0 or self.ncols<=0):
            return False
        gridmax=-np.finfo(np.double).max
        gridmin=np.finfo(np.double).max
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])!=self.nodata and mx[i,j]<gridmin):
                    gridmin=mx[i,j]
                if(int(mx[i,j])!=self.nodata and mx[i,j]>gridmax):
                    gridmax=mx[i,j]
        print('save_bw:', gridmin, gridmax, self.nodata)
        fig1 = plt.figure()
        cmap = plt.get_cmap('Greys', 500)
        cmap.set_under('white')
        img=plt.imshow(mx,cmap=cmap)
        img.set_clim(gridmin,gridmax)
        plt.colorbar(cmap=cmap)
        plt.axis('off')
        fig1.savefig(name,bbox_inches='tight')
        del mx
        return True
    # access to the internal data =========================================
    def get(self,int i, int j):
        """ returns a single value from the matrix """
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        return mat[i,j]
    def set(self,int i, int j, DTYPE_t val):
        """ set a single values """
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        mat[i,j]=val
        return True
    def set_all(self,DTYPE_t val):
        """ set all values """
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        mat[:,:]=val
        return True
    def set_all_nd(self,DTYPE_t val):
        """ set all value exept nodata """
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j]!=self.nodata)):
                    mat[i,j]=val
        return True
    def size(self):
        """ returns the size: nrows, ncols """
        return self.nrows, self.ncols
    def get_datacells(self):
        """ returns the number of data cells """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        count=0
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])==self.nodata):
                    count+=1
        return self.nrows*self.ncols-count
    def get_nodata(self):
        """ returns the code for nodata """
        return self.nodata
    def set_nodata(self,val):
        """ replaces the old nodata with val """
        self.nodata=val
        return True
    def get_csize(self):
        """ returns the size of a grid cell """ 
        return self.csize
    def set_header(self, int nrows, int ncols, double x=0, double y=0,
                   double csize=1, int nodata=-9999):
        """ set the header with new values
            if self.mat is None define it and fill it with zeros
        """
        if(self.mat is None):
            self.nrows=nrows
            self.ncols=ncols
            self.mat=np.zeros((nrows,ncols))
        else:
            self.nrows=self.mat.shape[0]
            self.ncols=self.mat.shape[1]
        self.x=x
        self.y=y
        self.csize=csize
        self.nodata=nodata
        return True
    def get_header(self):
        """ returns the complete header as 6 numbers
        """
        return [self.nrows, self.ncols, self.x, self.y,
                self.csize, self.nodata]
    def clear_time(self):
        self.time1=str('\0')
        self.date1=str('\0')
        return True
    def set_date(self, datum):
        self.date1= <str> datum    # '04d-02d-02d' : year month day
        return True
    def set_time(self, zeit):
        self.time1= <str> zeit     # '02d:02d:02d' : hour min sec
        return True
    def get_matc(self, int i0=0, int i1=0, int j0=0, int j1=0):
        """ returns a copy of a part of the mat
        """
        if(i0==0 and i1==0 and j0==0 and j1==0):
            mx=np.copy(self.mat)
            return mx
        else:
            if(not (i0>=0 and i1<=self.nrows and j0>=0 and j1<=self.ncols)):
                return None
            mx=np.copy(self.mat[i0:i1,j0:j1])
            return mx
    def gen_mask(self,int i0, int i1, int j0, int j1):
        """ generates a mask of a grid filled with 1 all other are 0 """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat 
        if(not (i0>=0 and i1<=self.nrows and j0>=0 and j1<=self.ncols)):
            return False
        mat[:,:]=0.0
        mat[i0:i1,j0:j1]=1.0
        self.mat=mat
        return True
    def get_matp(self):
        """ returns a pointer to the matrix
        """
        return self.mat
    def set_mat(self,np.ndarray[DTYPE_t,ndim=2] mat1):
        """ replace the matrix of a grid with an external one
        """
        cdef int nr,nc
        (nr,nc)=np.shape(mat1)
        if(self.nrows!=nr or self.ncols!=nc):
            return False
        self.mat=mat1
        return True
    def set_nan(self):
        """ help function replaces the nodata value with np.nan """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat 
        mat[mat==self.nodata]=np.nan
        return True
    def reset_nan(self):
        """ help function replaces nans with self.nodata """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        mat[np.isnan(mat)]=self.nodata
        return True
    # show the data =======================================================
    def show_hist(self,int b1=20, int flag=0):
        """ plot a hist using b1=20 as number of bins
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef int i,j 
        if(self.nrows<=0 or self.ncols<=0):
            return None
        img=[]
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    img.append(mat[i,j])
        if(flag!=0):
            return img
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        plt.grid(True)
        plt.hist(img,b1,normed=False,color = 'r')
        plt.xlabel('data')
        plt.ylabel('frequency')
        plt.title('Histogram')
        plt.show()
        return True
    def showi(self):
        """ show a grid using ion() """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mx=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        plt.ion()
        plt.imshow(mx)
        plt.draw()
        return True
    def show_diff(self, grid g1, int flag=0):
        """ shows the difference between gx and g1 """
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        cdef np.ndarray[DTYPE_t,ndim=2] m1=g1.get_matc()
        cdef int i,j
        cdef int nrows,ncols,nodata
        nrows,ncols=g1.size()
        nodata=g1.get_nodata()
        if(self.nrows != nrows or self.ncols != ncols):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])==self.nodata or int(m1[i,j])==nodata):
                    mx[i,j]=self.nodata
                else:
                    mx[i,j]-=m1[i,j]
        if(flag==1):
            return mx
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        cmap = plt.get_cmap('jet', 500)
        cmap.set_under('white')
        img=plt.imshow(mx,cmap=cmap)
        # img.set_clim(gridmin,gridmax)
        plt.colorbar(cmap=cmap)
        plt.title('Diff')
        plt.show()
        del mx
        return True
   
    def show(self, sub1=False,title='', X='', Y='',flag=0):
        """ shows color with options title, X,Y only pos values"""
        cdef int i,j
        cdef double gridmin, gridmax
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        if(self.nrows<=0 or self.ncols<=0):
            return False
        if(sub1==True):
            mx=np.copy(self.sub)
        gridmax=-np.finfo(np.double).max
        gridmin=np.finfo(np.double).max
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])!=self.nodata and mx[i,j]<gridmin):
                    gridmin=mx[i,j]
                if(int(mx[i,j])!=self.nodata and mx[i,j]>gridmax):
                    gridmax=mx[i,j]
        if(flag==1):
            return mx
        print('show:', gridmin, gridmax, self.nodata)
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        cmap = plt.get_cmap('jet', 500)
        cmap.set_under('white')
        img=plt.imshow(mx,cmap=cmap)
        img.set_clim(gridmin,gridmax)
        plt.colorbar(cmap=cmap)
        if(title==''):
            plt.title('nrows:' + str(self.nrows) + ' ncols:' + str(self.ncols))
        else:
            plt.title(title)
        if(X!=''):
            plt.xlabel(X)
        if(Y!=''):
            plt.ylabel(Y)
        plt.show()
        del mx
        return True

    def show_p(self,x,y,color='k',size=None, t='', X='', Y='',flag=0):
        """
        adds to an image made from show a set of point with the
        colors = 'r', 'g', 'b', 'k', 'w'
        and a size the matplotlib size as default: 20
        t : title
        X : x-axis
        Y : y-axis
        flag : for internal use only 
        """
        cdef int i,j
        cdef double gridmin, gridmax
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        if(self.nrows<=0 or self.ncols<=0):
            return False
        gridmax=-np.finfo(np.double).max
        gridmin=np.finfo(np.double).max
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])!=self.nodata and mx[i,j]<gridmin):
                    gridmin=mx[i,j]
                if(int(mx[i,j])!=self.nodata and mx[i,j]>gridmax):
                    gridmax=mx[i,j]
        if(flag!=0):
            return mx,gridmin,gridmax  # for internal use only
        print('show:', gridmin, gridmax, self.nodata)
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        cmap = plt.get_cmap('jet', 500)
        cmap.set_under('white')
        img=plt.imshow(mx,cmap=cmap)
        img.set_clim(gridmin,gridmax)
        plt.colorbar(cmap=cmap)
        if(t==''):
            plt.title('nrows:' + str(self.nrows) + ' ncols:' + str(self.ncols))
        else:
            plt.title(t)
        if(X!=''):
            plt.xlabel(X)
        if(Y!=''):
            plt.ylabel(Y)
        if size is None:
            plt.scatter(x,y,c=color,alpha=1.0)
        else:
            plt.scatter(x,y,c=color,s=size,alpha=1.0)
        plt.show()
        del mx
        return True
       
    def show_bw(self, sub1=False, title='', X='', Y=''):
        """ shows bw with options title, X,Y """
        cdef int i,j
        cdef double gridmin, gridmax
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        if(self.nrows<=0 or self.ncols<=0):
            return False
        if(sub1==True):
            mx=np.copy(self.sub)
        gridmax=-np.finfo(np.double).max
        gridmin=np.finfo(np.double).max
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])!=self.nodata and mx[i,j]<gridmin):
                    gridmin=mx[i,j]
                if(int(mx[i,j])!=self.nodata and mx[i,j]>gridmax):
                    gridmax=mx[i,j]
        print('show:', gridmin, gridmax, self.nodata)
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        cmap = plt.get_cmap('Greys', 500)
        cmap.set_under('white')
        img=plt.imshow(mx,cmap=cmap)
        img.set_clim(gridmin,gridmax)
        plt.colorbar(cmap=cmap)
        if(title==''):
            plt.title('nrows:' + str(self.nrows) + ' ncols:' + str(self.ncols))
        else:
            plt.title(title)
        if(X!=''):
            plt.xlabel(X)
        if(Y!=''):
            plt.ylabel(Y)
        plt.show()
        del mx
        return True
    def show_3d(self, int stride=-1, sub1=False, title='', X='', Y='',flag=0):
        """ shows a grid using 3D: stride should be so that the
            grid size is approx 50..80 it will be adapted
        """
        cdef int i,j
        cdef double gridmin, gridmax,d
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        cdef np.ndarray[ITYPE_t,ndim=1] Xt,Yt
        cdef np.ndarray[ITYPE_t,ndim=2] X1,Y1
        if(self.nrows<=0 or self.ncols<=0):
            return None
        if(sub1==True):
            mx=np.copy(self.sub)
        if(stride==-1):
            stride=int(max(self.nrows,self.ncols)/60.0)
        if(stride<1):
            stride=1
        
        gridmax=-np.finfo(np.double).max
        gridmin=np.finfo(np.double).max
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])!=self.nodata and mx[i,j]<gridmin):
                    gridmin=mx[i,j]
                if(int(mx[i,j])!=self.nodata and mx[i,j]>gridmax):
                    gridmax=mx[i,j]
        d=gridmin-(gridmax-gridmin)/100.0
        print('show:', gridmin, gridmax, self.nodata)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])==self.nodata):
                    mx[i,j]=d
        if(flag!=0):
            return mx
        plt.ioff()
        plt.clf()
        mx=mx.transpose()
        Xt = np.arange(0,self.nrows)
        Yt = np.arange(0,self.ncols)
        X1, Y1 = np.meshgrid(Xt, Yt)
        ax=plt.subplot(111, projection='3d')
        ax.plot_surface(X1, Y1, mx, 
                        rstride=stride, 
                        cstride=stride, 
                        cmap='jet', 
                        linewidth=0, 
                        antialiased=True)
        if(title==''):
            plt.title('nrows:' + str(self.nrows) + ' ncols:' + str(self.ncols))
        else:
            plt.title(title)
        if(X!=''):
            plt.xlabel(X)
        if(Y!=''):
            plt.ylabel(Y)
        plt.show()
        return True
    def show_contour(self,sub1=False,title='',X='',Y='',clines=6,flag=0):
        """ shows a grid using a contour plot,
            default clines= number of contour lines
        """
        cdef int i,j,cl
        cdef double gridmin, gridmax,d
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        cdef np.ndarray[ITYPE_t,ndim=1] Xt,Yt
        cdef np.ndarray[ITYPE_t,ndim=2] X1,Y1
        cl=clines
        if(self.nrows<=0 or self.ncols<=0):
            return None
        if(sub1==True):
            mx=np.copy(self.sub)
        gridmax=-np.finfo(np.double).max
        gridmin=np.finfo(np.double).max
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])!=self.nodata and mx[i,j]<gridmin):
                    gridmin=mx[i,j]
                if(int(mx[i,j])!=self.nodata and mx[i,j]>gridmax):
                    gridmax=mx[i,j]
        d=gridmin-(gridmax-gridmin)/100.0
        print('show:', gridmin, gridmax, self.nodata)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])==self.nodata):
                    mx[i,j]=d
        if(flag!=0):
            return mx
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        cmap=plt.get_cmap('jet',500)
        cmap.set_under('white')
        im = plt.imshow(mx,cmap=cmap)
        Xt = np.arange(0,self.nrows)
        Yt = np.arange(0,self.ncols)
        X1, Y1 = np.meshgrid(Yt, Xt)
        # drawing the function
        cset = plt.contour(X1,Y1,mx,cl,linewidths=1,colors='k')
        plt.clabel(cset,inline=True,fmt='%1.3f',fontsize=10)
        plt.colorbar(im) # adding the colobar on the right

        if(title==''):
            plt.title('nrows:' + str(self.nrows) + ' ncols:' + str(self.ncols))
        else:
            plt.title(title)
        if(X!=''):
              plt.xlabel(X)
        if(Y!=''):
            plt.ylabel(Y)
        plt.show()
        return True
    def shows(self, vals1, int flag=0):
        """ shows all regions which are in the array: vals
        """
        cdef int i,j,x,y
        cdef double mi,ma
        cdef np.ndarray[ITYPE_t,ndim=1] vals=np.array(vals1,dtype=np.int)
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        cdef DTYPE_t gridmin=np.min(vals)-1.0
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])==self.nodata or (not (int(mx[i,j]) in vals))):
                    mx[i,j]=self.nodata
        if(flag==1):
            return mx
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        cmap = plt.get_cmap('jet', 500)
        cmap.set_under('white')
        img=plt.imshow(mx,cmap=cmap)
        (x,y,mi)=self.get_min()
        (x,y,ma)=self.get_max()
        img.set_clim(mi,ma)
        plt.colorbar(cmap=cmap)
        plt.title('nrows:' + str(self.nrows) + ' ncols:' + str(self.ncols))
        plt.show()
        del mx
        return True
    def showr(self,DTYPE_t val1, DTYPE_t val2, int flag=0, int bw=0):
        """ shows all in [val1,val2]
        """
        cdef int i,j,x,y
        cdef double mi,ma
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mx[i,j])==self.nodata or mx[i,j]<val1 or mx[i,j]>val2):
                    mx[i,j]=self.nodata
        if(flag==1):
            return mx
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        cmap = plt.get_cmap('jet', 500)
        if(bw==0):
            cmap = plt.get_cmap('Greys', 500)
        cmap.set_under('white')
        img=plt.imshow(mx,cmap=cmap)
        (x,y,mi)=self.get_min()
        (x,y,ma)=self.get_max()
        img.set_clim(mi,ma)
        plt.colorbar(cmap=cmap)
        plt.title('nrows:' + str(self.nrows) + ' ncols:' + str(self.ncols))
        plt.show()
        del mx
        return True
    def show_transect(self,int i0,int j0,int i1,int j1, int flag=0):
        """ shows a transect fron loc0=(i0,j0) to loc1=(i1,j1)
            flag=1 : returns the transect without showing
        """
        cdef int i,j,num
        num=int(np.sqrt((i1-i0)*(i1-i0)+(j1-j0)*(j1-j0)))
        cdef np.ndarray[DOUBLE_t,ndim=1] y=np.linspace(i0, i1, num)
        cdef np.ndarray[DOUBLE_t,ndim=1] x=np.linspace(j0, j1, num)
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        cdef np.ndarray[DOUBLE_t,ndim=1] t
        if(i0<0 or j0<0 or i1>=self.nrows or j1>=self.ncols):
            return None,None
        zi = scipy.ndimage.map_coordinates(np.transpose(mx), 
                                           np.vstack((x,y)),order=1)
        t=np.arange(len(zi))*self.csize
        if(flag==1):
            return t,zi
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        plt.plot(t,zi)
        plt.title("from: x0=%d,x1=%d to y0=%d,y1=%d" % (j0,j1,i0,i1))
        plt.ylabel('y')
        plt.xlabel('s')
        plt.grid(True)
        plt.show()
        return True
    def show_cwt(self,int i0,int j0,int i1,int j1, int l=0, int flag=0):
        """ shows a cwt transformation "ricker" as an image of the transect
        """
        cdef int i,j,num
        num=int(np.sqrt((i1-i0)*(i1-i0)+(j1-j0)*(j1-j0)))
        cdef np.ndarray[DOUBLE_t,ndim=1] y=np.linspace(i0, i1, num)
        cdef np.ndarray[DOUBLE_t,ndim=1] x=np.linspace(j0, j1, num)
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        cdef np.ndarray[DOUBLE_t,ndim=2] cwtmatr
        cdef np.ndarray[DOUBLE_t,ndim=1] t
        if(i0<0 or j0<0 or i1>=self.nrows or j1>=self.ncols):
            return None,None
        zi = scipy.ndimage.map_coordinates(np.transpose(mx), 
                                           np.vstack((x,y)),order=1)
        t=np.arange(len(zi))*self.csize
        if(l==0):
            widths = np.arange(1, int(num/2))
        else:
            widths = np.arange(1, l)
        cwtmatr = signal.cwt(zi, signal.ricker, widths)
        if(flag==1):
            return cwtmatr
        plt.ioff()
        plt.clf()
        plt.subplot(111)
        gridmin=np.min(cwtmatr)
        gridmax=np.max(cwtmatr)
        cmap = plt.get_cmap('jet', 500)
        cmap.set_under('white')
        img=plt.imshow(cwtmatr,cmap=cmap)
        img.set_clim(gridmin,gridmax)
        plt.colorbar(cmap=cmap)
        plt.title("CWT ricker")
        plt.xlabel("s")
        plt.ylabel("cwt")
        plt.show()
    # statistics ==========================================================
    def info(self):
        """
        prints the header of a grid
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef int i,j
        cdef int data=0, nodata=0
        print('nrows:',self.nrows)
        print('ncols:', self.ncols)
        print('xllcorner:',self.x)
        print('yllcorner:',self.y)
        print('csizesize:',self.csize)
        print('NODATA_value:',self.nodata)
        if((mat is None) or self.nrows<=0 or self.ncols<=0):
            return
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    nodata+=1
                else:
                    data+=1
        print('number of data:', data)
        print('number of nodata:', nodata)
        return True
    def mean_std(self):
        """ tells the mean and std """
        cdef double mean=0,mean2=0,std=0
        cdef int count=0
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return self.nodata, self.nodata
        if(len(np.where(self.mat==self.nodata)[0])==0):
            mean=np.mean(self.mat) 
            std=np.std(self.mat)
            return mean,std
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mean+=mat[i,j]
                    mean2+=mat[i,j]*mat[i,j]
                    count+=1
        mean/=count
        mean2/=count
        return mean, np.sqrt(mean2-mean**2)
    def get_minmax(self):
        """ returns the min and the maximum of the grid without nodata
        """
        cdef double minval=np.finfo(np.double).max
        cdef double maxval=np.finfo(np.double).min
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return self.nodata,self.nodata
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata and mat[i,j]<minval):
                    minval=mat[i,j]
                if(int(mat[i,j])!=self.nodata and mat[i,j]>maxval):
                    maxval=mat[i,j]
        return minval,maxval
    def get_min(self, double minval=np.finfo(np.double).max, int mark=-1):
        """ tells the minval and the position """
        cdef int i,j,x=-1, y=-1
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return x,y,self.nodata
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])>mark and mat[i,j]<minval):
                    x=i
                    y=j
                    minval=mat[i,j]
        return x,y,minval
    def get_max(self, int nodata=-9999):
        """ tells the maxval and the position """
        cdef float maxval=np.finfo(np.double).min
        cdef int i,j,x=-1, y=-1
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return x,y,self.nodata
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=nodata and mat[i,j]>maxval):
                    x=i
                    y=j
                    maxval=mat[i,j]
        return x,y,maxval
    def unique(self):
        """ return a dictionary with unic values (only useful for int) """
        cdef i,j
        if(self.nrows<=0 or self.ncols<=0):
            return None
        vals={}
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(self.mat[i,j])!=self.nodata):
                    if(not(int(self.mat[i,j]) in vals)):
                        vals[int(self.mat[i,j])]=1
                    else:
                        vals[int(self.mat[i,j])]+=1
        return vals
    def statr(self, float a=-9999.0, float b=-9999.0):
        """ returns the total, mean, std of all cells:
            a<=cell<=b
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef int i,j,count
        cdef float mean, mean2, sumx
        mean=0
        mean2=0
        count=0
        sumx=0
        if(a==-9999.0):
            a=np.finfo(np.float32).min
        if(b==-9999.0):
            b=np.finfo(np.float32).max
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata and a<=mat[i,j] and mat[i,j]<=b):
                    mean+=mat[i,j]
                    sumx+=mat[i,j]
                    mean2+=mat[i,j]*mat[i,j]
                    count+=1
        if(count<=2):
            return 0,0,0
        mean/=count
        mean2/=count
        mean2=np.sqrt(mean2-mean**2)
        return count,sumx,mean,mean2
    def corr(self,grid gx):
        """ calculates the correlation between two grids """
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat2=gx.get_matc()
        cdef int nodata=gx.get_nodata()
        cdef double xmean=0   # mean of self
        cdef double ymean=0   # mean of gx
        cdef double sx=0  
        cdef double sy=0  
        cdef double cov=0
        cdef int xcount=0
        cdef int ycount=0
        if(self.nrows!=gx.size()[0] or self.ncols!=gx.size()[1]):
            return 0
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat1[i,j])!=self.nodata and int(mat2[i,j])!=nodata):
                    xmean+=mat1[i,j]
                    xcount+=1
                    ymean+=mat2[i,j]
                    ycount+=1
        if(xcount==0 or ycount==0):
            return 0
        xmean/=xcount
        ymean/=ycount
        xcount=0
        ycount=0
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat1[i,j])!=self.nodata and int(mat2[i,j])!=nodata):
                    sx+=(mat1[i,j]-xmean)**2
                    sy+=(mat2[i,j]-ymean)**2
                    cov+=(mat1[i,j]+xmean)*(mat2[i,j]-ymean)
        return(cov/(np.sqrt(sx)*np.sqrt(sy)))
    def point_in(self,np.ndarray[ITYPE_t,ndim=1] x,
                 np.ndarray[ITYPE_t,ndim=1] y,
                 int i0, int j0, int k):
        """ help function with k=index """
        cdef int i,j
        if(k<2):
            return True
        for i in np.arange(k):
            if(x[i]==j0 and y[i]==i0):
                return False
        return True
    def sample(self,int nr=100,filename=None):
        """ very fast version now, uses:
            np.random.shuffle
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[ITYPE_t,ndim=1] x=np.zeros(nr,dtype=np.int)
        cdef np.ndarray[ITYPE_t,ndim=1] y=np.zeros(nr,dtype=np.int)
        cdef np.ndarray[np.double_t,ndim=1] z=np.zeros(nr)
        cdef np.ndarray[ITYPE_t,ndim=2] c=np.zeros((self.nrows*self.ncols,2),
                                                    dtype=np.int)
        cdef int i,j,k, count=0
        if(nr<1):
            return None,None,None
        # sample from data cells
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    c[count,0]=i
                    c[count,1]=j
                    count+=1
        # shuffle the coordinates
        if(count<nr):
            return None,None,None
        arr=c[0:count]
        np.random.shuffle(arr)
        # fill the outputs
        if(filename is None):
            for k in xrange(nr):
                x[k]=arr[k,1]
                y[k]=arr[k,0]
                z[k]=np.double(mat[y[k],x[k]])
            return y,x,z
        else:
            f=open(filename,'w')
            f.write("x y z\n")
            for k in xrange(nr):
                x[k]=arr[k,1]
                y[k]=arr[k,0]
                z[k]=np.double(mat[y[k],x[k]])
                s="%d %d %f\n" % (x[k],y[k],z[k])
                f.write(s)
            f.close()
            return y,x,z
    def sample_p(self, int nr, double p):
        """
        returns a ndarrays x,y with nr coordinates for
        with mat[i,j]>=p
        returns:
        y : ndarray(int) with rows (i)
        x : ndarray(int) with cols (j)
        z : ndarray(float32) with vals
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef int i,j
        cdef np.ndarray[ITYPE_t,ndim=1] x=np.array([],dtype=np.int)
        cdef np.ndarray[ITYPE_t,ndim=1] y=np.array([],dtype=np.int)
        cdef np.ndarray[DTYPE_t,ndim=1] z=np.array([],dtype=np.float32)
        if(nr<1):
            return None
        loc=[]  # list of locations
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(mat[i,j]>p):
                    loc.append((i,j))
        np.random.shuffle(loc)
        # fill the x,y,z
        for k in xrange(nr):
            i=loc[k][0]
            j=loc[k][1]
            x=np.append(x,j)
            y=np.append(y,i)
            z=np.append(z,np.float32(mat[i,j]))
        return y,x,z
        
    def sample_det(self, DTYPE_t val):
        """ returns ndarrays x,y with all coordinates for
            with mat[i,j]==val
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef int i,j
        cdef np.ndarray[ITYPE_t,ndim=1] x=np.array([],dtype=np.int)
        cdef np.ndarray[ITYPE_t,ndim=1] y=np.array([],dtype=np.int)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(mat[i,j]==val):
                    x=np.append(x,j)
                    y=np.append(y,i)
        return y,x
    def sample_neg(self, ix,jy, float radius, int n):
        """ samples all points in random order which are
            farther from all point of a given collection (i1,j1)
            the radius is given in number of cells
        """
        cdef np.ndarray[ITYPE_t,ndim=1] i1=np.array(ix,dtype=np.int)
        cdef np.ndarray[ITYPE_t,ndim=1] j1=np.array(jy,dtype=np.int)
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[ITYPE_t,ndim=2] z=np.zeros((self.nrows*self.ncols,2),
                                                   dtype=np.int)
        cdef int i,j,k,count,flag
        cdef float r=float(radius)**2
        # collect all points which are outside the radius
        count=0;
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                flag=0
                if(int(mat[i,j])!=self.nodata):
                    for k in xrange(len(i1)):
                        if((i-i1[k])*(i-i1[k])+
                           (j-j1[k])*(j-j1[k])<r):
                            flag=1
                            break
                    if(flag==0):
                        z[count,0]=i
                        z[count,1]=j
                        count+=1
        # select from cells
        if(count<=0):
            return None
        arr=z[0:count]           # select the non zeros
        np.random.shuffle(arr)   # shuffle the points
        return arr[0:n]
    # shannon indexgamma.astype(float)
    def shannon(self):
        """ calculates the shannon index over an normalized array
            x/sum(x)
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DOUBLE_t,ndim=1] x
        cdef int i,j
        cdef float s
        X=[]
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    X.append(mat[i,j])
        x=np.array(X)
        s=np.sum(x)  # normalze the data
        x=x/s
        # print 'shannon:',s,sum(x)
        return -np.sum(x[x>0]*np.log(x[x>0]))
     # shannon indexgamma.astype(float)
    def shannons(self,nr=30):
        """ calculates the scaled shannon index over an normalized array
            x/sum(x)
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DOUBLE_t,ndim=1] x
        cdef int i,j
        cdef float s
        X=[]
        if(nr<10):
            print 'error in get_shannons: nr=',nr,' must be >10 '
            return self.nodata
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    X.append(mat[i,j])
        h=np.histogram(X,bins=nr,density=True)
        x=h[0]
        s=np.sum(x)
        x=x.astype(float)
        x/=float(s)
        return -np.sum(x[x>0]*np.log(x[x>0]))/np.log(float(nr))
    # mixin after William Seitz ===========================================
    def histogram(self,mx,nr):
        """ help function replaces the numpy.histogram
            implements only positiv numbers (negativ will be normalized
            to 0..1)
        """
        cdef np.ndarray[DOUBLE_t,ndim=1] m=np.array(mx)
        cdef np.ndarray[ITYPE_t, ndim=1] im
        cdef int i
        m=m.astype(float)       # make sure that is float
        # normalize it check max!=min
        if(float(np.max(m)-np.min(m))!=0):
            m=(m-float(np.min(m)))/(float(np.max(m)-np.min(m)))
        else:
            print 'error in histogram: Min==Max'
        m*=(nr-1)                # put in range 0..n-1
        im=m.astype(int)         # transform it to int
        h={}                     # use a dict for histogram
        for i in xrange(len(im)):
            if im[i] in h:
                h[im[i]]+=1
            else:
                h[im[i]]=1
        return h.values()
    def mixin(self,int nr=30, int dis=0):
        """ takes a data set mx and generates a historgram
            if dis!=0 the data has to be discrete numbers
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef int i,j,k,l,nodata,data,delta
        cdef float dx   # is use to store the rest between int and float
        nodata=0
        data=0
        dx=0.0
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    nodata+=1
                else:
                    data+=1
        cdef np.ndarray[DOUBLE_t,ndim=1] mx=np.zeros(data) # collect only data
        k=0
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mx[k]=mat[i,j]
                    k+=1
        if(dis==0):                   # floating point values
            d1=self.histogram(mx,nr)      # new version of hist
            d1=np.array(d1)
        else:
            d1=np.array((self.unique()).values())
            nr=len(d1)
            if(nr<5 or nr>50):
                print 'error in unique values: ',nr,' wrong!'
                return None
        d1=d1.astype(float)       # transform it in a ndarray
        df=np.sort(float(nr)*d1/np.sum(d1))[::-1]  # nomalize float
        d1=np.round(df)
        d2=nr*np.ones(nr,dtype=int)  
        l=nr                           
        d2[0]=np.int(np.round(d1[0]))     # start with the first of d1[0] 
        for i in xrange(1,l):             # l is necessary
            delta=np.int(np.round(d1[i]+dx)) # transform the next of d1
            dx += (df[i]-delta)
            if(delta>=1):
                d2[i]=d2[i-1]+delta
            else:
                d2[i]=d2[i-1]+1
            if(d2[i]>l):
                    d2[i]=l
                    return d2
        return d2
    def majorization(self, grid g1, int nr=30, int dis=0):
        """ 
        majorization compares two grids according to:
        defines the majorization between two lists
        a_1 >= b_1
        a_1 + a_2 >= b_1 + b_2
        a_1 + a_2 + a_3 >= b_1 + b_2 + b_3
        ...
        a_1 + a_2 + ... + a_n-1 >= b_1 + b_2 + ... + b_n-1
        a_1 + a_2 + ... + a_n-1 + a_n >= b_1 + b_2 + ... + b_n-1 + b_n
        
        The data come out of a histogram or a unique and will be
        normalized using mixin before the majorization is applied.
        """
        cdef int f1,f2,j
        cdef np.ndarray[ITYPE_t,ndim=1] m1,m2
        m1=self.mixin(nr,dis)  # extract the mixin from the grid
        m2=g1.mixin(nr,dis)    # extract the mixin from g1
        #print m1
        #print m2
        f1=0
        f2=0
        for j in xrange(nr):
            if(m1[j]>m2[j]):
                f1=1
                break
        for j in xrange(nr):
            if(m1[j]<m2[j]):
                f2=1
                break
        if f1==1 and f2==1:
            return 0   # non comparable
        if f1==0 and f2==1:
            return -1  # m1<m2
        if f1==1 and f2==0:
            return 1   # m2<m1
        if f1==0 and f2==0:
            return self.nodata
    def gen_partition(self,int n, a, int level):
        """ helpfunction to generate the partition recurrent
        """
        a=np.copy(a)
        N=len(a)
        if(n<1):
            return
        a[level]=n
        swp=np.zeros(N)
        swp[0:(level+1)]=(a[::-1])[(N-level-1):N]
        self.partition[self.counter]=np.cumsum(swp)
        # self.partition[self.counter]=np.cumsum(a)
        self.counter+=1
        if(level==0):
            first=1
        else:
            first=a[level-1]
        for i in xrange(first,int(n/2+1.0)):
            a[level]=i
            self.gen_partition(n-i,a,level+1)
    def complexity(self, int nr=30, int dis=0):
        """ 
        The mixin will be compared with all 5604 possible
        partitions of nr=30 and the normlized incompareabel 
        will be returned
        The parameter dis=0 menas a floting point map is analyzed
        using a histogram, if dis=1 the unique() is used to extract the values.
        """
        cdef int i,j,k,l, n,f1,f2,clow,chigh,icomp
        self.counter=0
        trys={5 : 7,
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
              30: 5604,
              31: 6842,
              32: 8349,
              33: 10143,
              34: 12310,
              35: 14883,
              36: 17977,
              37: 21637,
              38: 26015,
              39: 31185,
              40: 37338,
              41: 44583,
              42: 53174,
              43: 63261,
              44: 75175,
              45: 89134,
              46: 105558,
              47: 124754,
              48: 147273,
              49: 173525,
              50: 204226}
        maxi={5: 0,
              6: 1,
              7: 2,
              8: 4,
              9: 7,
              10: 12,
              11: 19,
              12: 29,
              13: 42,
              14: 61,
              15: 87,
              16: 120,
              17: 164,
              18: 222,
              19: 297,
              20: 392,
              21: 515,
              22: 669,
              23: 866,
              24: 1109,
              25: 1415,
              26: 1792,
              27: 2265,
              28: 2838,
              29: 3550,
              30: 4413,
              31: 5475,
              32: 6751,
              33: 8314,
              34: 10043,
              35: 12460,
              36: 15169,
              37: 18444,
              38: 22332,
              39: 27012,
              40: 32538,
              41: 39156,
              42: 46955,
              43: 56250,
              44: 67162,
              45: 80119,
              46: 95288,
              47: 113229,
              48: 134173,
              49: 158850,
              50: 187593}
        n=nr
        if(n<5 or n>50):
            print 'error in complexity: use a nr in [6,50]'
            return -9999
        mixin=self.mixin(n,dis)
        if(mixin is None):
            return self.nodata
        n=len(mixin)
        a=[0 for i in range(n)]
        self.partition=np.zeros((trys[n],n))
        self.gen_partition(n,a,0)
        comp_counter=0
        cdef float delta=0.0
        self.partition=self.partition.astype(int)
        clow=0
        chigh=0
        icomp=0
        for i in xrange(trys[n]):
            f1=0
            f2=0
            for j in xrange(n):
                if(self.partition[i,j]>mixin[j]):
                    f1=1
                    break
            for j in xrange(n):
                if(self.partition[i,j]<mixin[j]):
                    f2=1
                    break
            if f1==1 and f2==1:
               icomp+=1
            if f1==0 and f2==1:
                clow+=1
            if f1==1 and f2==0:
                chigh+=1
        print 'icomp:',icomp,' clow:',clow,' chigh:',chigh
        if(maxi[n]==0):
            return 0
        return float(icomp)/float(maxi[n])
            
    # simple destructive operations =======================================
    def norm(self):
        """
        normalize the grid according to: (x-min)/(max-min)
        remove the nodata before!
        """
        cdef double min1,max1,d
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        min1=np.min(mat[mat>self.nodata])
        max1=np.max(mat[mat>self.nodata])
        d=max1-min1
        print('norm:' , min1, max1, d)
        if(d!=0.0):
            mat[mat>self.nodata]=(mat[mat>self.nodata]-min1)/d
            return True
        return False
    def znorm(self):
        """ normalizes the grid accrding to:
            z=(mat-mean(mat))/std(mat)
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef double mu=np.mean(mat[mat>self.nodata])
        cdef double std=np.std(mat[mat>self.nodata])
        print('znorm mean:', mu,'std:', std)
        if(std!=0):
            mat[mat>self.nodata]=(mat[mat>self.nodata]-mu)/std
            return True
        return False
    def replace(self,double val1, double val2):
        """ replace the val1 with val2
        """
        if(self.nrows<=0 or self.ncols<=0):
            return False
        self.mat[self.mat==val1]=val2
        return True
    def set_all(self, float val, int nodata=0):
        """ set  all values to a const """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        if(nodata==0 and len(np.where(self.mat==self.nodata)[0])==0):
            self.mat[:,:]=val
            return True
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(nodata==0):
                    mat[i,j]=val
                else:
                    if(int(mat[i,j])!=self.nodata):
                        mat[i,j]=val
        return True
    def add(self, float val):
        """ add the grid with an float
        """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        if(len(np.where(mat==self.nodata)[0])==0):
            self.mat[:,:]+=val
            return True
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mat[i,j]+=val
        return True
    def mul(self, float val):
        """ multiply the grid with a float 
        """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        if(len(np.where(mat==self.nodata)[0])==0):
            self.mat[:,:]*=val
            return True
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mat[i,j]*=val
        return True
    def mul_add(self, float mul, float add):
        """ multiply and add the grid with floats 
        """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        if(len(np.where(mat==self.nodata)[0])==0):
            mat[:,:]=mat[:,:]*mul+add
            return True
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mat[i,j]=mat[i,j]*mul+add
        return True
    def log(self,double d=1.0):
        """ calculates the lg(d+x) for all x>=0
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        mat[mat<0]=0.0
        self.mat=np.log10(d+mat)
        return True
    def ln(self,double d=1.0):
        """ calculates the ln(d+x) for all x>=0
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        mat[mat<0]=0.0
        self.mat=np.log(d+mat)
        return True
    def fabs(self):
        """ calculates the fabs of a grid
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        mat[mat!=self.nodata]=np.fabs(mat[mat!=self.nodata])
        self.mat=mat
        return True
    def sign(self):
        """ if g<0 0 else 1
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        mat[mat!=self.nodata]=np.sign(mat[mat!=self.nodata])
        self.mat=mat
        return True
   # complex destructive operations =====================================
    def inv(self):
        """ invert a grid between min and max """
        cdef int i,j,x,y
        cdef double gridmax, gridmin
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        (x,y,gridmax)=self.get_max()
        gridmin=gridmax
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    if(gridmin>mat[i,j]):
                        gridmin=mat[i,j]
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mat[i,j]=gridmax-mat[i,j]+gridmin
        return True
    def inv_ab(self,double a):
        """
        a=upper limit of interval
        """
        cdef double gridmax=a
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mat[i,j]=(gridmax-mat[i,j])
        return True
    def lut(self, table):
        """ apply a lukup table to a grid """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata or not (int(mat[i,j]) in table)):
                    continue
                mat[i,j]=table[int(mat[i,j])]
        return True
    def select(self, vals_arr, int val1=1, int val2=0):
        """ set all values in vals to val1 else to val0 """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=1] vals=np.array(vals_arr).astype('float32')
        if(self.nrows<=0 or self.ncols<=0):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    continue
                if(int(mat[i,j]) in vals):
                    mat[i,j]=val1
                else:
                    mat[i,j]=val2
        return True
    def border(self,int val):
        """ collects all cells in an dict{cell,freq} which are
            in d4 neighborhood of the cell with mat==val
        """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return None
        lut={}
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    continue
                if(int(mat[i,j])==val):
                    if(i>0 and int(mat[i-1,j])!=val):
                        if(int(mat[i-1,j]) in lut):
                            lut[int(mat[i-1,j])]+=1
                        else:
                            lut[int(mat[i-1,j])]=1
                    if(j+1<self.ncols and int(mat[i,j+1])!=val):
                        if(int(mat[i,j+1]) in lut):
                            lut[int(mat[i,j+1])]+=1
                        else:
                            lut[int(mat[i,j+1])]=1
                    if(i+1<self.nrows and int(mat[i+1,j])!=val):
                        if(int(mat[i+1,j]) in lut):
                            lut[int(mat[i+1,j])]+=1
                        else:
                            lut[int(mat[i+1,j])]=1
                    if(j>0 and int(mat[i,j-1])!=val):
                        if(int(mat[i,j-1]) in lut):
                            lut[int(mat[i,j-1])]+=1
                        else:
                            lut[int(mat[i,j-1])]=1
        return lut
    def cond(self, float min, float max, float min1=-9999, float max1=-9999):
        """ retrict all values in the range from [min,max] """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    if(mat[i,j]<min):
                        mat[i,j]=min1
                        continue
                    if(mat[i,j]>max):
                        mat[i,j]=max1
        return True
    def cut(self, float max1, float val=-9999):
        """ clamps the max or set it to nodata """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    if(mat[i,j]>=max1):
                        mat[i,j]=val
        return True
    def cut_off(self,float min,float max,float val=-9999):
        """ removes all values in the range from [min,max) """
        cdef int i,j
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    if(mat[i,j]>=min and mat[i,j]<max):
                        mat[i,j]=val
        return True
    def classify(self,int nr=10):
        """ classify a continous range [min,max] in a set {c1,c2,c3,...cnr}
        """
        cdef int i,j
        cdef double min1,max1,d
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(nr<2):
            return False
        min=np.finfo(np.double).max
        max=np.finfo(np.double).min
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    continue
                if(mat[i,j]<min1):
                    min1=mat[i,j]
                if(mat[i,j]>max1):
                    max1=mat[i,j]
        max1=np.round(max1)
        min1=np.round(min1)
        d=(max1-min1)*1.001 # small delta
        print('classify:',min1,max1,d)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    continue
                mat[i,j]=int(nr*(mat[i,j]-min1)/d)
        return True
    def reclass(self,m,k):
        """ reclass the grid using m and k """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=np.copy(self.mat)
        cdef int i
        if(len(m)!=len(k)):
            return False
        for i in np.arange(len(m)):
            t=(mat<=m[i])
            mat[t]=np.nan
            mat1[t]=k[i]
        self.mat=mat1
        return True
    # minimal variance partition= =========================================
    def varpart(self,nr=5000):
        """ part a grid in nr=5000 rectangular region with min var 
            criterion
        """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef int i,d,flag=0,count=0
        cdef double var1, var2
        cdef float mean
        var_dict={}
        rect_arr={}
        r0=rect(0,self.nrows,0,self.ncols)  # the complete grid
        rect_arr[0]=r0                 # add the grid
        var_dict[0]=np.var(mat)        # add the variance
        for i in xrange(nr):
            d=max(var_dict.iteritems(), key=operator.itemgetter(1))[0]
            r0=rect_arr.pop(d)         # remove the largest subarray
            var_dict.pop(d)            # remove the old variance
            if((r0.i2()-r0.i1()) > (r0.j2()-r0.j1())):
                if((r0.i2()-r0.i1())<2):
                    flag=1             # smallest rect are reached
                    break
                r1=rect(r0.i1(),r0.i1()+int((r0.i2()-r0.i1())/2),
                        r0.j1(),r0.j2())
                r2=rect(r0.i1()+int((r0.i2()-r0.i1())/2),r0.i2(),
                        r0.j1(),r0.j2())
            else:
                if((r0.j2()-r0.j1())<2):
                    flag=1             # smallest rect are reached
                    break
                r1=rect(r0.i1(),r0.i2(),
                        r0.j1(),r0.j1()+int((r0.j2()-r0.j1())/2))
                r2=rect(r0.i1(),r0.i2(),
                        r0.j1()+int((r0.j2()-r0.j1())/2),r0.j2())
            var1=np.var(mat[r1.i1():r1.i2(),r1.j1():r1.j2()])
            var2=np.var(mat[r2.i1():r2.i2(),r2.j1():r2.j2()])
            # save the new rects
            rect_arr[count]=r1
            var_dict[count]=var1
            count+=1                 # increment count
            rect_arr[count]=r2
            var_dict[count]=var2
            count+=1                 # increment count+=2
        # all rects were collected
        # fill the rects with mean values
        dist=[]
        for i in rect_arr.keys():
            mean=np.mean(mat[rect_arr[i].i1():rect_arr[i].i2(),
                             rect_arr[i].j1():rect_arr[i].j2()])
            dist.append((rect_arr[i].i2()-rect_arr[i].i1())*
                        (rect_arr[i].j2()-rect_arr[i].j1()))
            mat[rect_arr[i].i1():rect_arr[i].i2(),
                rect_arr[i].j1():rect_arr[i].j2()]=mean
        return dist
                     
    # maximum subarray= ===================================================
       # help function is used inside of max_subarray
    def kadane(self,np.ndarray[DTYPE_t, ndim=1] input):
        """ help function for max. subarray """
        cdef int i,lx1=0
        cdef double maxx=0.0, cur=0.0
        self.x1=0
        self.x2=0  
        for i in xrange(len(input)):
            cur += input[i]  
            if(cur > maxx):  
                maxx = cur  
                self.x2 = i  
                self.x1 = lx1  
            if (cur < 0):  
                cur = 0  
                lx1 = i + 1  
        return maxx
    def max_subarray_list(self, double thresh=0, int n=1):
        """ maximum subarray main function """
        cdef int i,k,j,fx1,fx2,fy1,fy2
        cdef double max_sum,cur,summ,mean,std,min1
        cdef np.ndarray[DTYPE_t,ndim=2] sub=np.copy(self.mat)
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        min1=-9999.0
        for i in xrange(n):
            if(thresh==0):
                thresh=np.mean(sub)
            sub-=thresh
            tmp=np.zeros(self.ncols,dtype=DTYPE)
            fx1=fx2=fy1=fy2=max_sum=cur=-1
            for i in xrange(self.nrows):
                for k in xrange(self.ncols):
                    tmp[k]=0.0
                for j in xrange(i,self.nrows):
                    for k in range(self.ncols):
                        tmp[k]+=sub[j,k]
                    cur=self.kadane(tmp)
                    if(cur>max_sum):
                        fy1=self.x1
                        fy2=self.x2
                        fx1=i
                        fx2=j
                        max_sum=cur
            fx2+=1
            fy2+=1
            print(fx1,fx2,fy1,fy2)
            summ=np.sum(mat[fx1:fx2,fy1:fy2])
            mean=np.mean(mat[fx1:fx2,fy1:fy2])
            std=np.std(mat[fx1:fx2,fy1:fy2])
            print(max_sum, summ, (fx2-fx1)*(fy2-fy1), mean, std)
            sub+=thresh
            sub[fx1:fx2,fy1:fy2]=min1
            self.sub=sub
        return True
    # trend and kernel techniques =========================================
    # removes the trend of a layer in both directions (x,y)
    # using a lineare multiple regression with numpy.linalg.lstsq
    # new version can handle nodata values 16.9.2014
    def remove_trend(self, int nr=2000):  # use 2000 sample points
        """ remove the trend from a map using a linear regression """
        cdef np.ndarray A,y
        cdef int i,j,k,l,flag
        cdef double a,b,c,minval
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(self.nrows<=0 or self.ncols<=0):
            return False
        A=np.zeros((nr,3),dtype=np.double)           # matrix for the data
        y=np.zeros(nr,dtype=np.double)               # vector with heights
        # sample it
        k=0
        while k<nr:
            flag=0
            i=np.random.randint(self.nrows)
            j=np.random.randint(self.ncols)
            if(int(mat[i,j])!=self.nodata):
                y[k]=self.mat[i,j]
                A[k,0]=i
                A[k,1]=j
                A[k,2]=1
                for l in xrange(k):
                    if(A[l,0]==A[k,0] and A[l,1]==A[k,1]):
                        flag=1
                if(flag==1):
                    continue
                k+=1
        # calc the regression
        a,b,c=np.linalg.lstsq(A,y)[0]
        print('a:',a,'b:',b,'c:',c)
        # remove the trend from the map
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mat[i,j]-=(a*i+b*j+c)
        # new minval
        (a,b,minval)=self.get_min()
        print('minval:',minval)
        # add minval
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    mat[i,j]-=minval
        return True
    def kernel(self, np.ndarray[DTYPE_t, ndim=2] w):
        """ simple kernel implementation with a kernel
             from the outside
        """
        cdef np.ndarray[DTYPE_t, ndim=2] res
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef int i,j,i1,j1,di,dj
        cdef double size
        res=signal.convolve2d(mat,w,boundary='symm')
        # reorganize the mat
        (i1,j1)=np.shape(res)
        di=int((i1-self.nrows)/2)
        dj=int((j1-self.ncols)/2)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                self.mat[i,j]=np.sqrt(res[i+di,j+dj])
        return True
    def kernel_sci(self,int ai, int bj,double sigma=1.0):
        """ gaussian kernel """
        cdef np.ndarray[DTYPE_t, ndim=2] w, res
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef int i,j,ai0,bj0
        if(ai%2==0): ai+=1 # guarantie odd numbers
        if(bj%2==0): bj+=1
        size=float(ai*bj)
        if(ai>=self.nrows or ai<1 or bj>=self.ncols or bj<1):
            print('error in kernel_sci parameter:',ai,bj)
            return False
        # fill the array for convolution
        w=np.zeros((ai,bj),dtype=np.float32)
        ai0=ai/2
        bj0=bj/2
        size=0
        for i in xrange(ai):
            for j in xrange(bj):
                w[i,j]+=np.exp(-((i-ai0)**2+(j-bj0)**2)/sigma)
                size+=w[i,j]
        res=signal.convolve2d(mat,w,boundary='symm')
        # reorganize the mat
        (i1,j1)=np.shape(res)
        di=int((i1-self.nrows)/2)
        dj=int((j1-self.ncols)/2)
        size=np.sqrt(size)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                self.mat[i,j]=res[i+di,j+dj]/size
        return True
    def kernel_squ(self,int ai,int bj):
        """ kernel with a square """
        cdef np.ndarray[DTYPE_t, ndim=2] w, res
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef double size
        if(ai%2==0): ai+=1 # guarantie odd numbers
        if(bj%2==0): bj+=1
        size=float(ai*bj)
        if(ai>=self.nrows or ai<1 or bj>=self.ncols or bj<1):
            print('error in kernel_sci parameter:',ai,bj)
            return False
        # fill the array for convolution
        w=np.ones((ai,bj),dtype=np.float32)
        res=signal.convolve2d(mat,w,boundary='symm')
        # reorganize the mat
        (i1,j1)=np.shape(res)
        di=int((i1-self.nrows)/2)
        dj=int((j1-self.ncols)/2)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                self.mat[i,j]=res[i+di,j+dj]/size
                # self.mat[i,j]=np.sqrt(res[i+di,j+dj])
        return True
    # same as squ but using a circle
    def kernel_cir(self,int radius):
        """ circular kernel """
        cdef np.ndarray[DTYPE_t, ndim=2] w, res
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef double size
        cdef int r2=radius*radius
        cdef int ai=radius
        cdef int bj=radius
        cdef int i,j,i1,j1,di,dj
        if(ai%2==0): ai+=1 # guarantie odd numbers
        if(bj%2==0): bj+=1
        size=0
        if(ai>=self.nrows or ai<1 or bj>=self.ncols or bj<1):
            print('error in kernel_sci parameter:',ai,bj)
            return False
        # fill the array for convolution
        w=np.zeros((ai,bj),dtype=np.float32)
        for i in xrange(ai):
            for j in xrange(bj):
                if(i*i+j*j<r2):
                    w[i,j]=1.0
                    size+=1.0
        res=signal.convolve2d(mat,w,boundary='symm')
        # reorganize the mat
        (i1,j1)=np.shape(res)
        di=int((i1-self.nrows)/2)
        dj=int((j1-self.ncols)/2)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                self.mat[i,j]=res[i+di,j+dj]/size
        return True
    def knn(self,int k, float min1, float max1):
        """ selects all k neighbors of the cell(i,j) and
            classifies all k neighbors into:
            1 : if min1<=cell(k)<=max1
            0 : else
            the result is the majority of the k neighbors
        """
        cdef int i,j,i1,j1,i2,j2
        cdef int k1   # summarizes the counts
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        if(k%2==0):
            k+=1 # odd numbers
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    k1=0
                    for i1 in xrange(-k/2,k/2+1):
                        for j1 in xrange(-k/2,k/2+1):
                            j2=j+j1
                            i2=i+i1
                            if(i2>=0 and i2<self.nrows and
                                j2>=0 and j2<self.ncols):
                                if(int(mat[i2,j2])!=self.nodata):
                                    if(mat[i2,j2]>=min1 and
                                       mat[i2,j2]<=max1):
                                        k1+=1
                                    else:
                                        k1-=1
                    if(k1>0):
                        mx[i,j]=1
                    else:
                        mx[i,j]=0
        self.mat=mx
        return True
    # flood fill technique ==============================================
    def floodFill(self,int i,int j, float level1, int mark=-1):
        """ flood fill algorithm based on a stack implementation """
        cdef int count=0
        cdef double minval,level
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(i<0 or i>=self.nrows or j<0 or j>=self.ncols):
            return -9999
        toFill = set()
        toFill.add((i,j))
        minval=mat[i,j]
        level=level1+minval
        while len(toFill)>0:
            (i,j) = toFill.pop()
            if(int(mat[i,j])==self.nodata):
                continue
            if(int(mat[i,j])==mark):
                # count+=1
                continue
            if(mat[i,j]>level):
                continue
            self.mat[i,j]=mark
            count += 1
            if(i>0 and mat[i-1,j]>mark):
                toFill.add((i-1,j))
            if(i+1<self.nrows and mat[i+1,j]>mark):
                toFill.add((i+1,j))
            if(j>0 and mat[i,j-1]>mark):
                toFill.add((i,j-1))
            if(j+1<self.ncols and mat[i,j+1]>mark):
                toFill.add((i,j+1))
        return count
        
    def floodFills(self,int i,int j, float level1, int mark=-1):
        """ flood fill algorithm based on a stack implementation 
            returns the standard deviation
        """
        cdef int count=0, count1=0
        cdef double minval,level
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mx=np.copy(self.mat)
        cdef double xquer=0.0
        cdef double xquer2=0.0
        if(i<0 or i>=self.nrows or j<0 or j>=self.ncols):
            return -9999
        if(int(mat[i,j])==mark):
            return -9999,-9999
        toFill = set()
        toFill.add((i,j))
        minval=mat[i,j]
        level=level1+minval
        while len(toFill)>0:
            (i,j) = toFill.pop()
            if(int(mat[i,j])==self.nodata):
                continue
            if(int(mat[i,j])==mark):
                continue
            if(mat[i,j]>level):
                continue
            mat[i,j]=mark
            xquer += mx[i,j]
            xquer2 += (mx[i,j]*mx[i,j])
            count += 1
            count1 += 1
            if(i>0 and mat[i-1,j]>mark):
                toFill.add((i-1,j))
            if(i+1<self.nrows and mat[i+1,j]>mark):
                toFill.add((i+1,j))
            if(j>0 and mat[i,j-1]>mark):
                toFill.add((i,j-1))
            if(j+1<self.ncols and mat[i,j+1]>mark):
                toFill.add((i,j+1))
        if(count1>2):
            return xquer/count1, np.sqrt(1.0/count1*
                                         (xquer2-1.0/count1*(xquer*xquer)))
        return count1,count
    def floodFill_size(self,int i,int j,double level1,int size=5, int mark=-1):
        # after floodFill_size was running don't forget to
        # remove the small (marked=-2) objects points in the grid
        cdef int count=0
        cdef double level
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if(i<0 or i>=self.nrows or j<0 or j>=self.ncols):
            return -9999
        print('flood:', i,j,self.mat[i,j],level1,self.mat[i,j]+level1)
        count=0
        toFill = set()
        toFill.add((i,j))
        minval=mat[i,j]
        level=level1+minval
        while len(toFill)>0:
            (i,j) = toFill.pop()
            if(int(mat[i,j])==self.nodata):
                continue
            if(int(mat[i,j])==mark):
                # count+=1
                continue
            if(mat[i,j]>level):
                continue
            mat[i,j]=mark-1
            count+=1
            if(i>0 and mat[i-1,j]>mark):
                toFill.add((i-1,j))
            if(i+1<self.nrows and mat[i+1,j]>mark):
                toFill.add((i+1,j))
            if(i>0 and mat[i,j-1]>mark):
                toFill.add((i,j-1))
            if(i+1<self.ncols and mat[j,j+1]>mark):
                toFill.add((i,j+1))
        if(count >= size):
            self.replace(mark-1,mark)
            return count # return with nodata as markup
        return 0  # return with marked
    # add and mul etc. two grids to one =====================================
    def add_grid(self, grid g1):
        """ add on grid to an other """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef int gli,glj,i,j,mat1_nodata
        (g1i,g1j)=g1.size()
        mat1_nodata=g1.get_nodata()
        if(g1i!=self.nrows or g1j!=self.ncols):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata or 
                   int(mat1[i,j])==mat1_nodata):
                    mat[i,j]=self.nodata
                else:
                    mat[i,j]+=mat1[i,j]
        return True
    def diff_grid(self, grid g1):
        """ calcualates the diff of two grids"""
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef int gli,glj,i,j,mat1_nodata
        (g1i,g1j)=g1.size()
        mat1_nodata=g1.get_nodata()
        if(g1i!=self.nrows or g1j!=self.ncols):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata or 
                   int(mat1[i,j])==mat1_nodata):
                    mat[i,j]=self.nodata
                else:
                    mat[i,j]-=mat1[i,j]
        return True
    def mul_grid(self, grid g1):
        """ multiply two grids """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef int gli,glj,i,j,mat1_nodata
        (g1i,g1j)=g1.size()
        mat1_nodata=g1.get_nodata()
        if(g1i!=self.nrows or g1j!=self.ncols):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata or 
                   int(mat1[i,j])==mat1_nodata):
                    mat[i,j]=self.nodata
                else:
                    mat[i,j]*=mat1[i,j]
        return True
    def max_grid(self,grid g1):
        """ combine two grids using maximum """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef int gli,glj,i,j,mat1_nodata
        (g1i,g1j)=g1.size()
        mat1_nodata=g1.get_nodata()
        if(g1i!=self.nrows or g1j!=self.ncols):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata or 
                   int(mat1[i,j])==mat1_nodata):
                    mat[i,j]=self.nodata
                else:
                    mat[i,j]=max(mat[i,j],mat1[i,j])
        return True
    def min_grid(self,grid g1):
        """ combine two grids using minimum """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef int gli,glj,i,j,mat1_nodata
        (g1i,g1j)=g1.size()
        mat1_nodata=g1.get_nodata()
        if(g1i!=self.nrows or g1j!=self.ncols):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata or 
                   int(mat1[i,j])==mat1_nodata):
                    mat[i,j]=self.nodata
                else:
                    mat[i,j]=min(mat[i,j],mat1[i,j])
        return True
    def or_grid(self,grid g1):
        """ replace nodata with values from grid g1 """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef int gli,glj,i,j
        (g1i,g1j)=g1.size()
        if(g1i!=self.nrows or g1j!=self.ncols):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    mat[i,j]=mat1[i,j]
        return True
    def and_grid(self,grid g1):
        """ includes the nodata values of self.mat or g1 """
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t,ndim=2] mat1=g1.get_matp()
        cdef gli,glj,i,j,nodata
        (g1i,g1j)=g1.size()
        mat1_nodata=g1.get_nodata()
        if(g1i!=self.nrows or g1j!=self.ncols):
            return False
        nodata=g1.get_nodata()
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat1[i,j])==nodata):
                    mat[i,j]=self.nodata
        return True
    # point  algorithms using x,y,z as np.arrays ===========================
    # use of int as coordinates x,y and float32 for z 
    def transform_to_ij(self,y1,x1):
        """ takes two lists or np.arrays with geo. coorinates and
            transforms them to grid coordinates [0,nrows], [0,ncols]
        """
        cdef np.ndarray[ITYPE_t,ndim=1] x=np.zeros(len(x1),dtype=np.int)
        cdef np.ndarray[ITYPE_t,ndim=1] y=np.zeros(len(x1),dtype=np.int)
        cdef int i
        if(len(x1)!=len(y1)):
            return None, None
        for i in xrange(len(x1)):
            x[i]=int((x1[i]-(self.x+self.csize/2.0))/self.csize)
            y[i]=int((y1[i]-(self.y+self.csize/2.0))/self.csize)
            y[i]=self.nrows-1-y[i]
            if(y[i]<0 or y[i]>=self.nrows or x[i]<0 or x[i]>=self.ncols):
                return None, None
        return y,x
    def inside_geo(self,float y1, float x1):
        """ takes a coordinate y1,x1 and returns the value of the grid
        """
        cdef int i,j
        j=int((x1-(self.x+self.csize/2.0))/self.csize)
        i=int((y1-(self.y+self.csize/2.0))/self.csize)
        i=self.nrows-1-i
        if(i<0 or i>=self.nrows or j<0 or j>=self.ncols):
            return None
        return self.mat[i,j]
    def set_geo(self, float y1, float x1, float z1):
        """ set the z at pos y1,x1 """
        cdef int i,j
        j=int((x1-(self.x+self.csize/2.0))/self.csize)
        i=int((y1-(self.y+self.csize/2.0))/self.csize)
        i=self.nrows-1-i
        if(i<0 or i>=self.nrows or j<0 or j>=self.ncols):
            return False
        self.mat[i,j]=np.float32(z1)
        return True
    def count_geo(self,float y1, float x1):
        """ add 1 to the point at pos y1,x1 in geo coordinates """
        cdef int i,j
        j=int((x1-(self.x+self.csize/2.0))/self.csize)
        i=int((y1-(self.y+self.csize/2.0))/self.csize)
        i=self.nrows-1-i
        if(i<0 or i>=self.nrows or j<0 or j>=self.ncols):
            return False
        self.mat[i,j]+=1.0
        return True
    def transform_from_ij(self,i1,j1):
        """ takes two lists with grid coordinates and
            transforms them to geographic coordinates
        """
        cdef np.ndarray[DOUBLE_t, ndim=1] x=np.zeros(len(i1),dtype=np.double)
        cdef np.ndarray[DOUBLE_t, ndim=1] y=np.zeros(len(i1),dtype=np.double)
        cdef int i
        if(len(i1)!=len(j1)):
            return None, None
        for i in xrange(len(i1)):
            x[i]=self.x+j1[i]*self.csize+self.csize/2.0
            y[i]=self.y+(self.nrows-i1[i]-1)*self.csize+self.csize/2.0
        return y,x
    def interpolate(self, y1,x1,z1, str method='linear'):
        """ 
        x,y,z coordinates and values 
        range from: 0<=x<=1 and 0<=y<=1
        method=
               'multiquadric': sqrt((r/self.epsilon)**2 + 1)
               'inverse': 1.0/sqrt((r/self.epsilon)**2 + 1)
               'gaussian': exp(-(r/self.epsilon)**2)
               'linear': r
               'cubic': r**3
               'quintic': r**5
               'thin_plate': r**2 * log(r)
         """
        cdef np.ndarray[DTYPE_t,ndim=1] x=np.array(x1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=1] y=np.array(y1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=1] z=np.array(z1).astype(np.float32)
        x/=np.float32(self.ncols)
        y/=np.float32(self.nrows)
        if((self.mat is None) or len(x)<=0 or len(y)<=0 or len(z)<=0):
            return False
        rbfi=Rbf(x, y, z, function=method)
        tx=np.linspace(0, 1, self.ncols)
        ty=np.linspace(0, 1, self.nrows)
        XI, YI = np.meshgrid(tx, ty)
        self.mat=np.float32(rbfi(XI,YI))
        return True
    # use of int as coordinates x,y and float32 for z 
    def voronoi(self,y1,x1,z1):
        """ calculates a voroni map from i,j,z """
        cdef int i,j,k,k0
        cdef double dist,dist0
        cdef np.ndarray[DTYPE_t,ndim=1] x=np.array(x1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=1] y=np.array(y1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=1] z=np.array(z1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if((mat is None) or len(x)<=0 or len(y)<=0 or len(z)<=0):
            return False
        if(len(x)!=len(y) or len(y)!=len(z)<=0):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                dist0=np.finfo(np.double).max
                k0=0
                for k in xrange(len(x)):
                    dist=(i-y[k])*(i-y[k])+(j-x[k])*(j-x[k])
                    if(dist<dist0):
                        dist0=dist
                        k0=k
                mat[i,j]=z[k0]
        return True
    # use of int as coordinates x,y and float32 for z 
    def distance(self, y1,x1):
        """ calcs the distance between all i,j points """
        cdef int i,j,k
        cdef double dist,dist0
        cdef np.ndarray[DTYPE_t,ndim=1] x=np.array(x1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=1] y=np.array(y1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=2] mat=self.mat
        if((mat is None) or len(x)<=0 or len(y)<=0):
            return False
        if(len(x)!=len(y)):
            return False
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                dist0=np.finfo(np.double).max
                for k in xrange(len(x)):
                    dist=(i-y[k])*(i-y[k])+(j-x[k])*(j-x[k])
                    if(dist<dist0):
                        dist0=dist
                mat[i,j]=np.float(self.csize*np.sqrt(dist0))
        return True
    # implementation of a poisson cfd solver
    def poisson(self, y1,x1,z1, double eps, int iter=25):
        """ uses a iterative method to solve the poisson equation:
            d^2V(x,y)/dx^2+d^2V(x,y)/dy^2=-const(x,y)
            uses number of iterations=25
        """
        cdef np.ndarray[DTYPE_t,ndim=1] x=np.array(x1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=1] y=np.array(y1).astype(np.float32)
        cdef np.ndarray[DTYPE_t,ndim=1] z=np.array(z1).astype(np.float32)
        cdef np.ndarray[np.double_t, ndim=2] cfd1=np.zeros((
                self.nrows+2,self.ncols+2))
        cdef np.ndarray[np.double_t, ndim=2] rho=np.copy(cfd1)
        cdef np.ndarray[np.double_t, ndim=2] V_temp=np.copy(cfd1)
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef int k,i,j,iterations
        cdef double h2=1.0/(self.csize*self.csize)
        cdef double error=2*eps
        cdef double f
        for k in xrange(len(x)):
            # cfd1[y[k],x[k]]=z[k]
            # rho[self.nrows-1-y[k],x[k]]=z[k] 23.1.2015
            rho[y[k],x[k]]=z[k]
        while iterations<iter and error> eps:
            V_temp = np.copy(cfd1)
            error=0.0
            for i in xrange(1,self.nrows):
                for j in xrange(1,self.ncols):
                    cfd1[i,j] = 0.25*(V_temp[i+1,j] + cfd1[i-1,j] +
                                      cfd1[i,j-1] + V_temp[i,j+1] + rho[i,j]*h2)
                    error += abs(cfd1[i,j]-V_temp[i,j])
            iterations += 1
            # error /= float(self.nrows**2)
        print('cfd_poisson error=',error, 'iterartions=', iterations)
        # transform it back to self.mat
        f=np.max(z)/np.max(cfd1)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                mat[i,j]=np.float32(cfd1[i+1,j+1])*f
        return True

    # implementation of flow algorithms
    def d4(self):
        """ code u=1 r=3 d=5 l=7 sink=-1 """
        if(self.mat is None):
            return False
        cdef int i,j, dir
        cdef DTYPE_t minval
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t, ndim=2] d4_mat=\
            np.zeros((self.nrows,self.ncols),dtype=DTYPE)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    dir=-1 # sink
                    minval=mat[i,j]
                    if(i>0 and mat[i-1,j]<minval):
                        minval=mat[i-1,j]
                        dir=1  # u
                    if(j+1<self.ncols and mat[i,j+1]<minval):
                        minval=mat[i,j+1]
                        dir=3  # r
                    if(i+1<self.nrows and mat[i+1,j]<minval):
                        minval=mat[i+1,j]
                        dir=5  # d
                    if(j>0 and mat[i,j-1]<minval):
                        dir=7  # l
                    d4_mat[i,j]=dir
        self.d4_mat=d4_mat
        return True
    def d8(self):
        """ code u=1 ur=2 r=3 dr=4 d=5 dl=6 l=7 ul=8 sink=-1 """
        if(self.mat is None):
            return False
        cdef int i,j, dir
        cdef DTYPE_t minval, sq2=np.sqrt(2.0)
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t, ndim=2] d8_mat=\
            np.zeros((self.nrows,self.ncols),dtype=DTYPE)
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])!=self.nodata):
                    dir=-1 # sink
                    minval=mat[i,j]
                    if(i>0 and mat[i-1,j]<minval):
                        minval=mat[i-1,j]
                        dir=1  # u
                    if(i>0 and j<self.nrows and mat[i-1,j+1]<minval/sq2):
                        minval=mat[i-1,j+1]/sq2
                        dir=2  #ur
                    if(j+1<self.ncols and mat[i,j+1]<minval):
                        minval=mat[i,j+1]
                        dir=3  # r
                    if(i+1<self.nrows and j+1<self.ncols and 
                       mat[i+1,j+1]<minval/sq2):
                        minval=mat[i+1,j+1]/sq2 
                        dir=4  # dr
                    if(i+1<self.nrows and mat[i+1,j]<minval):
                        minval=mat[i+1,j]
                        dir=5  # d
                    if(i+1<self.nrows and j>0 and mat[i+1,j-1]<minval/sq2):
                        minval=mat[i+1,j-1]/sq2
                        dir=6  # dl
                    if(j>0 and mat[i,j-1]<minval):
                        minval=mat[i,j-1]
                        dir=7  # l
                    if(i>0 and j>0 and mat[i-1,j-1]<minval/sq2):
                        dir=8  # ul
                    d8_mat[i,j]=dir
        self.d8_mat=d8_mat
        return True     
    def grad_d4(self):
        """ generates a map with gradient values from d4 """
        if(self.mat is None):
            return False
        if(self.d4_mat is None):
            self.d4()
        cdef int i,j,dir
        cdef DTYPE_t minval
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t, ndim=2] matn=np.copy(self.mat)
        cdef np.ndarray[DTYPE_t, ndim=2] d4_mat=self.d4_mat
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    continue
                if(int(d4_mat[i,j])==-1):
                    matn[i,j]=-1
                    continue
                dir=int(d4_mat[i,j])
                if(dir==1):  
                    matn[i,j]-=mat[i-1,j]
                    continue
                if(dir==3):
                    matn[i,j]-=mat[i,j+1]
                    continue
                if(dir==5):
                    matn[i,j]-=mat[i+1,j]
                    continue
                if(dir==7):
                    matn[i,j]-=mat[i,j-1]
        self.mat=matn
        return True
    def grad_d8(self):
        """ generates a map with gradient values from d8 """
        if(self.mat is None):
            return False
        if(self.d8_mat is None):
            self.d8()
        cdef int i,j,dir
        cdef DTYPE_t minval
        cdef np.ndarray[DTYPE_t, ndim=2] mat=self.mat
        cdef np.ndarray[DTYPE_t, ndim=2] matn=np.copy(self.mat)
        cdef np.ndarray[DTYPE_t, ndim=2] d8_mat=self.d8_mat
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                if(int(mat[i,j])==self.nodata):
                    continue
                if(int(d8_mat[i,j])==-1):
                    matn[i,j]=-1
                    continue
                dir=int(d8_mat[i,j])
                if(dir==1):  
                    matn[i,j]-=mat[i-1,j]      #u
                    continue
                if(dir==2):
                    matn[i-1,j+1]-=mat[i-1,j]  #ur
                    continue
                if(dir==3):
                    matn[i,j]-=mat[i,j+1]      #r
                    continue
                if(dir==4):
                    matn[i,j]-=mat[i+1,j+1]    #dr
                    continue
                if(dir==5):
                    matn[i,j]-=mat[i+1,j]      #d
                    continue
                if(dir==6):
                    matn[i,j]-=mat[i+1,j-1]    #dl
                    continue
                if(dir==7):
                    matn[i,j]-=mat[i,j-1]      #l
                    continue
                if(dir==8):
                    matn[i,j]-=mat[i-1,j-1]    #ul
        self.mat=matn
        return True


# ===================== Copy ===============================================
def copy_grid(grid gx):
    """ copy two grids """
    g1=grid()
    (nrows,ncols,x,y,csize,nodata)=gx.get_header()
    g1.set_header(nrows,ncols,x,y,csize,nodata)
    g1.set_mat(gx.get_matc())
    g1.clear_time()
    return g1
# ===================== Zoom ===============================================

def create_zoom(grid gx, int i0, int i1, int j0, int j1):
    """ generates a new grid from a part of the original
        i0,j0 upper left corner
        i1,j1 lower right corner
        returns a new grid of the zoom
    """
    cdef int nrows,ncols,nodata
    cdef double csize,x,y
    (nrows,ncols,x,y,csize,nodata)=gx.get_header()
    if(i0<=0 or i0>=i1 or j0<=0 or j0>j1 or i1>=nrows or j1>=ncols):
        return None
    g1=grid()
    # calculate the new nrows and ncols
    nrows1=i1-i0
    ncols1=j1-j0
    # calculae the new lower left corner in geographic coordinates
    x=x+(nrows-i1)*csize
    y=y+j0*csize
    g1.set_header(nrows1,ncols1,x,y,csize,nodata)
    g1.set_mat(gx.get_matc(i0,i1,j0,j1))
    return g1

# ===================== Sample ===============================================
def sample(g1,g4, g2=None,g3=None,n=100,filename=None,
           x1='x1',x2='x2',x3='x3',x4='y'):
    """ samples from up to three grids as inputs and one grid
        as output of a training set
        n values and
        writes the table to a file
    """
    cdef int i,j,k, g1_nows,g2_nrows,g3_nrows,g1_ncols,g2_ncols,g3_ncols
    cdef float val1,val2,val3,val4
    cdef np.ndarray[DTYPE_t, ndim=2] m1=g1.get_matp()
    cdef np.ndarray[DTYPE_t, ndim=2] m2
    cdef np.ndarray[DTYPE_t, ndim=2] m3
    cdef np.ndarray[DTYPE_t, ndim=2] m4
    g1_nrows,g1_ncols=g1.size()
    if((g1 is None) or (g4 is None)):
        return None,None
    if(g2 is not None):
        g2_nrows,g2_ncols=g2.size()
        if(g1_nrows!=g2_nrows or g1_ncols!=g2_ncols):
            print("error in sample: grids missmatch!")
            return None,None
        m2=g2.get_matp()
    if(g3 is not None):
        g3_nrows,g3_ncols=g3.size()
        if(g1_nrows!=g3_nrows or g1_ncols!=g3_ncols):
            print("error in sample: grids missmatch!")
            return None,None
        m3=g3.get_matp()
    if(g4 is not None):
        g4_nrows,g4_ncols=g4.size()
        if(g1_nrows!=g4_nrows or g1_ncols!=g4_ncols):
            print("error in sample: grids missmatch!")
            return None,None
        m4=g4.get_matp()
    k=0
    val1=0
    val2=0
    val3=0
    val4=0
    res=[]
    resy=[]
    while(k<n):
        i=np.random.randint(0,g1_nrows)
        j=np.random.randint(0,g1_ncols)
        val1=m1[i,j]
        if(int(val1)==g1.get_nodata()):
            continue
        if(g2 is not None):
            val2=m2[i,j]
            if(int(val2)==g2.get_nodata()):
                continue
        if(g3 is not None):
            val3=m3[i,j]
            if(int(val3)==g3.get_nodata()):
                continue
        if(g4 is not None):
            val4=m4[i,j]
            if(int(val4)==g4.get_nodata()):
                continue    
        if((g2 is not None) and (g3 is not None) and (g4 is not None)):
            res.append([val1,val2,val3])
            resy.append(val4)
            k+=1
            continue
        if((g2 is not None) and (g3 is None) and (g4 is not None)):
            res.append([val1,val2])
            resy.append(val4)
            k+=1
            continue
        if((g2 is None) and (g3 is not None) and (g4 is not None)):
            res.append([val1,val3])
            resy.append(val4)
            k+=1
            continue
        if((g2 is None) and (g3 is None) and (g4 is not None)):
            res.append([val1])
            resy.append(val4)
            k+=1
            continue
        res.append([val1])
        k+=1
    if(filename is None):
        return res,resy
    f=open(filename,'w')
    if((g2 is not None) and (g3 is not None) and (g4 is not None)):
        f.write("%s %s %s %s\n" % (x1,x2,x3,x4))
    if((g2 is not None) and (g3 is None) and (g4 is not None)):
        f.write("%s %s %s\n" % (x1,x2,x4))
    if((g2 is None) and (g3 is not None) and (g4 is not None)):
        f.write("%s %s %s\n" % (x1,x3,x4))
    if((g2 is None) and (g3 is None) and (g4 is not None)):
        f.write("%s %s\n" % (x1,x4))
    for k in np.arange(n):
        if((g2 is not None) and (g3 is not None) and (g4 is not None)):
            s="%f %f %f %f\n" % (res[k][0],res[k][1],res[k][2],resy[k])
        if((g2 is not None) and (g3 is None) and (g4 is not None)):
            s="%f %f %f\n" % (res[k][0],res[k][1],resy[k])
        if((g2 is None) and (g3 is not None) and (g4 is not None)):
            s="%f %f %f\n" % (res[k][0],res[k][1],resy[k])
        if((g2 is None) and (g3 is None) and (g4 is not None)):
            s="%f %f\n" % (res[k][0],resy[k])
        f.write(s)
    f.close()
    return res,resy
