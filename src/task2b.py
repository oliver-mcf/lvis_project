'''
Task2b: Produce DEMs for Pine Island Glacier in 2009 and 2015
'''

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *


def main():
    '''Main function to combine LVIS flight-path DEMs of Pine Island Glacier for a given year'''
    
    # Define command line parser to use for multiple LVIS years
    parser = argparse.ArgumentParser(description = "Process LVIS files from a specified year.")
    parser.add_argument("year", help = "Year of LVIS data (2009 or 2015)")
    args = parser.parse_args()

    start = time.process_time()

    # Find DEM subsets and study area
    dem_list = glob.glob(f'/home/s1949330/Documents/MSc_OOSA/project_data/{args.year}/*.tif')
    print(f'Number of DEM subsets: {len(dem_list)}')

    # Filter subsets within range of study area (to merge all 244 subsets at once, RAM = ~9GB)
    glacier = '/home/s1949330/Documents/MSc_OOSA/project_data/pine_island/pine_island_glacier.shp'
    filtered_subsets = filter_geotiffs(dem_list, glacier)

    # Merge filtered subsets in appropriate batches
    merged_output_dir = f'/home/s1949330/Documents/MSc_OOSA/project_data/{args.year}/filtered/'
    merge_subsets(filtered_subsets, merged_output_dir, step_size = 10)

    # Combine merged subsets
    filtered_list = glob.glob(f'/home/s1949330/Documents/MSc_OOSA/project_data/{args.year}/filtered/*.tif')
    output_dir = f'/home/s1949330/Documents/MSc_OOSA/project_data/{args.year}/filtered/combined/'
    merge_subsets(filtered_list, output_dir, len(filtered_list))
    os.rename(str(output_dir) + 'merged_subsets0.tif', str(output_dir) + f'LVIS_DEM_{args.year}.tif')

    # Crop combined DEM to study area polygon
    pine_island = '/home/s1949330/Documents/MSc_OOSA/project_data/pine_island/pine_island_glacier.shp'
    lvis_dem = str(output_dir) + f'LVIS_DEM_{args.year}.tif'
    pig_dem = str(output_dir) + f'PIG_DEM_{args.year}.tif'
    clip_geotiff(lvis_dem, pine_island, pig_dem)

    # Visualise DEM of Pine Island Glacier, 2009
    PIG_DEM = rio.open(str(output_dir) + f'PIG_DEM_{args.year}.tif')
    data = PIG_DEM.read(1, masked = True)
    plt.figure(figsize = (8, 8))
    plt.imshow(data, cmap = 'magma', extent = PIG_DEM.bounds, origin = 'upper')
    cbar = plt.colorbar(shrink = 0.5)
    cbar.set_label('Elevation (m)')
    plt.title(f"LVIS DEMs for Pine Island Glacier, {args.year}")
    plt.show()
    PIG_DEM.close()

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round((time.process_time() - start), 2)} seconds")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")

if __name__ == '__main__':

    main()

    # python task2b.py 2009
    #                  2015