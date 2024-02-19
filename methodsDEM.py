'''
Methods for LVIS DEMs
'''

# Import libraries
import glob
from osgeo import gdal
import numpy as np
import os
import rasterio as rio
from rasterio import features
from rasterio.merge import merge
from rasterio.enums import Resampling
from rasterio.mask import mask
from shapely.geometry import mapping
import geopandas as gpd
from shapely.geometry import shape, box
import subprocess



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
    print(f'Subsets in range of glacier: {len(filtered_list)}')
    return filtered_list

###########################################

def batch_merge_subsets(filtered_list, output_dir, step_size):
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
    print(f'Successful merge from {len(filtered_list)} to {merged_count} subsets')


    # merge the newly merged subsets in range of glacier
    #output = 'PIG_DEM.tif'
    #final_vrt = gdal.BuildVRT(os.path.join(output_dir, 'PIG_DEM.vrt'), [f'merged_dem{i}.tif' for i in range(0, len(filtered_list), step_size)])
    #gdal.Translate(os.path.join(output_dir, output), final_vrt, xRes = 30, yRes = -30)
    #final_vrt = None
    #print(f'SUCCESSFUL PINE ISLAND GLACIER DEM: {output_dir}{output}')

def merge_geotiffs(input_files, output_file):
    """
    Merge multiple GeoTIFFs into a single GeoTIFF file.

    Parameters:
    - input_files: List of input GeoTIFF file paths to be merged.
    - output_file: Output GeoTIFF file path.

    Returns:
    - None
    """
    # Open the first GeoTIFF to use its geospatial information
    with gdal.Open(input_files[0]) as src_ds:
        # Create an output GeoTIFF with the same geospatial information
        gdal.Warp(output_file, src_ds, options=['COMPRESS=DEFLATE'])

        # Loop through the remaining GeoTIFFs and add them to the output
        for input_file in input_files[1:]:
            gdal.Warp(output_file, input_file, options=['COMPRESS=DEFLATE'], destSRS=src_ds.GetProjection())