from osgeo import gdal
from osgeo import gdalconst
import struct
import datetime 

"""
please download the tile data from 
https://www.ngdc.noaa.gov/mgg/topo/gltiles.html
unpack ist and put it in one directory
download the header: https://www.ngdc.noaa.gov/mgg/topo/elev/esri/hdr/
and put it in the same directory
the dataname is the tile name a10g,b10g,c10g,...
"""

class DEM():
    def __init__(self,dataname):
        self.dataset=gdal.Open(dataname)
        self.dem_band=self.dataset.GetRasterBand(1)

    def altitude_at_raster_range(self,x1, y1, x2, y2):
        min_x = int(min(x1, x2))
        max_x = int(max(x1, x2))
        min_y = int(min(y1, y2))
        max_y = int(max(y1, y2))
        scanline_width = max_x - min_x + 1
        scanline_data_format = "<" + ("h" * scanline_width)
        data = []
        for y in range(min_y, max_y + 1):
            scanline = self.dem_band.ReadRaster(min_x, y,
                                           scanline_width,
                                           1,
                                           scanline_width,
                                           1,
                                           gdalconst.GDT_Int16)
            values = struct.unpack(scanline_data_format, scanline)
            data.append(values)
        return data
        
    def geographic_coordinates_to_raster_points(self,lon,lat):
        transform = self.dataset.GetGeoTransform()
        transform_inverse = gdal.InvGeoTransform(transform)
        x, y = gdal.ApplyGeoTransform(transform_inverse, lon, lat)
        return x,y
    
    def altitude_at_geographic_coordinates(self,lon, lat):
        x, y = self.geographic_coordinates_to_raster_points(lon, lat)
        values = self.altitude_at_raster_range(x, y, x, y)
        return values[0][0]
    
""" Example for some Locations in Armenia """

lon1,lat1 = 44.659701,41.090899,
lon2,lat2 = 46.406782,39.20771
lon3,lat3 = 45.147114,40.878794

dem=DEM('g10g')
h1=dem.altitude_at_geographic_coordinates(lon1,lat1)
h2=dem.altitude_at_geographic_coordinates(lon2,lat2)
h3=dem.altitude_at_geographic_coordinates(lon3,lat3)
print('H1: ',h1,' H2: ',h2,' H3: ',h3) 
