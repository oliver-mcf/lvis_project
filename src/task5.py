'''
Task5: Produce Map of Elevation Change for Pine Island Glacier, 2009-2015
'''

###########################################

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *
from handleTiffs import *

###########################################

# Main function
def main():
    '''Main function to produce an elevation chage map of Pine Island Glacier from 2009 to 2015'''

    # Start CPU runtime
    start = time.process_time()

    # Load shapefile and DEMs
    shapefile_path = '/home/s1949330/Documents/MSc_OOSA/project/shapes/pine_island_glacier.shp'
    dem_09 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2009_FINAL.tif'
    dem_15 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2015_FINAL.tif'

    # Clip each DEM to the study area 
    output_dem_09 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2009_FINAL_OVERLAP.tif'
    output_dem_15 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2015_FINAL_OVERLAP.tif'
    clip_tiff(dem_09, shapefile_path, output_dem_09, reference_raster = dem_09)
    clip_tiff(dem_15, shapefile_path, output_dem_15, reference_raster = dem_09)

    # Create instances of tiffHandle for the new GeoTIFFs
    clipped_dem_09_handle = tiffHandle(output_dem_09)
    clipped_dem_15_handle = tiffHandle(output_dem_15)

    # Flatten the data and create masked arrays
    flattened_data_09 = np.ma.masked_invalid(clipped_dem_09_handle.flatten_tiff())
    flattened_data_15 = np.ma.masked_invalid(clipped_dem_15_handle.flatten_tiff())

    # Calculate elevation change 
    change_values = flattened_data_15 - flattened_data_09

    # Print statistics without NaN values
    print('Mean elevation change: ', np.ma.mean(change_values))
    print('Median elevation change: ', np.ma.median(change_values))

    # Express change in ice volume
    surface_area = clipped_dem_09_handle.nY * clipped_dem_09_handle.nX
    total_ice_volume_change = np.ma.sum(change_values) * surface_area
    print(f'TOTAL ICE VOLUME CHANGE: {total_ice_volume_change} m^3')

    # Write elevation change to geotiff
    output_change_tiff = '/home/s1949330/Documents/MSc_OOSA/LVIS_ELEVATION_CHANGE.tif'
    change_tiff_handle = tiffHandle(output_dem_09)
    change_values_2d = change_values.reshape(clipped_dem_09_handle.nY, clipped_dem_09_handle.nX)
    change_tiff_handle.write_tiff(change_values_2d, output_change_tiff, epsg = 3031)

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round((time.process_time() - start), 2)} seconds")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")


if __name__ == '__main__':
     
     main()

