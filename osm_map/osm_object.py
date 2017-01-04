#!/usr/bin/env python
# -*- coding: utf-8 -*-


from osmviz.manager import PILImageManager, OSMManager
import PIL.Image as Image
import numpy as np
from pyproj import Proj, transform
import math
import scipy
from scipy import misc
import sys
import os
sys.path.append(os.environ['SAMT2MASTER']+"/src")
import grid as samt2
import pylab as plt

# objectoriented mapviewer for SAMT2
# after Felix Linde make_map.py

class MapVisualization(object):
    """ 
    The class MapVisualisation allows SAMT2 to use an openstreetmap
    for visualization. The visualisation uses a picture of the OSM,
    not a vector graphic. 
    The MapVisaulisation provides an Interface to set the projection,
    to define the picture, the resolution of the picture etc.
    """
    def __init__(self):
        """
        Defines the Projections used in SAMT2 for an application in
        Germany, shuold be adapted for usage in other countries
        """
        self.utm31=Proj(init='EPSG:32631')
        self.utm32=Proj(init='EPSG:32632')
        self.utm33=Proj(init='EPSG:32633')
        self.erts1=Proj(init='EPSG:25831')
        self.erts2=Proj(init='EPSG:25832')
        self.erts3=Proj(init='EPSG:25833')
        self.wgs84=Proj(init='EPSG:4326')
        self.gk5=Proj(init='EPSG:31469')
        self.epsg=self.gk5 # default projection of the used SAMT2 grid
        self.scalef=0.0    # set the scale factor
        self.ulx=0.0       # set the edges of the bounding box
        self.uly=0.0
        self.lrx=0.0
        self.lry=0.0
        self.llx=0.0       # original llx,lly from grid
        self.lly=0.0
        self.map=None      # stores the picture as ndarray
        self.zoom_lvl=0.0  # zoom level for OSM tiles
        self.flag=False    # flag to correct the first digit in llx
    def set_projection(self,epsg):
        """
        Defines the projections of the grid:
        
        Parameters:
        -----------
        epsg as string see EPSG:32631
        
        Returns:
        --------
        True/False if projection available
        """
        self.flag=True     # flag to correct the first digit in llx
        self.epsg=None
        if(epsg=='EPSG:32631'):
            self.epsg=self.utm31
            return True
        if(epsg=='EPSG:32632'):
            self.epsg=self.utm32
            return True
        if(epsg=='EPSG:32633'):
            self.epsg=self.utm33
            return True
        if(epsg=='EPSG:31469'):
            self.epsg=self.gk5
            return True
        if(epsg=='EPSG:4326'):
            self.epsg=self.wgs84
            return True
        if(epsg=='EPSG:25831'):
            self.epsg=self.erts1
            return True
        if(epsg=='EPSG:25832'):
            self.epsg=self.erts2
            return True
        if(epsg=='EPSG:25833'):
            self.epsg=self.erts3
            return True
        return False
     
    def bb(self,gx):
        """
        Bounding Box (bb) defines the ulx,uly and lrx,lry from the SAMT2 
        header. The projection self.epsg has to be set bevore usage.
        
        Parameters:
        -----------
        a valid SAMT2 grid in self.epsg projection
        
        Object Variables:
        -----------------
        self.ulx,self.uly,self.lrx,self.lry
        self.scalef, self.llx,self.lly
        
        Returns:
        --------
        True/False if the projection was succseful
        """
        (nrows,
         ncols,
         llx,
         lly,
         csize,
         nodata)=gx.get_header()
        if(self.flag==True):
            llx=float(str(llx)[1:])
        self.llx=llx
        self.lly=lly
        scale=np.round(np.log2(min(nrows,ncols)))
        self.scalef=np.power(2.0,9-scale)
        if(self.scalef == 0.0):
            return False
        self.nrows=int(nrows*self.scalef)
        self.ncols=int(ncols*self.scalef)
        self.csize=csize/self.scalef
        #print("Scaling: nrows=%d ncols=%d csize=%f" %
        #      (self.nrows,self.ncols,self.csize))
        # set the ulx,uly, lrx,lry from the grid after scaleling
        ulx=llx
        uly=lly+nrows*csize
        lrx=llx+ncols*csize
        lry=lly
        # project it and store it
        self.ulx,self.uly = transform(self.epsg,self.wgs84,ulx,uly)
        self.lrx,self.lry = transform(self.epsg,self.wgs84,lrx,lry)
        #print(self.ulx,self.uly,ulx,uly)
        #print(self.lrx,self.lry,lrx,lry)
        return True
    
    def get_map(self):
        """
        Retrieves the map from the Internet and estimate the zoom level.

        Parameters:
        -----------
        self.ulx,self.uly,self.lrx,self.lry, self.csize

        Object Variables:
        -----------------
        self.map, self.zoom_lvl

        Returns:
        --------
        True/False according the load was successful
        """
        if(self.scalef == 0.0):  # check if scalef and ulx,uly,... are defined
            return False
        self.zoom_lvl=round(np.log2(np.cos(np.deg2rad(self.lry)))-
                            np.log2(self.csize)+17.256199796589126,0)
        print('zomm level:', self.zoom_lvl)
        imgr = PILImageManager('RGB')
        osm = OSMManager(image_manager=imgr)
        print(self.lry,self.uly,self.ulx,self.lrx)
        image,bnds = osm.createOSMImage((self.lry,
                                         self.uly,
                                         self.ulx,
                                         self.lrx),
                                        self.zoom_lvl)
        osm.getTileCoord(self.ulx, self.uly, self.zoom_lvl)
        # image.show()
        self.map=np.array(image)
        return True

    def cut_map(self):
        """ 
        Combines the definition of the  map_ulx, map_uly and
        cutting of the map and 
        resize of the map
        
        Parameters:
        -----------------
        self.ulx,self.uly, self.zoom_lvl, self.epsg
        
        Returns:
        --------
        new_map/None depending on the operations
        """
        if(self.map is None): # check if map is loaded
            return None
        imgr = PILImageManager('RGB')
        osm = OSMManager(image_manager=imgr)
        xtile, ytile = osm.getTileCoord(self.ulx, self.uly, self.zoom_lvl)
        n = 2.0 ** self.zoom_lvl
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        map_ulx,map_uly = transform(self.wgs84,self.epsg,lon_deg,lat_deg)
        # print(lon_deg,lat_deg,map_ulx,map_uly)
        # cut the map
        p_size_map=40075017.*np.cos(np.deg2rad(self.uly))/2**(self.zoom_lvl+8)
        x1=self.llx
        y1=self.lly+(self.nrows*self.csize)
        dx=int((x1-map_ulx)/p_size_map)
        dy=int((map_uly-y1)/p_size_map)
        # print('cut_map:',dx,dy, p_size_map)
        map_new=self.map[dy:dy+
                         (self.nrows*int(self.csize/p_size_map)),
                         dx:dx+(self.ncols*int(self.csize/p_size_map)),:]
        # resize the map
        map_final=scipy.misc.imresize(map_new, (self.nrows, self.ncols))
        return map_final

def create_map(gx,projection='EPSG:31469'):
    """
    Uses a grid with a known coordinate system (default= 'EPSG:31469')
    for gk5.
    
    Parameter:
    ----------
    the aktual grid gx, and the Projection (UTM 1-3, ERTS 1-3 and WGS 84)
    Returns:
    --------
    the image (ndarray) of the map
    """
    mv=MapVisualization()
    if(projection!='EPSG:31469'):
        val=mv.set_projection(projection)
    mv.bb(gx)
    mv.get_map()
    map=mv.cut_map()
    return map
    
