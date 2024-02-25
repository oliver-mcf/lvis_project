'''
Task2: Produce DEM for Single LVIS Flight
Task3: Produce DEM for all LVIS Flights in 2009 and 2015
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
    '''Main function to batch process LVIS and produce flight-path DEMs for a given year'''
    
    # Define command line parser to use for multiple LVIS years
    parser = argparse.ArgumentParser(description = "Process LVIS files from a specified year.")
    parser.add_argument("year", help = "Year of LVIS data, 2009 or 2015")
    parser.add_argument("--single_file", action = "store_true", help = "Process only one LVIS file to DEM")
    parser.add_argument("--res", type = int, default = 30, help = "Spatial resolution of DEM in meters")
    parser.add_argument("--output_dir", help = "Output directory for DEM(s)")
    args = parser.parse_args()
    
    # Start CPU runtime
    start = time.process_time()

    # Identify directory containing LVIS files
    dir = f'/geos/netdata/oosa/assignment/lvis/{args.year}/'
    lvis_files = [f for f in os.listdir(dir) if f.endswith('.h5')]
    print('Number of LVIS files: ', len(lvis_files))

    # Isolate one LVIS file
    for file in lvis_files:
        lvis_file = os.path.join(dir, file)

        # Initialize class
        LVIS = plotLVIS(lvis_file, onlyBounds = True)
    
        # Define subset size, RAM < 2 GB
        subset_size = (LVIS.bounds[2] - LVIS.bounds[0]) / 16
        for x0 in np.arange(LVIS.bounds[0], LVIS.bounds[2], subset_size):
            x1 = x0 + subset_size
            for y0 in np.arange(LVIS.bounds[1], LVIS.bounds[3], subset_size):
                y1 = y0 + subset_size

                # Read subset of LVIS data
                LVIS_subset = plotLVIS(lvis_file, minX = x0, minY = y0, maxX = x1, maxY = y1, setElev = True)
                if LVIS_subset.nWaves == 0:
                    continue
            
                # Calculate footprint ground estimates
                LVIS_subset.set_elevations()
                LVIS_subset.estimate_ground()
                print(f'DEM subset ground estimates: {LVIS_subset.zG[:5]}')

                # Convert footprints to DEM
                LVIS_subset.reproject_coords(3031)
                outName = f'{args.output_dir}/DEM_subset_{args.year}.x.{x0}.y.{y0}.tif'
                LVIS_subset.write_tiff(LVIS_subset.zG, LVIS_subset.x, LVIS_subset.y, res = args.res, filename = outName, epsg = 3031)

                # Produce DEM for one LVIS file if condition is applied
                if args.single_file:
                    break

        print(f'-----------------LVIS FILE DEM COMPLETE-----------------\n')

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round(((time.process_time() - start) / 60), 2)} minutes")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")

###########################################
    
if __name__ == '__main__':
    main()