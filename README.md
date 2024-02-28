# LVIS Project

The main purpose of this project was to develop a library of python code to process NASA's LVIS LiDAR data to examine ice mass change of Pine Island Glacier from acquisition flights in 2009 and 2015.  

## Contents
- [Data](#Data)
- [Code Structure](#Code-Structure):
    - [readLVIS.py](#readLVIS.py) - *Base-class to read LVIS files and store data*
    - [processLVIS.py](#processLVIS.py) - *Sub-class to process LVIS data and estimate ground*
    - [plotLVIS.py](#plotLVIS.py) - *Sub-class to visualise LVIS data*
    - [methodsDEM.py](#methodsDEM.py) - *Class and methods to handle DEM geotiff files*
    - [manageRAM.py](#manageRAM.py) - *Methods to calculate CPU and RAM usage*
- [Usage Instructions](#Usage-Instructions):
    - [Packages](#Packages)
    - [Task 1](#Task-1) - *Read LVIS file and plot arbitrary waveform*
    - [Task 2](#Task-2) - *Produce DEM for single LVIS flight path*
    - [Task 3](#Task-3) - *Produce DEMs for all LVIS flights in 2009 and 2015*
    - [Task 4](#Task-4) - *Produce smooth DEMs for Pine Island Glacier in 2009 and 2015*
    - [Task 5](#Task-5) - *Calculate elevation and ice mass change for Pine Island Glacier, 2009-2015*
- [Outputs](#Outputs)

## Data
**PIG:**  In this study, the spatial extent of Pine Island Glacier (PIG) was defined as the marine-terminating subset of that defined by the GLIMS Glacier Database. The study area was manually assigned informed by both the GLIMS shapefile and LVIS flight paths in both 2009 and 2015. The shapefile used in this project is accessible in `shapes/pine_island_glacier.shp` alongside its supplementary files.   

**LVIS**:  
NASA's Land, Vegetation, and Ice Sensor [(LVIS)](https://lvis.gsfc.nasa.gov/Home/index.html) is an airborne LiDAR instrument which retrieves data on surface topography and 3-D structure. This project was designed to deal with LVIS data acquired during NASA's [Operation IceBridge](https://icebridge.gsfc.nasa.gov/), which monitored key glaciers at the poles during the gap in ICESat (2003-09) and ICESat-2 (2018-) missions. The LVIS data is available on the [NASA Earth Data Portal](https://search.earthdata.nasa.gov/search?q=LVIS) or via the [LVIS webpage](https://lvis.gsfc.nasa.gov/Data/GE.html?status=submitted).

## Code Structure

### Scripts
- [readLVIS.py](#readLVIS.py): *Base-class to read LVIS files and store data*.
- [processLVIS.py](#processLVIS.py): *Sub-class to process LVIS data and estimate ground*.
- [plotLVIS.py](#plotLVIS.py): *Sub-class to visualise LVIS data*.
- [methodsDEM.py](#methodsDEM.py): *Class and independent methods to handle DEM geotiff files*.

### readLVIS.py
File contains a class to read and store LVIS data from a HDF5 file format. The class holds methods to retrieve all or a spatial subset of LVIS data from a file. The default coordinate reference system encoding for all LVIS data is WGS84 / EPSG:4326.  

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

The class is initialised as follows: 

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

The main purpose of this class is to give the attribute of elevations to each waveform:
    
    LVIS.z

  
### processLVIS.py
File contains a class to process LVIS data, inheriting from the class **readLVIS** in *readLVIS.py*. The class initialiser is not overwritten and expects a LVIS file.  

*Class:* **processLVIS**  
The additional variables:
    
    threshold:    Value threshold outwidth is considered noise.
    zG:           Centre of gravity signal, calibrated specifically for ice.
    res:          Range resolution.
    noiseBins:    Number of bins as an integer.
    meanNoise:    Mean waveform noise.
    stdevNoise:   Standard deviation of waveform noise.
    denoised:     Smoothed, denoised waveform.

The class is initialised as follows: 

    from processLVIS import processLVIS
    LVIS = processLVIS(filename)

The class holds the following methods:
    
    estimate_ground():    Returns ground estimate from waveform.
    set_threshold():      Sets waveform noise threshold.
    centre_gravity():     Finds centre of gravity of denoised waveforms.
    find_stats():         Calculates standard deviation and mean of noise.
    denoise():            Removes noise in waveform data.

The main purpose of this class is to give the attribute of ground estimate to each waveform:
    
    LVIS.zG

### plotLVIS.py
File contains a class to visualise LVIS data, inheriting from the class **processLVIS** in *processLVIS.py*. The class initialiser is not overwritten and expects a LVIS file.  

*Class:* **plotLVIS**  
The additional variables:
    
    inProj:               Value threshold outwidth is considered noise.
    outProj:              Centre of gravity signal, calibrated specifically for ice.
    x, y:                 Range resolution.
    bounds:               Number of bins as an integer.
    plot:                 Mean waveform noise.
    minX, minY:           Bottom left coordinate of file bounds.
    maxX, maxY:           Top right coordinate of file bounds.
    nX, nY:               Number of horizontal and vertical pixels.
    xInds, yInds:         Indices of horizontal and vertical pixels.
    pixel_footprints:     Number of waveform returns intersecting with a given pixel.
    pixel_mean:           Average waveform return of those intersecting with a given pixel.
    imageArr:             Ground estimates from footprints intersecting with each pixel stored in a 2-D numpy array.

The class is initialised as follows: 

    from plotLVIS import plotLVIS
    LVIS = plotLVIS(filename)

The class holds the following methods:
    
    reproject_coords():    Returns ground estimate from waveform.
    reproject_bounds():    Reprojects the coordinate reference system encoded in file bounds from longitude/latitude to an anticipated x, y with metre units. 
    plot_wave():           Creates a figure illustrating one waveform return as a function of intensity and elevation.
    write_tiff():          Writes 2-D numpy array of average footprint ground estimates per pixel.

The main purpose of this class is to illustrate one waveform return and produce a geotiff raster of ground estimates:
    
    LVIS.plot
    LVIS.imageArr

### methodsDEM.py
File contains an independent class and other methods to handle and manipulate DEM geotiff raster files. The class initialiser expects a geotiff file.  

*Class:* **methodsDEM**  
The additional variables:
    
    ds:                Geotiff as a dataset object.
    nX, nY:            Number of horizontal and vertical pixels.
    transform_ds:      Stored geolocation information.
    xOrigin, yOrigin:  Coordinates of raster x and y corners.
    pixelWidth:        Spatial resoution in horizontal direction.
    pixelHeight:       Spatial resolution in vertical direction.
    data:              Geotiff data in a 2-D numpy array.

The class is initialised as follows: 

    from methodsDEM import methodsDEM
    DEM = methodsDEM(filename)

The class holds the following methods:
    
    read_tiff():           Reads a geotiff and its data as a 2-D numpy array.
    calculate_change():    Calculates change between data of two geotiff raster files.
    write_tiff():          Writes a geotiff raster from a 2-D numpy array.

The main purpose of this class is to calculate the difference between the data of two geotiff files and produce a new geotiff of the change values.
    
    DEM.data
    change, mean = DEM.calculate_change(other_tiff, avg = False)
    DEM.write_tiff(data, output_filename, epsg)




## Usage Instructions


## Outputs

