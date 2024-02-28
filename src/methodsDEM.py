'''
Class & Methods to Handle DEMs
'''

# Import libraries
from pyproj import Proj, transform
from osgeo import osr
import numpy as np
import glob
from osgeo import gdal, gdal_array
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import box
import rasterio as rio
from rasterio.mask import mask
from rasterio.enums import Resampling
from rasterio.plot import show
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds, Window
from rasterio.warp import reproject, Resampling
from rasterio.vrt import WarpedVRT
from scipy.interpolate import griddata


# Define class
class methodsDEM():
  '''Class to handle geotiff files'''

  ###########################################
  
  def __init__(self, filename):
    self.read_tiff(filename)

  ###########################################

  def read_tiff(self,filename):
    '''Read a geotiff into RAM'''
    # open a dataset object
    ds = gdal.Open(filename)
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
    
  def calculate_change(self, other_tiff, avg = False):
    '''Calculate change in values between two geotiffs'''
    # check dimensions of geotiffs match
    if self.data.shape != other_tiff.data.shape:
        raise ValueError("GeoTIFFs have different dimensions.")
    # calculate change / difference
    elevation_change = other_tiff.data - self.data
    # if avg argument given
    if avg == True:
      # exclude NaN and nodata values
      nan_mask = np.isnan(elevation_change)
      elevation_change[nan_mask] = -999
      # generate statistics
      mean_elevation_change = np.mean(elevation_change[elevation_change != -999])
      return mean_elevation_change, elevation_change
  
  ###########################################

  def write_tiff(self, data, filename, epsg):
    '''Write a geotiff from a raster layer'''
    # set geolocation information
    geotransform = (self.xOrigin, self.pixelWidth, 0, self.yOrigin, 0, self.pixelHeight)
    # load data into geotiff object
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

def filter_tiffs(geotiff_list, shapefile):
  '''Function to return list of geotiffs in range of study area'''
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
  print(f'Subsets in range of study area: {len(filtered_list)}')
  return filtered_list

  ###########################################

def merge_tiffs(filtered_list, output_dir, step_size, label):
  '''Function to batch process / merge geotiffs'''
  # systematically iterate through subsets
  merged_count = 0
  for i in range(0, len(filtered_list), step_size):
      select_list = filtered_list[i:i + step_size]
      # build virtual dataset of current subsets
      vrt_filename = os.path.join(output_dir, f'{label}_merged_subsets{i}.vrt')
      vrt = gdal.BuildVRT(vrt_filename, select_list)
      # translate the virtual dataset to a tiff
      output_filename = os.path.join(output_dir, f'{label}_merged_subsets{i}.tif')
      gdal.Translate(output_filename, vrt, xRes = 30, yRes = -30)
      # close virtual dataset
      vrt = None
      merged_count += 1
      # show evidence of merge
      if merged_count > 1:
          print(f'Merged {len(filtered_list)} to {merged_count} files')
      elif merged_count == 1:
          print(f'------------SUCCESS: LVIS DEM MERGED------------')

###########################################

def clip_tiff(input_file, shapefile, output_file, reference_raster = None):
  '''Function to clip a geotiff to study area'''
  # read input raster and shapefile
  glacier = gpd.read_file(shapefile)
  dem = rio.open(input_file)
  # align raster and shape geometry
  glacier = glacier.to_crs(dem.crs)
  geometry = glacier.geometry.values[0]
  geoms = [geometry]
  # use reference raster dimensions if provided
  if reference_raster:
      reference = rio.open(reference_raster)
      vrt_options = {'resampling': Resampling.nearest, 'src_crs': dem.crs, 'src_transform': dem.transform, 'crs': reference.crs,
                      'transform': reference.transform, 'width': reference.width, 'height': reference.height}
      vrt = WarpedVRT(dem, **vrt_options)
      dem = rio.MemoryFile().open(driver = 'GTiff', count = 1, width = reference.width, height = reference.height, 
                                  transform = reference.transform, dtype = vrt.read(1).dtype)
      dem.write(vrt.read(1), 1)
  # clip dem to shapefile
  dem_glacier, transform = rio.mask.mask(dataset = dem, shapes = geoms, crop = True)
  # update metadata with epsg and no-data value
  metadata = dem.meta.copy()
  metadata.update({'driver': 'GTiff', 'crs': 'EPSG:3031', 'height': dem_glacier.shape[1], 'width': dem_glacier.shape[2], 
                    'transform': transform, 'nodata': -999})
  # write the clipped DEM as geotiff
  with rio.open(output_file, 'w', **metadata) as dst:
      dst.write(dem_glacier)
  dem.close()
  print(f'------------SUCCESS: LVIS DEM CLIPPED------------:\t {output_file}')

###########################################

def smooth_tiff(input_file, output_file, window_size):
  '''Gap fill no data values in geotiff'''
  # read input raster data
  with rio.open(input_file) as src:
      data = src.read(1)
      # identify coords of nodata values
      nodata_mask = (data == src.nodata) | (data < 20)
      y, x = np.where(~nodata_mask)
      values = data[~nodata_mask]
      # create grid for interpolation
      y_grid, x_grid = np.mgrid[0:data.shape[0]:window_size, 0:data.shape[1]:window_size]
      # interpolate nodata values
      print('Smoothing geotiff...')
      filled_data = griddata((y, x), values, (y_grid, x_grid), method = 'linear')
      # create geotiff with filled data
      with rio.open(output_file, 'w', **src.profile) as dst:
          dst.write(filled_data, 1)
  print(f'------------SUCCESS: LVIS DEM SMOOTHED------------:\t {output_file}')

###########################################
    


