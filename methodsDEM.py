'''
Methods for LVIS DEMs
'''

# Import libraries
import glob
from osgeo import gdal
import numpy as np
import os
import rasterio as rio
from rasterio.plot import show
from rasterio import features
from rasterio.merge import merge
from rasterio.enums import Resampling
from rasterio.mask import mask
from shapely.geometry import mapping
import geopandas as gpd
from shapely.geometry import shape, box
import matplotlib.pyplot as plt
import subprocess


###########################################

def convert_bytes(number):
    '''Function to convert file size to known units'''
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if number < 1024.0:
            return "%3.1f %s" % (number, x)
        number /= 1024.0
    return

###########################################

def file_size(file):
    '''Function to calculate filesize of file'''
    if os.path.isfile(file):
        file_info = os.stat(file)
        return convert_bytes(file_info.st_size)
    return

###########################################

def filter_subsets(dem_list, shapefile):
    '''Return list of DEM subsets in range of shapefile'''
    # read shape and define bounding box
    gdf = gpd.read_file(shapefile)
    bounding_box = gdf.total_bounds
    # read subsets
    filtered_list = []
    for dem_file in dem_list:
        ds = gdal.Open(dem_file)
        dem_bbox = [ds.GetGeoTransform()[0], ds.GetGeoTransform()[3] + ds.RasterYSize * ds.GetGeoTransform()[5],
                    ds.GetGeoTransform()[0] + ds.RasterXSize * ds.GetGeoTransform()[1], ds.GetGeoTransform()[3]]
        # retrieve data within bounding box
        dem_geom = box(dem_bbox[0], dem_bbox[1], dem_bbox[2], dem_bbox[3])
        shapefile_geom = box(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])
        # add to filtered list if data intersects with box
        if dem_geom.intersects(shapefile_geom):
            filtered_list.append(dem_file)
    print(f'DEM subsets in range of glacier: {len(filtered_list)}')
    return filtered_list

###########################################

def merge_subsets(filtered_list, output_dir, step_size):
    '''Batch process to merge DEM subsets'''
    # systematically iterate through subsets
    merged_count = 0
    for i in range(0, len(filtered_list), step_size):
        select_list = filtered_list[i:i + step_size]
        # build virtual dataset of current subsets
        vrt_filename = os.path.join(output_dir, f'merged_subsets{i}.vrt')
        vrt = gdal.BuildVRT(vrt_filename, select_list)
        # translate the virtual dataset to a tiff
        output_filename = os.path.join(output_dir, f'merged_subsets{i}.tif')
        gdal.Translate(output_filename, vrt, xRes = 30, yRes = -30)
        # close virtual dataset
        vrt = None
        merged_count += 1
    print(f'Successful merge from {len(filtered_list)} to {merged_count} DEM subsets')

###########################################

def clip_geotiff(input_file, shape_file, output_file):
    '''Clip DEM geotiff to study area'''
    # read input raster and shapefile
    glacier = gpd.read_file(shape_file)
    dem = rio.open(input_file)
    # align raster and shape geometry
    glacier = glacier.to_crs(dem.crs)
    geometry = glacier.geometry.values[0]
    geoms = [geometry]
    # clip dem to shapefile
    dem_glacier, transform = mask(dataset = dem, shapes = geoms, crop = True)
    metadata = dem.meta.copy()
    metadata.update({'driver': 'GTiff', 'height': dem_glacier.shape[1], 'width': dem_glacier.shape[2], 'transform': transform})
    # write the clipped DEM as geotiff
    with rio.open(output_file, 'w', **metadata) as dst:
        dst.write(dem_glacier)
    dem.close()
    print(f'------------SUCCESSFUL LVIS DEM OF PINE ISLAND GLACIER------------:\n {output_file}')

###########################################