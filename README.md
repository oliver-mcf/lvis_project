# LVIS Project

The main purpose of this project was to develop a library of python code to process NASA's LVIS LiDAR data to examine ice mass change of Pine Island Glacier from acquisition flights in 2009 and 2015.  

## Contents
- [Data](#Data) >>> lvis, shapes
- [Code Structure](#Code-Structure) >>> directory, class/functions, main files
- [Usage Instructions](#Usage-Instructions) >>> imported libraries, tasks1-5 command line
- [Outputs](#Outputs) >>> tasks1-5

## Data
**PIG:**  In this study, the spatial extent of Pine Island Glacier (PIG) was defined as the marine-terminating subset of that defined by the GLIMS Glacier Database. The study area was manually assigned informed by both the GLIMS shapefile and LVIS flight paths in both 2009 and 2015. The shapefile used in this project is accessible in `shapes/pine_island_glacier.shp` alongside its supplementary files.   

**LVIS**:  
NASA's Land, Vegetation, and Ice Sensor [(LVIS)](https://lvis.gsfc.nasa.gov/Home/index.html) is an airborne LiDAR instrument which retrieves data on surface topography and 3-D structure. This project was designed to deal with LVIS data acquired during NASA's [Operation IceBridge](https://icebridge.gsfc.nasa.gov/), which monitored key glaciers at the poles during the gap in ICESat (2003-09) and ICESat-2 (2018-) missions. The LVIS data is available on the [NASA Earth Data Portal](https://search.earthdata.nasa.gov/search?q=LVIS) or via the [LVIS webpage](https://lvis.gsfc.nasa.gov/Data/GE.html?status=submitted).

## Code Structure
### readLVIS.py
File contains a class to read a store LVIS data from a HDF5 file format. The class holds methods to retrieve all or a spatial subset of LVIS data from a file. The default coordinate reference system encoding for all LVIS data is WGS84 / EPSG:4326.  

*Class:* **readLVIS**  
The data is stored as the variables:

    waves:   Lidar waveforms as a 2D numpy array.
    lon:     Longitude as a 1D numpy array.
    lat:     Latitude as a 1D numpy array.
    nWaves:  Number of waveforms in this file as an integer.
    nBins:   Number of bins per waveform as an integer.
    lZN:     Elevation of the bottom waveform bin.
    lZ0:     Elevation of the top waveform bin.
    lfid:    LVIS flight ID integer.
    shotN:   LVIS shot number for this flight.

The data is read as: 

    from readLVIS import readLVIS
    LVIS = readLVIS(filename)

The data can also be read as a subset, with defined bounds, and or with elevations set:
    
    LVIS = readLVIS(filename, minX, minY, maxX, maxY)
    LVIS = readLVIS(filename, onlyBounds = True)
    LVIS = readLVIS(filename, setElev = True)

The class holds the following methods:
    
    set_elevations():  Converts the compressed elevations into arrays of elevation, z.
    one_waveform():    Returns one LVIS waveform as an array.
    dump_coords():     Returns all coordinates of data as two numpy arrays.
    dump_bounds():     Returns the bottom left and top right coordinates of data in file.

The focal purpose of this class is to give the attribute of elevations to each waveform:
    
    LVIS.z

  
### processLVIS.py
File contains a class to process LVIS data, inheriting from the class `readLVIS` in *readLVIS.py*. The class initialiser is not overwritten and expects a LVIS file.  

*Class:* **processLVIS**  
The additional variables:
    
    threshold:    Value threshold outwidth is considered noise.
    zG:           Centre of gravity signal, calibrated specifically for ice.
    res:          Range resolution.
    noiseBins:    Number of bins as an integer.
    meanNoise:    Mean waveform noise.
    stdevNoise:   Standard deviation of waveform noise.
    denoised:     Smoothed, denoised waveform.

The data is processed as: 

    from processLVIS import processLVIS
    LVIS = processLVIS(filename)

The class holds the following methods:
    
    estimate_ground():    Returns ground estimate from waveform.
    set_threshold():      Sets waveform noise threshold.
    centre_gravity():     Finds centre of gravity of denoised waveforms.
    find_stats():         Calculates standard deviation and mean of noise.
    denoise():            Removes noise in waveform data.

The focal purpose of this class is to give the attribute of ground estimate to each waveform:
    
    LVIS.zG



## Usage Instructions


## Outputs

