'''
Task1: Read LVIS file, Plot Waveform
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
    '''Main function to read a LVIS file and plot a waveform at a given index'''

    # Define command line parser to read a LVIS file and a waveform at a given index   
    parser = argparse.ArgumentParser(description = 'Read LVIS File and Plot Waveform')
    parser.add_argument('lvis_file', type = str, help = 'Path to the LVIS file')
    parser.add_argument('--waveform_index', type = int, default = 100, help = 'Index of waveform in subset of file to plot')
    args = parser.parse_args()

    start = time.process_time()

    # Initialize LVIS class
    LVIS = plotLVIS(args.lvis_file, onlyBounds = True)

    # Subset LVIS data
    x0, y0 = LVIS.bounds[0], LVIS.bounds[1]
    x1, y1 = x0 + 0.5, y0 + 0.5

    # Read subset LVIS data
    LVIS_subset = plotLVIS(args.lvis_file, minX = x0, minY = y0, maxX = x1, maxY = y1)
    LVIS_subset.reproject_coords(3031)
    LVIS_subset.set_elevations()

    # Save subset coordinates to visualize
    df = pd.DataFrame({'x': LVIS_subset.x, 'y': LVIS_subset.y})
    df.to_csv('task1_subset.csv', index = False)
    print(df.head())

    # Plot one waveform from subset
    waveform = LVIS_subset.one_waveform(ind = args.waveform_index)
    LVIS_subset.plot_wave(waveform[1], waveform[0], outName = f'waveform_{args.lvis_file}.png')
    print(f'Waveform at index {args.waveform_index}: {LVIS_subset.x[args.waveform_index]}, {LVIS_subset.y[args.waveform_index]} (EPSG:3031)')

    # Print the number of waveforms in the subset
    num_waveforms = len(LVIS_subset.x)
    print(f'Number of waveforms in the subset: {num_waveforms}')

    # Calculate CPU runtime and RAM usage
    print(f"CPU runtime: {round((time.process_time() - start), 2)} seconds")
    ram = psutil.Process().memory_info().rss
    print(f"RAM usage: {convert_bytes(ram)}")


if __name__ == '__main__':

    main()

    # python task1.py '/geos/netdata/oosa/assignment/lvis/2009/... .h5' --waveform_index 150