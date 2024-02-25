'''
Task4: Produce Smoothed DEMs for Pine Island Glacier in 2009 and 2015
'''

###########################################

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *

###########################################

# Main function
def main():
    '''Main function to produce and smooth LVIS DEMs for Pine Island Glacier in a given year'''
    
    # Define command line parser to use for multiple LVIS years
    parser = argparse.ArgumentParser(description = "Process LVIS files from a specified year.")
    parser.add_argument("year", help = "Year of LVIS data, 2009 or 2015")
    parser.add_argument("--smooth", action = "store_true", help = "Perform gap-filling algorithm to smooth LVIS DEMs")
    parser.add_argument("--output_dir", help = "Output directory for DEM(s)")
    args = parser.parse_args()

    # Start CPU runtime
    start = time.process_time()

    # Filter DEM subsets to those in study area
    dem_list = glob.glob(f'DEM_subset_{args.year}.*.tif')
    print(f'Number of DEM subsets: {len(dem_list)}')
    shape = 'pine_island_glacier.shp'
    filtered_subsets = filter_tiffs(dem_list, shape)

    # Batch merge filtered subsets (to merge all 244 subsets at once, RAM = ~9GB)
    merge_tiffs(filtered_subsets, args.output_dir, step_size = 10, label = f'initial_{args.year}')
    merged_list = glob.glob(f'initial_{args.year}_*.tif')
    merge_tiffs(merged_list, args.output_dir, step_size = len(merged_list), label = f'final_{args.year}')
    os.rename(f'final_{args.year}_merged_subsets_0.tif', f'LVIS_DEM_{args.year}.tif')

    # Crop merged LVIS DEM to study area
    lvis_dem = f'LVIS_DEM_{args.year}.tif'
    output_file = os.path.join(args.output_dir, f'PIG_DEM_{args.year}.tif')
    clip_tiff(lvis_dem, shape, output_file)

    # Visualise DEM of Pine Island Glacier, 2009
    PIG_DEM = rio.open(output_file)
    data = PIG_DEM.read(1, masked = True)
    plt.figure(figsize = (10, 10))
    plt.imshow(data, cmap = 'magma', extent = PIG_DEM.bounds, origin = 'upper')
    cbar = plt.colorbar(shrink = 0.5)
    cbar.set_label('Elevation (m)')
    plt.title(f"LVIS Flight DEMs for Pine Island Glacier, {args.year}")
    plt.show()
    PIG_DEM.close()

    # Perform smoothing algorithm if condition is applied
    if args.smooth():
        smooth_dem = f'LVIS_DEM_{args.year}_FINAL.tif' 
        smooth_tiff(lvis_dem, smooth_dem)

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round(((time.process_time() - start) / 60), 2)} minutes")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")


if __name__ == '__main__':
     
     main()

    # python task4.py 2009 smooth
    #                 2015 smooth