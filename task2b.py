'''
Task2b: Produce DEM of Pine Island Glacier
'''

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *


if __name__ == '__main__':
    
    # Identify DEM subsets and study area
    dem_list = glob.glob('/home/s1949330/Documents/MSc_OOSA/project_data/2009/*.tif')
    print(len(dem_list))
    glacier = '/home/s1949330/Documents/MSc_OOSA/project_data/pine_island/pine_island_glacier.shp'

    # Identify subsets within range
    filtered_subsets = filter_subsets(dem_list, glacier)

    # Merge selected subsets
    output_dir = '/home/s1949330/Documents/MSc_OOSA/project_data/2009/filtered/'
    merge_subsets(filtered_subsets, output_dir, step_size = 15)





 


'''''''''
    
    # Output directory
    output_dir = '/home/s1949330/Documents/MSc_OOSA/project_data/'

    # Chunk size
    chunk_size = 3  # You can adjust this based on your available memory

    # Iterate through chunks of DEMs
    for i in range(0, len(dem_list), chunk_size):
        chunk_dem_list = dem_list[i:i + chunk_size]

        # Build VRT for the current chunk
        vrt_filename = os.path.join(output_dir, f'merged_chunk_{i}.vrt')
        vrt = gdal.BuildVRT(vrt_filename, chunk_dem_list)

        # Translate the VRT to a GeoTIFF
        output_filename = os.path.join(output_dir, f'merged_chunk_{i}.tif')
        gdal.Translate(output_filename, vrt, xRes=30, yRes=-30)

        # Close the VRT dataset
        vrt = None



    
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