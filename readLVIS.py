'''
Class to Read LVIS File
'''

# Import libraries
import numpy as np
import h5py as h5
from pyproj import Proj, transform
from pprint import pprint
import pandas as pd


class readLVIS():
  '''Class to retrieve data from LVIS file'''

  ###########################################

  def __init__(self, filename, setElev = False, minX = -100000000, maxX = 100000000, minY = -1000000000, maxY = 100000000, onlyBounds = False):
    '''Class initialiser: Read spatial subset of LVIS data'''
    self.read_LVIS(filename, minX, minY, maxX, maxY, onlyBounds)
    print("Successful readLVIS:", filename)
    if(setElev):            # to save time, only read elevation if wanted
      self.set_elevations()

  ###########################################

  def read_LVIS(self, filename, minX, minY, maxX, maxY, onlyBounds):
    '''Read LVIS file'''
    f = h5.File(filename, 'r')
    # set projection
    self.projection = Proj("epsg:4326")
    # determine how many bins (vertical points)
    self.nBins = f['RXWAVE'].shape[1]
    # read coordinates for subsetting
    lon0 = np.array(f['LON0'])                      # longitude of waveform top
    lat0 = np.array(f['LAT0'])                      # lattitude of waveform top
    lonN = np.array(f['LON' + str(self.nBins -1)])  # longitude of waveform bottom
    latN = np.array(f['LAT' + str(self.nBins -1)])  # lattitude of waveform bottom
    # find a single coordinate per footprint
    tempLon = (lon0 + lonN) / 2.0
    tempLat = (lat0 + latN) / 2.0
    # write out bounds and leave if needed
    if(onlyBounds):
      self.lon = tempLon
      self.lat = tempLat
      self.bounds = self.dump_bounds()
      return
    # determine which are in region of interest
    useInd = np.where((tempLon >= minX) & (tempLon < maxX) & (tempLat >= minY) & (tempLat < maxY))
    if(len(useInd) > 0):
      useInd = useInd[0]
    # check data is in region of interest
    if(len(useInd) == 0):
      print("No data contained in that region")
      self.nWaves = 0
      return
    # save the subset of all data
    self.nWaves = len(useInd)
    print("Number of waves in the subset:", self.nWaves)
    self.lon = tempLon[useInd]
    self.lat = tempLat[useInd]
    # load sliced arrays, to save RAM
    self.lfid = np.array(f['LFID'])[useInd]          # LVIS flight ID number
    self.lShot = np.array(f['SHOTNUMBER'])[useInd]   # the LVIS shot number, a label
    self.waves = np.array(f['RXWAVE'])[useInd]       # the recieved waveforms, the data
    self.nBins = self.waves.shape[1]
    # these variables will be converted to easier variables
    self.lZN = np.array(f['Z' + str(self.nBins -1)])[useInd]       # The elevation of the waveform bottom
    self.lZ0 = np.array(f['Z0'])[useInd]                           # The elevation of the waveform top
    # close file, return to initialiser
    f.close()
    return

  ###########################################

  def set_elevations(self):
    '''Creates an array of elevations per waveform'''
    self.z = np.empty((self.nWaves, self.nBins))
    # loop over waves, return array of elevations (floats)
    for i in range(0, self.nWaves): 
      self.z[i] = np.linspace(self.lZ0[i], self.lZN[i],  self.nBins)

  ###########################################

  def one_waveform(self, ind):
    '''Return a single waveform'''
    return(self.z[ind], self.waves[ind])

  ###########################################

  def dump_coords(self):
     '''Return coordinates'''
     return(self.lon,self.lat)

  ###########################################

  def dump_bounds(self):
     '''Return bounds'''
     return[np.min(self.lon), np.min(self.lat), np.max(self.lon), np.max(self.lat)]  # this returns a list rather than a tuple

  ###########################################