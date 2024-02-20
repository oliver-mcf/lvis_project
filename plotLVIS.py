'''
Class to Visualise LVIS data
'''

# Import libraries
from pyproj import Proj, transform
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal, osr
import os
import glob
import rasterio as rio
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from rasterio.merge import merge
from rasterio.mask import mask
from shapely.geometry import mapping, Point
import geopandas as gpd
from processLVIS import processLVIS


# Define class
class plotLVIS(processLVIS):
  '''Class to visualise LVIS data'''

  ###########################################

  def reproject_coords(self, outEPSG):
    '''Reproject footprint coordinates'''
    inProj = self.projection
    outProj = Proj("epsg:" + str(outEPSG))
    self.outProj = outProj
    self.x, self.y = transform(inProj, self.outProj, self.lat, self.lon)

  ###########################################

  def reproject_bounds(self, outEPSG):
    '''Reproject the file bounds'''
    inProj = Proj(self.projection)
    outProj = Proj("epsg:" + str(outEPSG))
    self.bounds[0,2], self.bounds[1,3] = transform(inProj, outProj, self.bounds[0,2], self.bounds[1,3])

  ###########################################
      
  def plot_wave(self, x, y, outName):
    ''''Plot a single waveform'''
    plot = outName
    plt.plot(x, y)
    plt.xlabel("Waveform return")
    plt.ylabel("Elevation (m)")
    plt.savefig(plot)
    plt.close()
    print("Successful plotLVIS: ", plot)

  ###########################################
  
  def write_tiff(self, data, x, y, res, filename, epsg):
      '''Write array to GeoTIFF using rasterio'''
      # set bounds
      minX = np.min(x)
      maxX = np.max(x)
      minY = np.min(y)
      maxY = np.max(y)
      # set image size
      nX = int((maxX - minX) / res + 1)
      nY = int((maxY - minY) / res + 1)
      # pack in to array
      imageArr = np.full((nY, nX), -999.0)
      # iterate over each pixel
      for i in range(nY):
          for j in range(nX):
              # calculate the raster pixel index in x and y
              xInds = np.where((x >= (minX + j * res)) & (x < (minX + (j + 1) * res)))[0]
              yInds = np.where((y >= (maxY - (i + 1) * res)) & (y < (maxY - i * res)))[0]
              # find intersecting footprints
              pixel_footprints = data[np.intersect1d(xInds, yInds)]
              # calculate the mean of intersecting footprints
              if len(pixel_footprints) > 0:
                  pixel_mean = np.mean(pixel_footprints)
                  imageArr[i, j] = pixel_mean
        # set geolocation information (note GeoTIFFs count down from top edge in Y)
      transform = from_origin(minX, maxY, res, res)

        # Write data to GeoTIFF using rasterio
      with rio.open(filename, 'w', driver = 'GTiff', height = nY, width = nX, count = 1, dtype = imageArr.dtype, crs = f'EPSG:{epsg}', transform = transform, nodata = -999) as dst:
            dst.write(imageArr, 1)
      print("Success:", filename)

  ###########################################
