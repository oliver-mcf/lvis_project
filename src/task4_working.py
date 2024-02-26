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
    shape = '.../shapes/pine_island_glacier.shp'
    filtered_subsets = filter_tiffs(dem_list, shape)

    # Batch merge filtered subsets (to merge all 244 subsets at once, RAM = ~9GB)
    merge_tiffs(filtered_subsets, args.output_dir, step_size = 10, label = f'initial_{args.year}')
    merged_list = glob.glob(f'initial_{args.year}_*.tif')
    merge_tiffs(merged_list, args.output_dir, step_size = len(merged_list), label = f'final_{args.year}')
    os.rename(f'final_{args.year}_merged_subsets_0.tif', f'LVIS_DEM_{args.year}_RAW.tif')

    # Crop merged LVIS DEM to study area
    lvis_dem = f'LVIS_DEM_{args.year}_RAW.tif'
    output_file = os.path.join(args.output_dir, f'LVIS_DEM_{args.year}_CROP.tif')
    clip_tiff(lvis_dem, shape, output_file)

    # Perform smoothing algorithm if condition is applied
    if args.smooth:
        raw_dem = f'LVIS_DEM_{args.year}.tif'
        smooth_dem = str(args.output_dir) + f'LVIS_DEM_{args.year}_SMOOTH.tif' 
        smooth_tiff(raw_dem, smooth_dem, window_size = 1)

        # Crop smoothed DEM to Pine Island Glacier
        final_dem = str(args.output_dir) + f'LVIS_DEM_{args.year}_FINAL.tif'
        clip_tiff(smooth_dem, shape, final_dem)

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round(((time.process_time() - start) / 60), 2)} minutes")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")


if __name__ == '__main__':
     
     main()
