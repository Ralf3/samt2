from osmviz.manager import PILImageManager, OSMManager
import PIL.Image as Image
import numpy as np
from pyproj import Proj, transform
import math
import scipy
from scipy import misc

def transf(x_ul,y_ul, pix_ver, pix_hor, p_size, projection=31469):
    """The function 'transf()' transforms a point from one (geographical)
       coordinate system to another.
       Input and output koordinate system are define by their
       EPSG code (31469= Gauss-Krueger zone 5, 4326=WGS84)
       from the desired map dimensions in pixels and the pixel size,
       the function calculates the bounding box for the map
    """
    control="epsg:%d" % projection
    inProj = Proj(init=control)
    outProj = Proj(init='epsg:4326')
    x_ul2,y_ul2 = transform(inProj,outProj,x_ul,y_ul)
    x_lr, y_lr = x_ul+(p_size*pix_hor), y_ul-(p_size*pix_ver)
    x_lr2,y_lr2 = transform(inProj,outProj,x_lr,y_lr)
    return( x_ul2, y_ul2, x_lr2, y_lr2)

def get_map( x_ul, y_ul, x_lr,  y_lr, p_size):
    """the function 'get_map()' retrieves an open street map within the
       given bounding box and the zoom level that corresponds best to
       the desired pixel size.

       p_size=C*cos(lat)/2**(zoom_lvl+8)

       p_size   - pixel size in m
       C        - length of equator
       lat      - latitude
       zoom_lvl - OSM zoom level

       this formula has been manipulated and constant values have been
       included and precalculated to derive the zoom level from a given
       pixel size
       The map is returned as numpy array.
    """
    zoom_lvl=round(np.log2(np.cos(np.deg2rad(y_lr)))-
                   np.log2(p_size)+17.256199796589126,0)
    imgr = PILImageManager('RGB')
    osm = OSMManager(image_manager=imgr)
    image,bnds = osm.createOSMImage( ( y_lr, y_ul, x_ul, x_lr), zoom_lvl )
    osm.getTileCoord(x_ul, y_ul, zoom_lvl)
    # image.show()
    map_arr=np.array(image)
    return(map_arr, zoom_lvl)


def pos_map(x_ul, y_ul, zoom_lvl, projection=31469):
    """
       calculates the pos for the cutting
    """
    imgr = PILImageManager('RGB')
    osm = OSMManager(image_manager=imgr)
    xtile, ytile = osm.getTileCoord(x_ul, y_ul, zoom_lvl)
    n = 2.0 ** zoom_lvl
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    control="epsg:%d" % projection
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init=control)
    mapx_ul,mapy_ul = transform(inProj,outProj,lon_deg,lat_deg)
    return(mapx_ul, mapy_ul)

def cut_map(map_arr, x1, y1, y_ul,
            mapx_ul, mapy_ul, pix_ver, pix_hor,
            csize, zoom_lvl):
    """
        cuts a part of the map
    """
    print('x1, y1, y_ul, mapy_ul:', x1, y1, y_ul, mapy_ul)
    p_size_map=40075017.*np.cos(np.deg2rad(y_ul))/2**(zoom_lvl+8)
    dx=(x1-mapx_ul)/p_size_map
    dy=(mapy_ul-y1)/p_size_map
    print('cut_map:',dx,dy, p_size_map)
    map_new=map_arr[dy:dy+
                    (pix_ver*csize/p_size_map),
                    dx:dx+(pix_hor*csize/p_size_map),:]
    return(map_new)


def resize_map( map_new, pix_vert, pix_hor):
    """
       applies the imresize to a map
    """
    map_final=scipy.misc.imresize(map_new, (pix_vert, pix_hor))
    return(map_final)


# Main function should be used with samt2
def create_map(header,projection=31469):
    """
    the header comes from gx.get_header():
    [180, 300, 5396600.0, 5905900.0, 100.0, -9999]
    [nrows, ncols, xxl,yll, cize, nodata]
    """
    nrows=header[0]
    ncols=header[1]
    csize=header[4]
    # automated scale procedure
    scale=np.round(np.log2(min(nrows,ncols)))
    scalef=np.power(2.0,9-scale)
    print(scale, scalef)
    if(scalef!=0.0):
        nrows=int(nrows*scalef)
        ncols=int(ncols*scalef)
        csize=csize/scalef
    print(nrows,ncols,csize)
    x1=header[2]               # ll
    y1=header[3]+(nrows*csize) # ul
    x_ul, y_ul, x_lr, y_lr = transf(x1,y1, nrows, ncols, csize, projection)
    map_arr, zoom_lvl = get_map( x_ul, y_ul, x_lr,  y_lr, csize)
    mapx_ul, mapy_ul = pos_map(x_ul, y_ul, zoom_lvl, projection)
    print(mapx_ul, mapy_ul, x1,y1)
    #map_new = cut_map(map_arr,x1,y1+2400/scalef,y_ul,
    #                  mapx_ul,mapy_ul,nrows,ncols,csize,zoom_lvl)
    map_new = cut_map(map_arr,x1,y1,y_ul,
                      mapx_ul,mapy_ul,nrows,ncols,csize,zoom_lvl)
    map_final=resize_map(map_new, nrows, ncols)
    print('shape:', map_final.shape)
    return map_final

