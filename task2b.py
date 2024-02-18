'''
Task2b: Produce DEM for Pine Island Glacier
'''

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *


if __name__ == '__main__':
    
    # Identify DEM subsets
    dem_list = glob.glob('/home/s1949330/Documents/MSc_OOSA/project_data/2009/*.tif')
    print(len(dem_list))
    
    # Merge DEMs
    output_file = 'LVIS_DEM_2009.tif'
    merge_dem(dem_list, output_file) # > 9GB


    '''''''''

    # Crop DEM to Pine Island Glacier
    input_file = '/home/s1949330/Documents/MSc_OOSA/project_data/2009/LVIS_DEM_2009.tif'
    shape_file = '/home/s1949330/Documents/MSc_OOSA/project_data/GLIMS_PIG_shapefile/glims_polygons.shp'
    output_file = '/home/s1949330/Documents/MSc_OOSA/project_data/2009/PIG_DEM_2009.tif'

    # Align input and shape geometry
    glacier = gpd.read_file(shape_file)
    dem = rio.open(input_file)
    glacier.to_crs(dem.crs)
    geometry = glacier.geometry.values[0]
    geoms = [glacier(geometry)]

    # Crop LVIS DEM to Pine Island Glacier
    dem_glacier, transform = mask(dataset = dem, shapes = glacier, crop = True)
    metadata = dem.meta.copy()
    metadata.update({'driver': 'GTiff', 'height': glacier.shape[1], 'width': glacier.shape[2], 'transform': transform})

    # Write the clipped DEM as geotiff
    with rasterio.open(output_file, 'w', **metadata) as dst:
        dst.write(dem_glacier)
    dem.close()

    '''''''''
