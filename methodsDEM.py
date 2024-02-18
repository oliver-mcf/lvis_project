'''
Methods for LVIS DEMs
'''

# Import libraries
import glob
import numpy as np
import os
import rasterio as rio
from rasterio.merge import merge
from rasterio.enums import Resampling
from rasterio.mask import mask
from shapely.geometry import mapping
import geopandas as gpd
from plotLVIS import plotLVIS


###########################################

def merge_dem(file_list, merged_file):
    '''Merge multiple DEMs or geotiffs'''
    # read files
    datasets = [rio.open(file) for file in file_list]
    # merge dems
    mosaic, transform = merge(datasets, resampling = Resampling.nearest)
    # write merged dem to geotiff
    with rio.open(merged_file, 'w', driver = 'GTiff', count = 1, dtype = mosaic.dtype, crs = datasets[0].crs, transform = transform, width = mosaic.shape[2], height = mosaic.shape[1]) as dst:
        dst.write(mosaic, 1)
    # close open dems
    for dataset in datasets:
        dataset.close()

    print('Successful merge: ', merged_file)

###########################################
