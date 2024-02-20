'''
Task2b: Produce DEM of Pine Island Glacier, 2009
'''

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *


if __name__ == '__main__':
    start = time.process_time()

    # Find DEM subsets and study area
    dem_list = glob.glob('/home/s1949330/Documents/MSc_OOSA/project_data/2009/*.tif')
    print(f'Number of DEM subsets: {len(dem_list)}')

    # Filter subsets within range of study area (to merge all 244 subsets at once, RAM = ~9GB)
    glacier = '/home/s1949330/Documents/MSc_OOSA/project_data/pine_island/pine_island_glacier.shp'
    filtered_subsets = filter_subsets(dem_list, glacier)

    # Merge filtered subsets in appropriate batches
    merged_output_dir = '/home/s1949330/Documents/MSc_OOSA/project_data/2009/filtered/'
    merge_subsets(filtered_subsets, merged_output_dir, step_size = 10)

    # Combine merged subsets
    filtered_list = glob.glob('/home/s1949330/Documents/MSc_OOSA/project_data/2009/filtered/*.tif')
    output_dir = '/home/s1949330/Documents/MSc_OOSA/project_data/2009/filtered/combined/'
    merge_subsets(filtered_list, output_dir, len(filtered_list))
    os.rename(str(output_dir) + 'merged_subsets0.tif', str(output_dir) + 'LVIS_DEM_2009.tif')

    # Crop combined DEM to study area polygon
    pine_island = '/home/s1949330/Documents/MSc_OOSA/project_data/pine_island/pine_island_glacier.shp'
    lvis_dem = str(output_dir) + 'LVIS_DEM_2009.tif'
    pig_dem = str(output_dir) + 'PIG_DEM_2009.tif'
    clip_geotiff(lvis_dem, pine_island, pig_dem)

    # Visualise DEM of Pine Island Glacier, 2009
    PIG_DEM_2009 = rio.open(str(output_dir) + 'PIG_DEM_2009.tif')
    data = PIG_DEM_2009.read(1, masked = True)
    plt.figure(figsize = (8, 8))
    plt.imshow(data, cmap = 'magma', extent = PIG_DEM_2009.bounds, origin = 'upper')
    cbar = plt.colorbar(shrink = 0.5)
    cbar.set_label('Elevation (m)')
    plt.title("LVIS DEMs for Pine Island Glacier, 2009")
    plt.show()
    PIG_DEM_2009.close()

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round((time.process_time() - start), 2)} seconds")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")