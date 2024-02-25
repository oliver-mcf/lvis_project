'''
Methods for LVIS DEMs
'''

# Import libraries
import glob
from osgeo import gdal, gdal_array
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import box
from rasterio.mask import mask
from rasterio.enums import Resampling
from rasterio.plot import show
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds, Window
import rasterio as rio
from scipy.interpolate import griddata
from readLVIS import *
from processLVIS import *
from plotLVIS import *


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

def filter_tiffs(geotiff_list, shapefile):
    '''Return list of DEM subsets in range of shapefile'''
    # read shape and define bounding box
    gdf = gpd.read_file(shapefile)
    bounding_box = gdf.total_bounds
    # read subsets
    filtered_list = []
    for tiff in geotiff_list:
        ds = gdal.Open(tiff)
        dem_bbox = [ds.GetGeoTransform()[0], ds.GetGeoTransform()[3] + ds.RasterYSize * ds.GetGeoTransform()[5],
                    ds.GetGeoTransform()[0] + ds.RasterXSize * ds.GetGeoTransform()[1], ds.GetGeoTransform()[3]]
        # retrieve data within bounding box
        dem_geom = box(dem_bbox[0], dem_bbox[1], dem_bbox[2], dem_bbox[3])
        shapefile_geom = box(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])
        # add to filtered list if data intersects with box
        if dem_geom.intersects(shapefile_geom):
            filtered_list.append(tiff)
    print(f'Subsets in range: {len(filtered_list)}')
    return filtered_list

###########################################


def merge_tiffs(filtered_list, output_dir, step_size):
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

def clip_tiff(input_file, shapefile, output_file):
    '''Clip DEM geotiff to study area'''
    # read input raster and shapefile
    glacier = gpd.read_file(shapefile)
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
'''''''''
def smooth_tiff(input_file, output_file, window_size):
    # read input raster data
    with rio.open(input_file) as src:
        data = src.read(1)
        # identify coords of nodata values
        nodata_mask = (data == src.nodata) | (data < 0)
        y, x = np.where(~nodata_mask)
        values = data[~nodata_mask]
        # create grid for interpolation
        y_grid, x_grid = np.mgrid[0:data.shape[0]:window_size, 0:data.shape[1]:window_size]
        # interpolate nodata values
        filled_data = griddata((y, x), values, (y_grid, x_grid), method = 'linear')
        # create geotiff with filled data
        with rio.open(output_file, 'w', **src.profile) as dst:
            dst.write(filled_data, 1)
'''''''''

def smooth_tiff(input_file, output_file):
    with rio.open(input_file) as src:
        data = src.read(1)
        nodata_value = src.nodata

        # Identify coords of nodata values, including values less than 0
        nodata_mask = (data == nodata_value) | (data < 0)

        # Fill nodata values using GDAL's FillNodata
        filled_data = gdal.FillNodata(data, None, maxSearchDist=100, smoothingIterations=0)

        # Mask filled data using the original nodata_mask
        filled_data[nodata_mask] = nodata_value

        # Save the filled data to the output GeoTIFF
        with rio.open(output_file, 'w', **src.profile) as dst:
            dst.write(filled_data, 1)

###########################################

