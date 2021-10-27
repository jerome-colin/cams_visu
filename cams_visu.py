#! /usr/bin/env python

"""
Basic CAMS product viewer for MAJA AOT/MR/HR
"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "0.0.0"

import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as pl
import argparse, sys, glob


def find_location_index(lat, lon, data):
    """
    Return the closest lat and lon idx from DD values
    :param lat: DD latitude [-90:90]
    :param lon: DD longitude [0:360]
    :param data: a netCDF dataset with lat and lon dimensions
    :return: latitude index, longitude index
    """
    lat_idx = get_closest_index(lat, data['latitude'][:])

    if lon < 0:
        allround_lon = 360+lon
        print("WARNING: longitude should be [0:360]. Set %6.4f to %6.4f" % (lon, allround_lon))
    else:
        allround_lon = lon

    lon_idx = get_closest_index(allround_lon, data['longitude'][:])

    print("INFO: location (%5.3fN, %5.3fE) has index (%i, %i)" % (lat, lon, lat_idx, lon_idx))

    return lat_idx, lon_idx


def get_aot(aot_dataset, lat_idx, lon_idx):
    """
    Return species ratios to AOD (%), total AOD, aerosol short and long-names
    :param aot_dataset: netCDF dataset for AOT
    :param lat_idx: latitude as index
    :param lon_idx: longitude as index
    :return: (4) species ratios to AOD (%), total AOD, aerosol short and long-names
    """
    aot_var_names = []
    aot_var_longnames = []
    for var in aot_dataset.variables.values():
        aot_var_names.append(var.name)
        aot_var_longnames.append("   %s" % var.long_name)  # .split(' ')[:2])

    # Get AOT value per species
    aot = []
    for aer in aot_var_names[3:]:
        aot.append(aot_dataset[aer][0, lat_idx, lon_idx])
        #print("%s : %12.8f" % (aer, aot_dataset[aer][0, lat_idx, lon_idx]))

    aot_norm = aot / sum(aot) * 100

    return aot_norm, sum(aot), aot_var_names, aot_var_longnames


def get_closest_index(target, vector):
    """
    Return the index of the vector element closest to target
    :param target: a target value, eg. a latitude
    :param vector: an 1D array of the same type as target
    :return: an index as int
    """
    return (np.abs(vector - target)).argmin()


def get_mr(mr_dataset, lat_idx, lon_idx):
    """
    Return a 2D cube of ('aerosol', 'MR along altitude'), plus names and display settings
    :param mr_dataset: netCDF dataset of MR
    :param lat_idx: latitude as index
    :param lon_idx: longitude as index
    :return: (4) mr_cube, aerosols_variable_names, aerosols_variable_color, aerosols_variable_linestyle
    """
    # Define aerosol parameters
    aerosols_variable_names = ["aermr01", "aermr02", "aermr03", "aermr04", "aermr05", "aermr06", "aermr07", "aermr08",
                               "aermr09", "aermr10", "aermr11", "aermr16", "aermr17", "aermr18"]

    aerosols_variable_color = ['tab:blue', 'tab:blue', 'tab:blue', 'tab:orange', 'tab:orange', 'tab:orange',
                               'tab:green', 'tab:green', 'tab:grey', 'tab:grey', 'tab:red', 'tab:cyan', 'tab:cyan',
                               'tab:olive']
    aerosols_variable_linestyle = ['dotted', 'dashed', 'solid', 'dotted', 'dashed', 'solid', 'dashed', 'solid',
                                   'dashed', 'solid', 'solid', 'dashed', 'solid', 'solid']

    # Create an array of dimensions ('aerosol species', 'mixing ratio along level')
    mr_cube = np.zeros((len(aerosols_variable_names), len(mr_dataset['level'][:])))
    for i in range(len(aerosols_variable_names)):
        mr_cube[i, :] = mr_dataset[aerosols_variable_names[i]][:, :, lat_idx, lon_idx][0]

    return mr_cube, aerosols_variable_names, aerosols_variable_color, aerosols_variable_linestyle


def get_pressure_levels(dataset):
    """
    Return pressure levels equivalent to model levels for either 137 or 69 levels products
    :param dataset: a netCDF dataset of MR
    :return: ps_levels (vect)
    """
    # Check length of 'level' dimension to define equivalent pressure level values
    if len(dataset['level'][:]) == 137:
        ps_levels = [0.02, 0.031, 0.0457, 0.0683, 0.0975, 0.1361, 0.1861, 0.2499, 0.3299, 0.4288, 0.5496, 0.6952,
                     0.869, 1.0742, 1.3143, 1.5928, 1.9134, 2.2797, 2.6954, 3.1642, 3.6898, 4.2759, 4.9262, 5.6441,
                     6.4334, 7.2974, 8.2397, 9.2634, 10.372, 11.5685, 12.8561, 14.2377, 15.7162, 17.2945, 18.9752,
                     20.751, 22.6543, 24.6577, 26.7735, 29.0039, 31.3512, 33.8174, 36.4047, 39.1149, 41.9493,
                     44.9082, 47.9915, 51.199, 54.5299, 57.9834, 61.5607, 65.2695, 69.1187, 73.1187, 77.281,
                     81.6182, 86.145, 90.8774, 95.828, 101.0047, 106.4153, 112.0681, 117.9714, 124.1337, 130.5637,
                     137.2703, 144.2624, 151.5493, 159.1403, 167.045, 175.2731, 183.8344, 192.7389, 201.9969,
                     211.6186, 221.6146, 231.9954, 242.7719, 253.9549, 265.5556, 277.5852, 290.0548, 302.9762,
                     316.3607, 330.2202, 344.5663, 359.4111, 374.7666, 390.645, 407.0583, 424.019, 441.5395,
                     459.6321, 478.3096, 497.5845, 517.4198, 537.7195, 558.343, 579.1926, 600.1668, 621.1624,
                     642.0764, 662.8084, 683.262, 703.3467, 722.9795, 742.0855, 760.5996, 778.4661, 795.6396,
                     812.0847, 827.7756, 842.6959, 856.8376, 870.2004, 882.791, 894.6222, 905.7116, 916.0815,
                     925.7571, 934.7666, 943.1399, 950.9082, 958.1037, 964.7584, 970.9046, 976.5737, 981.7968,
                     986.6036, 991.023, 995.0824, 998.8081, 1002.225, 1005.3562, 1008.2239, 1010.8487, 1013.25]
        print("INFO: mixing ratio dataset with 137 levels")
    elif len(dataset['level'][:]) == 69:
        ps_levels = [0.02, 0.0467, 0.0975, 0.1861, 0.3299, 0.5496, 0.869, 1.3143, 1.9134, 2.6954, 3.6898, 4.9262,
                     6.4334, 8.2397, 10.372, 12.8561, 15.7162, 18.9752, 22.6543, 26.7735, 31.3512, 36.4047, 41.9493,
                     47.9915, 54.5299, 61.5607, 69.1187, 77.281, 86.145, 95.828, 106.4153, 117.9714, 130.5637,
                     144.2624, 159.1403, 175.2731, 192.7389, 211.6186, 231.9954, 253.9549, 277.5852, 302.9762,
                     330.2202, 359.4111, 390.645, 424.019, 459.6321, 497.5845, 537.7195, 579.1926, 621.1624,
                     662.8084, 703.3467, 742.0855, 778.4661, 812.0847, 842.6959, 870.2004, 894.6222, 916.0815,
                     934.7666, 950.9082, 964.7584, 976.5737, 986.6036, 995.0824, 1002.225, 1008.2239, 1013.25]
        print("INFO: mixing ratio dataset with 69 levels")
    else:
        print("ERROR: unknown level size")
        sys.exit(2)

    return ps_levels


def get_products(path):
    """
    Get filenames of files in path
    :param path: CAMS product path, expected AOT, MR and RH in netCDF4
    :return: filenames
    """
    files_list = glob.glob(path + '/*')
    file_mixing_ratio = [b for b in files_list if "_MR_" in b][0]
    file_aot = [b for b in files_list if "_AOT_" in b][0]
    file_relative_humidity = [b for b in files_list if "_RH_" in b][0]

    return file_mixing_ratio, file_aot, file_relative_humidity


def get_collection(path):
    return glob.glob(path + '/*.DIR')


def get_timestamp(file):
    """
    Parse filename and returns raw and nice timestamps
    :param file: filename
    :return: (2) raw, nice
    """
    timestamp = file.split("/")[-1].split("_")[-1].split(".")[0]

    return timestamp, "%s-%s-%s %s:%s UTC" % (
    timestamp[:4], timestamp[4:6], timestamp[6:8], timestamp[11:13], timestamp[13:15])


def show_location(filename, lat, lon):
    # Open netCDF datasets
    try:
        dataset = nc.Dataset(filename)

    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    # Find location indexes (assumes same (x,y) spatial resolution for both 3 files)
    lat_idx, lon_idx = find_location_index(lat, lon, dataset)

    print("DEBUG: Latitude of grid %i in netCDF is %6.4f, you asked for %6.4f" % (lat_idx, dataset['latitude'][lat_idx], lat))
    print("DEBUG: Longitude of grid %i in netCDF is %6.4f, you asked for %6.4f" % (lon_idx, dataset['longitude'][lon_idx], lon))
    print("DEBUG: Longitude ranges from %6.4f to %6.4f in netCDF" % (np.min(dataset['longitude'][:]), np.max(dataset['longitude'][:])))


def synthesis_plot(file_mixing_ratio, file_relative_humidity, file_aot, lat, lon, site_name=None, max_mr=2e-8):
    """
    Main routine
    :param file_mixing_ratio:
    :param file_relative_humidity:
    :param file_aot:
    :param lat:
    :param lon:
    :param site_name:
    :param max_mr:
    :return:
    """

    # Open netCDF datasets
    try:
        mr_dataset = nc.Dataset(file_mixing_ratio)
        rh_dataset = nc.Dataset(file_relative_humidity)
        aot_dataset = nc.Dataset(file_aot)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    # Find location indexes (assumes same (x,y) spatial resolution for both 3 files)
    lat_idx, lon_idx = find_location_index(lat, lon, mr_dataset)

    # Get pressure levels from model level in dataset
    mr_ps_levels = get_pressure_levels(mr_dataset)
    rh_ps_levels = rh_dataset['level'][:]

    # Get MR
    mr_cube, aerosols_variable_names, aerosols_variable_color, aerosols_variable_linestyle = get_mr(mr_dataset, lat_idx,
                                                                                                    lon_idx)

    # Get AOT
    aot_norm, aot, aot_var_names, aot_var_longnames = get_aot(aot_dataset, lat_idx, lon_idx)

    # Figure settings
    fig, axs = pl.subplots(1, 3, sharex=False, sharey=False, constrained_layout=True, figsize=(19, 8))
    fig.suptitle(("%s (%5.2f°N, %5.2f°E) @ %s, AOD(550nm) = %5.3f" % (
    site_name, mr_dataset['latitude'][lat_idx], mr_dataset['longitude'][lon_idx], get_timestamp(file_mixing_ratio)[1], aot)),
                 fontsize='xx-large')

    # MR subplot
    axs[0].invert_yaxis()
    axs[0].set_xlabel('CAMS Aerosols mixing ratio (kg/kg), %i levels' % len(mr_ps_levels), fontsize='x-large')
    axs[0].set_ylabel('Air pressure (hPa)', fontsize='x-large')
    axs[0].set_xlim([0, max_mr])
    for p in range(len(aerosols_variable_names)):
        axs[0].plot(mr_dataset[aerosols_variable_names[p]][:, :, lat_idx, lon_idx][0], mr_ps_levels,
                    aerosols_variable_color[p], linestyle=aerosols_variable_linestyle[p],
                    label=mr_dataset[aerosols_variable_names[p]].long_name)

    axs[0].legend(fontsize='large')

    # RH subplot
    axs[1].invert_yaxis()
    axs[1].set_xlabel("ECMWF relative humidity (%%), %i levels" % len(rh_ps_levels), fontsize='x-large')
    # axs[1].set_ylabel('Air pressure (hPa)')
    axs[1].yaxis.tick_right()
    axs[1].set_xlim([0, 100])
    axs[1].plot(rh_dataset['r'][:, :, lat_idx, lon_idx][0], rh_ps_levels, '.-', label='Relative humidity')

    # AOT subplot
    aot_variable_color = ['tab:orange', 'tab:green', 'tab:grey', 'tab:red', 'tab:cyan', 'tab:blue', 'tab:olive']
    axs[2].barh(aot_var_longnames[3:], aot_norm, color=aot_variable_color)
    axs[2].set_xlim([0, 100])
    axs[2].set_xlabel('CAMS species contribution to AOD at 550nm (%)', fontsize='x-large')
    axs[2].set_yticklabels(aot_var_longnames[3:], horizontalalignment="left", fontsize='x-large')

    # Saving figure
    pl.savefig("%s_%s.png" % (site_name, get_timestamp(file_mixing_ratio)[0]))


def main():
    """
    Produce a synthetic plot from CAMS products for a give site defined by its latitude/longitude. Be aware that the
    profiles plotted will match the closest (lat,lon) grid of the netCDF files, values are not interpolated to the
    exact location you give in input. Site name is not mandatory byt will make output filename nicer.

    Usage example :
    ~/S2__OPER_EXO_CAMS_20210301T120000_21000101T000000.DBL.DIR --lat 50.5 --lon 3.2 --site Lille

    :return: a PNG file
    """
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Path to a CAMS collection")
    parser.add_argument("--lat", help="Latitude in decimal degrees", type=float, required=True)
    parser.add_argument("--lon", help="Longitude in decimal degrees", type=float, required=True)
    parser.add_argument("--site", help="Site name for plot title", type=str, required=False)
    parser.add_argument("--maxmr", help="Maximum MR value, defaults to 2E-8", type=float, required=False, default=2e-8)
    args = parser.parse_args()

    collection = get_collection(args.directory)



    for p in collection:
        # Get file names:
        file_mixing_ratio, file_aot, file_relative_humidity = get_products(p)

        show_location(file_aot, args.lat, args.lon)

        # Produce plot
        synthesis_plot(file_mixing_ratio, file_relative_humidity, file_aot, args.lat, args.lon, site_name=args.site, max_mr=args.maxmr)

    sys.exit(0)


if __name__ == "__main__":
    main()
