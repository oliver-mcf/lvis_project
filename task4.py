'''
Task4: Produce Gap-Filled DEMs of Pine Island Glacier
'''

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *


def main():
    '''Main function to smooth flight-path DEMs'''
    
    # Define command line parser to use for multiple LVIS years
    parser = argparse.ArgumentParser(description = "Perform smoothing for LVIS flight path-DEMs from a specified year.")
    parser.add_argument("year", help = "Year of LVIS data (2009 or 2015)")
    args = parser.parse_args()

    start = time.process_time()

    # Perform smoothing algorithm
    flight_dem = f'/home/s1949330/Documents/MSc_OOSA/project_data/{args.year}/filtered/combined/PIG_DEM_{args.year}.tif'
    smooth_dem = f'/home/s1949330/Documents/MSc_OOSA/project_data/{args.year}/filtered/combined/PIG_DEM_{args.year}_FINAL.tif' 
    smooth_geotiff(flight_dem, smooth_dem, window_size = 1)

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round((time.process_time() - start), 2)} seconds")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")



if __name__ == '__main__':
    
    main()

    # python task4.py 2009
    #                 2015