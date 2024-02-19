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
from plotLVIS import plotLVIS



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
    print(f'Successfully merged {len(filtered_list)} into {merged_count} subsets')

    # merge the chunked GeoTIFFs into a final result if needed
    #final_vrt = gdal.BuildVRT(os.path.join(output_dir, 'merged.vrt'),
    #                          [f'merged_chunk_{i}.tif' for i in range(0, len(filtered_list), step_size)])
    #gdal.Translate(os.path.join(output_dir, 'mergedDEM.tif'), final_vrt, xRes=30, yRes=-30)
    #final_vrt = None










###########################################

def combine_dems(input_list, output_file, shape):
    # Retrieve wanted DEM data from subsets and combine
    # read geometry of shapefile
    gdf = gpd.read_file(shape)
    mask_geometry = gdf.geometry
    # find bounds of largest subset
    max_height, max_width = 0, 0
    for file in input_list:
        with rio.open(file) as src:
            height, width = src.shape
            max_height = max(max_height, height)
            max_width = max(max_width, width)
    # allocate space to store masked data from each subset
    combined_data = np.full((len(input_list), max_height, max_width), -999.0, dtype = float)
    # systematically read each subset
    for idx, filename in enumerate(input_list):
        with rio.open(filename) as src:
            data = src.read(1, masked=True)
            transform = src.transform
            crs = src.crs
            # set boolean (True/False) mask of pine island
            mask = features.geometry_mask(mask_geometry, transform = transform, out_shape = data.shape, invert = True)
            # apply mask subset and add to allocated space
            combined_data[idx, :data.shape[0], :data.shape[1]] = np.ma.masked_array(data, mask)
    # write the combined masked data to tiff
    print('Writing masked DEM to tiff...')
    with rio.open(output_file, 'w', driver = 'GTiff', height = max_height, width = max_width, 
                  count = len(input_list), dtype = combined_data.dtype, crs = crs, transform = transform, nodata = -999.0) as dst:
        dst.write(combined_data)

    print('SUCCESSFUL PINE ISLAND GLACIER DEM: ', output_file)

###########################################
