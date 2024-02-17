'''
Class to Visualise LVIS data with Command Line Parser
'''

# Import libraries
from pyproj import Proj, transform
import matplotlib.pyplot as plt
import argparse
import numpy as np
from osgeo import gdal, osr
from processLVIS import processLVIS     # inherit class


def get_cmd_args():
  '''Get commandline arguments'''
  # create an argparse object with a useful help comment
  p = argparse.ArgumentParser(description = ("An illustration of a command line parser"))
  # read a string
  p.add_argument("--input", dest = "inName", type = str, default = '/geos/netdata/oosa/week4/lvis_antarctica/ILVIS1B_AQ2015_1014_R1605_070717.h5', help = ("Input filename"))
  p.add_argument("--outRoot", dest = "outRoot", type = str, default = 'waveforms', help = ("Output filename root"))
  # parse the command line into an object
  cmdargs = p.parse_args()
  # return that object from this function
  return cmdargs


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

  def plot_waves(self, outRoot = "waveform", step = 1):
    '''Plot all waveforms'''
    # loop over list of waveforms
    for i in range(0, self.nWaves, step):
      self.plot_wave(i, outRoot = outRoot)

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
    '''Write array to geotiff'''
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
    
    '''''''''
    # calculate the raster pixel index in x and y
    xInds = np.array(np.floor((x - np.min(x)) / res), dtype = int)   # need to force to int type
    yInds = np.array(np.floor((np.max(y) -y) / res), dtype = int)    # floor rounds down. y is from top to bottom
    # simple pack which will assign a single footprint to each pixel
    imageArr[yInds, xInds] = data
    '''''''''

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

    # set geolocation information (note geotiffs count down from top edge in Y)
    geotransform = (minX, res, 0, maxY, 0, -res)
    # load data in to geotiff object
    dst_ds = gdal.GetDriverByName('GTiff').Create(filename, nX, nY, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(geotransform)            # specify coords
    srs = osr.SpatialReference()                    # establish encoding
    srs.ImportFromEPSG(epsg)                        # WGS84 lat/long
    dst_ds.SetProjection(srs.ExportToWkt())         # export coords to file
    dst_ds.GetRasterBand(1).WriteArray(imageArr)    # write image to the raster
    dst_ds.GetRasterBand(1).SetNoDataValue(-999)    # set no data value
    dst_ds.FlushCache()                             # write to disk
    dst_ds = None
    print("Image written to", filename)

  ###########################################