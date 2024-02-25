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

    # Load shapefile
    shapefile_path = '/home/s1949330/Documents/MSc_OOSA/project/src/pine_island_glacier.shp'

    # Load raster files
    dem_09 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2009_FINAL.tif'
    dem_15 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2015_FINAL.tif'

    # Clip each DEM to the study area using the smaller raster as a reference for dimensions
    output_dem_09 = '/home/s1949330/Documents/MSc_OOSA/Clipped_LVIS_DEM_2009.tif'
    output_dem_15 = '/home/s1949330/Documents/MSc_OOSA/Clipped_LVIS_DEM_2015.tif'
    clip_tiff(dem_09, shapefile_path, output_dem_09, reference_raster=dem_09)
    clip_tiff(dem_15, shapefile_path, output_dem_15, reference_raster=dem_09)

    
    
    # Create instances of tiffHandle for the new GeoTIFFs
    clipped_dem_09 = '/home/s1949330/Documents/MSc_OOSA/Clipped_LVIS_DEM_2009.tif'
    clipped_dem_15 = '/home/s1949330/Documents/MSc_OOSA/Clipped_LVIS_DEM_2015.tif'
    # Create instances of tiffHandle for the new GeoTIFFs
    clipped_dem_09_handle = tiffHandle(clipped_dem_09)
    clipped_dem_15_handle = tiffHandle(clipped_dem_15)

    # Flatten the data
    flattened_data_09 = clipped_dem_09_handle.flatten_tiff()
    flattened_data_15 = clipped_dem_15_handle.flatten_tiff()

    print(flattened_data_09.shape)
    print(flattened_data_15.shape)

    change_values = flattened_data_15 - flattened_data_09

    print("Change Values:")
    print(change_values)

    # Specify the output GeoTIFF for change values
    output_change_tiff = '/home/s1949330/Documents/MSc_OOSA/Change_Values.tif'

    # Create an instance of tiffHandle for the new GeoTIFF
    change_tiff_handle = tiffHandle(clipped_dem_09)  # Assuming clipped_dem_09 has the same dimensions

    # Reshape the change_values to a 2D array if needed
    change_values_2d = change_values.reshape(clipped_dem_09_handle.nY, clipped_dem_09_handle.nX)

    # Write the change values to the new GeoTIFF
    change_tiff_handle.write_tiff(change_values_2d, output_change_tiff, epsg=3031)  # Change the EPSG code accordingly



    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round(((time.process_time() - start) / 60), 2)} minutes")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")


if __name__ == '__main__':
     
     main()

