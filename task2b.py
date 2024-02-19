'''
Task2b: Produce DEM of Pine Island Glacier, 2009
'''

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *


if __name__ == '__main__':
    
    # Identify DEM subsets and study area
    dem_list = glob.glob('/home/s1949330/Documents/MSc_OOSA/project_data/2009/*.tif')
    print(f'Number of DEM subsets: {len(dem_list)}')
    glacier = '/home/s1949330/Documents/MSc_OOSA/project_data/pine_island/pine_island_glacier.shp'

    # Filter subsets within range of study area (to merge all 244 subsets at once, RAM = ~9GB)
    filtered_subsets = filter_subsets(dem_list, glacier)

    # Merge filtered subsets 
    merged_output_dir = '/home/s1949330/Documents/MSc_OOSA/project_data/2009/filtered/'
    batch_merge_subsets(filtered_subsets, merged_output_dir, step_size = 10)

    # Combine merged subsets
    filtered_list = glob.glob('/home/s1949330/Documents/MSc_OOSA/project_data/2009/filtered/*.tif')
    cmd = 'gdal_merge.py -ps 30 -30 -o /home/s1949330/Documents/MSc_OOSA/project_data/2009/filtered/combined/mergedDEM.tif -n -999'
    subprocess.call(cmd.split() + filtered_list)
    
    
    



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