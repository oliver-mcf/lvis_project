'''
Class to Process LVIS Data
'''

# Import libraries
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
from tqdm import tqdm
import argparse
from readLVIS import readLVIS


# Define class
class processLVIS(readLVIS):
  '''Class to process LVIS ground elevation over ice'''

  ###########################################
  
  def estimate_ground(self, sigThresh = 5, statsLen = 10, minWidth = 3, sWidth = 0.5):
    '''Return ground estimate from waveform'''
    # find noise statistics
    self.find_stats(statsLen = statsLen)
    # set noise threshold
    threshold = self.set_threshold(sigThresh)
    # remove background noise
    self.denoise(threshold, minWidth = minWidth, sWidth = sWidth)
    # find centre of gravity of remaining signal
    self.centre_gravity()

  ###########################################

  def set_threshold(self, sigThresh):
    '''Set noise threshold'''
    threshold = self.meanNoise + sigThresh * self.stdevNoise
    return(threshold)

  ###########################################

  def centre_gravity(self):
    '''Find centre of gravity of denoised waveforms to return array of ground elevation estimates'''
    # allocate space and set no data
    self.zG = np.full((self.nWaves), -999.0)
    # loop over waveforms
    for i in range(0, self.nWaves):
      if(np.sum(self.denoised[i]) > 0.0):                                # avoid empty waveforms (clouds etc)
        self.zG[i] = np.average(self.z[i], weights = self.denoised[i])   # calculte centre of gravity
    return(self.zG)

  ###########################################

  def find_stats(self, statsLen = 10):
    '''Calculate standard deviation and mean of noise'''
    # make empty arrays
    self.meanNoise = np.empty(self.nWaves)
    self.stdevNoise = np.empty(self.nWaves)
    # determine number of bins to calculate stats over
    res = (self.z[0,0] - self.z[0,-1]) / self.nBins    # range resolution
    noiseBins = int(statsLen / res)                    # number of bins within "statsLen"
    # loop over waveforms
    for i in range(0, self.nWaves):
      self.meanNoise[i] = np.mean(self.waves[i, 0: noiseBins])
      self.stdevNoise[i] = np.std(self.waves[i, 0: noiseBins])

  ###########################################

  def denoise(self, threshold, sWidth = 0.5, minWidth = 3):
    '''Remove noise in waveform data'''
    res = (self.z[0,0] - self.z[0,-1]) / self.nBins    # range resolution
    # make array for output
    self.denoised = np.full((self.nWaves, self.nBins), 0)
    # loop over waves
    for i in tqdm(range(0, self.nWaves)):
      # print("Denoising wave", i+1, "of", self.nWaves)
      # subtract mean background noise
      self.denoised[i] = self.waves[i] - self.meanNoise[i]
      # set all values less than threshold to zero
      self.denoised[i, self.denoised[i] < threshold[i]] = 0.0
      # minimum acceptable width
      binList = np.where(self.denoised[i] > 0.0)[0]
      for j in range(0, binList.shape[0]):                                        # loop over waveforms
        if((j > 0) & (j < (binList.shape[0] -1))):                                # if middle of array
          if((binList[j] != binList[j-1] +1) | (binList[j] != binList[j+1] -1)):  # if bins are consecutive
            self.denoised[i, binList[j]] = 0.0                                    # if not, set to zero
      # smooth
      self.denoised[i] = gaussian_filter1d(self.denoised[i], sWidth / res)

###########################################

