'''
Task5: Calculate Elevation & Mass Change for Pine Island Glacier, 2009-2015
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

    # Define command line parser to use for multiple LVIS years
    parser = argparse.ArgumentParser(description = "Process LVIS files from a specified year.")
    parser.add_argument("--output_dir", help = "Output directory for DEM(s)")
    args = parser.parse_args()

    # Start CPU runtime
    start = time.process_time()
    
    # Load shapefile and DEMs
    shape = '.../shapes/pine_island_glacier.shp'
    dem_09 = 'LVIS_DEM_2009_FINAL.tif'
    dem_15 = 'LVIS_DEM_2015_FINAL.tif'

    # Clip each DEM to the study area 
    output_dem_09 = f'{args.output_dir}LVIS_DEM_2009_FINAL_OVERLAP.tif'
    output_dem_15 = f'{args.output_dir}LVIS_DEM_2015_FINAL_OVERLAP.tif'
    clip_tiff(dem_09, shape, output_dem_09, reference_raster = dem_15)
    clip_tiff(dem_15, shape, output_dem_15, reference_raster = dem_15)

    # Read DEMs and calculate elevation change
    dem_09_tiff = methodsDEM(output_dem_09)
    dem_15_tiff = methodsDEM(output_dem_15)
    elevation_avg, elevation_change = dem_09_tiff.calculate_change(dem_15_tiff, avg = True)
    print('Average Elevation Change, 2009-2015: ', round(elevation_avg, 3), 'metres')

    # Create histogram for elevation change
    valid_change = elevation_change[(elevation_change != -999) & (elevation_change <= 75) & (elevation_change >= -75)]
    plt.hist(valid_change.flatten(), bins = 30, color = 'teal')
    plt.xticks(np.arange(-75, 76, 25))
    plt.title('LVIS Elevation Change of Pine Island Glacier, 2009-2015')
    plt.xlabel('Elevation Change (meters)')
    plt.ylabel('Frequency')
    plt.savefig(f'{args.output_dir}/lvis_dem_change_histogram.png')
    plt.show()

    # Write elevation change data to geotiff
    output_tiff = f'{args.output_dir}LVIS_ELEVATION_CHANGE.tif'
    dem_09_tiff.write_tiff(elevation_change, output_tiff, epsg = 3031)
    
    # Express elevation change in ice volume
    surface_area = (dem_09_tiff.nX * 30) * (dem_09_tiff.nY * 30)  # in square meters
    print(f'Surface Area: {surface_area} m²')

    # Calculate valid elevation change (excluding -999 values)
    valid_change = elevation_change[elevation_change != -999]

    # Calculate volume change in meters
    volume_change = np.sum(valid_change) * surface_area
    print(f'Ice Volume Change: {round(volume_change, 3)} m³')

    # Convert ice volume change to mass of water equivalent
    ice_density = 0.917 / 1000                       # convert density from g/cm³ to kg/m³
    water_density = 1.000 / 1000                     # convert density from g/cm³ to kg/m³
    mass_change = volume_change * (ice_density / water_density)
    print(f'Ice Mass Change: {round(mass_change, 3)} kg')
    print(f'Ice Mass Change per year: {round((mass_change / 6), 3)} kg/year')

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round((time.process_time() - start), 2)} seconds")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")


if __name__ == '__main__':
     
     main()

