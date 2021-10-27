#! /usr/bin/env python

"""
CAMS data extractor

Purpose : For a given 'path' containing a collection of CAMS products and a given site location (lat/lon in DD), reads
    all the AOT products and combine them to a single site-specific netCDF file.

v0.1.0 : bugfix for bug01. The timestamp of each product is tested. If any product in 'path' are dated
    before 2019-07-10 00:00:00 UTC, a dedicated 5 aerosol species file is created (suffixed '_5.nc'), while the later
    are concatenated in a file with suffix '_7.nc'. You may well get both depending on the range of your collection.

bug01 : if a collection covers dates before and after the 7 aerosols shift, only the 5 first species are stored in the
    netCDF stack.

v0.0.0 : initial released, passed successfully on a full CAMS collection covering 2017-2021
"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "0.1.0"

import argparse, sys, glob
import xarray as xr
import glob
from datetime import datetime


def get_timestamp(file):
    """
    Parse filename and returns raw and nice timestamps
    :param file: filename
    :return: (2) raw, nice
    """
    ts_str = file.split("/")[-1].split("_")[-1].split(".")[0]

    return datetime(int(ts_str[:4]), int(ts_str[4:6]), int(ts_str[6:8]), int(ts_str[11:13]), int(ts_str[13:15]))



def extract(path, output, lat, lon):
    list_of_cams_aot_files = glob.glob(path + '/**/*_AOT_*.nc', recursive = True)

    ts_seven_species = datetime(2019,7,10,0,0)
    print("INFO: shift to 7 aerosol species set to :", ts_seven_species)

    ds_5 = []
    ds_7 = []

    for f in list_of_cams_aot_files:

        try:
            ds_one_product = xr.open_dataset(f)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

        ds_one_product_site = ds_one_product.sel(latitude=lat, longitude=lon, method="nearest")

        ts = get_timestamp(f)

        if ts >= ts_seven_species:
            ds_7.append(ds_one_product_site)
        else:
            ds_5.append(ds_one_product_site)

    if len(ds_5) > 0:
        combined_5 = xr.concat(ds_5, dim='time')
        combined_5.to_netcdf(output[:-3]+"_5.nc", 'w')

    if len(ds_7) > 0:
        combined_7 = xr.concat(ds_7, dim='time')
        combined_7.to_netcdf(output[:-3]+"_7.nc", 'w')

def main():
    """
    For a given PATH, LAT, LON,
    read all cams aot netcdf files in PATH,
    extract values for (LAT, LON)
    output site specific values to a new netCDF file in OUTPUT
    :return: a netCDF file
    """
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Path to a CAMS collection")
    parser.add_argument("output", help="Fullpath name of the output netCDF file")
    parser.add_argument("--lat", help="Latitude in decimal degrees", type=float, required=True)
    parser.add_argument("--lon", help="Longitude in decimal degrees", type=float, required=True)
    args = parser.parse_args()

    extract(args.directory, args.output, args.lat, args.lon)

    sys.exit(0)


if __name__ == "__main__":
    main()