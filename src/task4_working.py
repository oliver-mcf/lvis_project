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

    # Perform smoothing algorithm if condition is applied
    if args.smooth:
        smooth_dem = str(args.output_dir) + f'LVIS_DEM_{args.year}_FINAL.tif' 
        smooth_tiff(f'/home/s1949330/Documents/MSc_OOSA/project_data/{args.year}/filtered/combined/LVIS_DEM_2015.tif', smooth_dem)

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round(((time.process_time() - start) / 60), 2)} minutes")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")


if __name__ == '__main__':
     
     main()