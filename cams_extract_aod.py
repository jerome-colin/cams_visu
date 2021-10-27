#! /usr/bin/env python

"""
Basic CAMS product viewer for MAJA AOT/MR/HR
"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "0.0.0"

import argparse, sys, glob
import xarray as xr
import glob


def extract(path, output, lat, lon):
    list_of_cams_aot_files = glob.glob(path + '/**/*_AOT_*.nc', recursive = True)

    ds = []

    for f in list_of_cams_aot_files:
        try:
            ds_one_product = xr.open_dataset(f)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

        ds_one_product_site = ds_one_product.sel(latitude=lat, longitude=lon, method="nearest")

        ds.append(ds_one_product_site)

    combined = xr.concat(ds, dim='time')

    combined.to_netcdf(output, 'w')


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