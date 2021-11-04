# This repository contains a set of small utilities to analyse and vizualize time series of CAMS aerosols datasets. 

WARNING: netCDF input files content is expected to match the ones created by StartMaja, with an EarthExplorer structure.

## cams_visu

For a given CAMS product in 'path', returns a plot summarizing aerosols mixing ratio profils, relative humidity profile and contribution of aerosols species to the AOD.

### Example of cams_visu output:

![Demo cams_visu](https://github.com/jerome-colin/cams_visu/blob/master/cams_visu_demo.png)

## cams_extract_aod

For a given 'path' containing a collection of CAMS products, a given site location (lat/lon in DD), reads all the AOT products and combine them to a site-specific netCDF file.

## cams_aot_timeline

Simple utility to plot timeseries of AOD. Input files can be generated with cams_extract_aod. The script will automatically switch from 5-species to 7-species datasets according to netcdf content. If the netcdf filename is of the form <anystring>_<anystring>_<sitename>_<whatever>.nc, sitename will be picked-up from filename. Otherwise, use --sitename option.

### Usage:

`
./cams_aod_timeline ncfiles/cams_aod_Calcuta_7.nc --sitename Calcuta --outdir ./figs
`

### Example of outputs:

![Demo stacked plot](https://github.com/jerome-colin/cams_visu/blob/master/Calcuta_7.png)
