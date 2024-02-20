'''
Task1: Read LVIS file, Plot Waveform
'''

# Import objects and methods
from readLVIS import *
from processLVIS import *
from plotLVIS import *
from methodsDEM import *


if __name__ == '__main__':
    start = time.process_time()

    # Initialise class
    lvis_file = '/geos/netdata/oosa/assignment/lvis/2009/ILVIS1B_AQ2009_1020_R1408_049700.h5'
    LVIS = plotLVIS(lvis_file, onlyBounds = True)
    
    # Subset LVIS data
    x0 = LVIS.bounds[0]
    y0 = LVIS.bounds[1]
    x1 = x0 + 0.1
    y1 = y0 + 0.1

    # Read subset LVIS data
    LVIS_subset = plotLVIS(lvis_file, minX = x0, minY = y0, maxX = x1, maxY = y1)
    LVIS_subset.reproject_coords(3031)
    LVIS_subset.set_elevations()

    # Save subset coordinates to visualise
    df = pd.DataFrame({'x': LVIS_subset.x, 'y': LVIS_subset.y})
    df.to_csv('/home/s1949330/Documents/MSc_OOSA/project_data/task1_subset.csv', index = False)
    print(df.head())
    
    # Plot one waveform from subset
    waveform = LVIS_subset.one_waveform(100)
    LVIS_subset.plot_wave(waveform[1], waveform[0], outName = 'waveform.png')
    print('Waveform:', LVIS_subset.x[0], LVIS_subset.y[0], '(EPSG:3031)')

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round((time.process_time() - start), 2)} seconds")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")