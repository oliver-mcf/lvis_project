'''
Class to Read and Write Geotiffs
'''

# Import libraries
from pyproj import Proj, transform
from osgeo import gdal
from osgeo import osr
import numpy as np
from methodsDEM import *


# Define class
class tiffHandle():
  '''Class to read/write geotiff files'''

  ###########################################
  
  def __init__(self, filename):
    self.read_tiff(filename)

  ###########################################

  def read_tiff(self,filename):
    '''Read a geotiff into RAM'''

    # open a dataset object
    ds = gdal.Open(filename)
    # could use gdal.Warp to reproject if wanted?
    # read data from geotiff object
    self.nX=  ds.RasterXSize             # number of pixels in x direction
    self.nY = ds.RasterYSize             # number of pixels in y direction
    # geolocation tiepoint
    transform_ds = ds.GetGeoTransform()  # extract geolocation information
    self.xOrigin = transform_ds[0]       # coordinate of x corner
    self.yOrigin = transform_ds[3]       # coordinate of y corner
    self.pixelWidth = transform_ds[1]    # resolution in x direction
    self.pixelHeight = transform_ds[5]   # resolution in y direction
    # return as a 2D numpy array
    self.data = ds.GetRasterBand(1).ReadAsArray(0, 0, self.nX, self.nY)
    print("Success reading geotiff")

  ###########################################

  def write_tiff(self, data, filename, epsg):
    '''Write a geotiff from a raster layer'''

    # Set geolocation information
    geotransform = (self.xOrigin, self.pixelWidth, 0, self.yOrigin, 0, self.pixelHeight)
    
    # Load data into geotiff object
    dst_ds = gdal.GetDriverByName('GTiff').Create(filename, self.nX, self.nY, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(geotransform)    # Specify coords
    srs = osr.SpatialReference()            # Establish encoding
    srs.ImportFromEPSG(epsg)                # WGS84 lat/long
    dst_ds.SetProjection(srs.ExportToWkt()) # Export coords to file
    dst_ds.GetRasterBand(1).WriteArray(data)  # Write image to the raster
    dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # Set no data value
    dst_ds.FlushCache()                     # Write to disk
    dst_ds = None
    print("Success writing image to", filename)

  ###########################################
    
  def flatten_tiff(self):
    return self.data.flatten()
  
  ###########################################