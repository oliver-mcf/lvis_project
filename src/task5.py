'''
Task5: Produce Map of Elevation Change for Pine Island Glacier, 2009-2015
'''

###########################################

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *
from manageRAM import *

###########################################

# Main function
def main():
    '''Main function to produce an elevation chage map of Pine Island Glacier from 2009 to 2015'''

    # Start CPU runtime
    start = time.process_time()
    
    # Load shapefile and DEMs
    shape = '/home/s1949330/Documents/MSc_OOSA/project/shapes/pine_island_glacier.shp'
    dem_09 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2009_FINAL.tif'
    dem_15 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2015_FINAL.tif'

    # Clip each DEM to the study area 
    output_dem_09 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2009_FINAL_OVERLAP.tif'
    output_dem_15 = '/home/s1949330/Documents/MSc_OOSA/LVIS_DEM_2015_FINAL_OVERLAP.tif'
    clip_tiff(dem_09, shape, output_dem_09, reference_raster = dem_15)
    clip_tiff(dem_15, shape, output_dem_15, reference_raster = dem_15)

    # Read DEMs and calculate elevation change
    dem_09_tiff = methodsDEM(output_dem_09)
    dem_15_tiff = methodsDEM(output_dem_15)
    elevation_avg, elevation_change = dem_09_tiff.calculate_change(dem_15_tiff, avg = True)
    print('Average Elevation Change, 2009-2015: ', round(elevation_avg, 3), 'metres')

    # Create histogram for elevation change
    valid_change = elevation_change[(elevation_change != -999) & (elevation_change <= 75) & (elevation_change >= -75)]
    plt.hist(valid_change.flatten(), bins = 30, color = 'steelblue')
    plt.xticks(np.arange(-75, 76, 25))
    plt.title('Elevation Change of Pine Island Glacier, 2009-2015')
    plt.xlabel('Elevation Change (meters)')
    plt.ylabel('Frequency')
    plt.show()

    # Write elevation change data to geotiff
    output_tiff = '/home/s1949330/Documents/MSc_OOSA/LVIS_ELEVATION_CHANGE.tif'
    dem_09_tiff.write_tiff(elevation_change, output_tiff, epsg = 3031)

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round((time.process_time() - start), 2)} seconds")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")


if __name__ == '__main__':
     
     main()

