#! /usr/bin/env python

"""
CAMS AOD timeline plot

Purpose : plots AOD for either 5-species or 7-species aerosols datasets produced by 'cams_extract_aod.py'

v0.0.0 : initial release, tested with both 5/7 species files
"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "0.1.1"

import sys, argparse
import xarray as xr
import matplotlib.pyplot as pl


def get_df(filename):
    """
    Convert netCDF to Pandas dataframe
    :param filename: netCDF AOD file
    :return: a Pandas dataframe
    """
    dataset = xr.open_dataset(filename)  # , engine='netcdf4').to_dataframe()
    df = dataset.to_dataframe()
    df.pop('latitude')
    df.pop('longitude')
    df = df.sort_index()
    # df.reset_index(inplace=True)

    return df


def get_mode(filename):
    """
    Get aerosol species count from filename
    :param filename:
    :return: 5 or 7
    """
    if (filename.split(".")[0][-2:]) == "_5":
        return 5
    if (filename.split(".")[0][-2:]) == "_7":
        return 7
    else:
        print("ERROR: no mode matching filename")
        sys.exit(1)


def get_ratios(df_i, mode=5):
    """
    Get ratios from AODs
    :param df_i:
    :param mode:
    :return: a dataframe
    """
    # deep copy, preserves original df
    df = df_i.copy(deep=True)

    if mode == 5:
        species = ['duaod550', 'omaod550', 'bcaod550', 'suaod550', 'ssaod550']
        df['Total'] = df['duaod550'] + df['omaod550'] + df['bcaod550'] + df['suaod550'] + df['ssaod550']
        df['rduaod550'] = df['duaod550'] / df['Total']
        df['romaod550'] = df['omaod550'] / df['Total']
        df['rbcaod550'] = df['bcaod550'] / df['Total']
        df['rsuaod550'] = df['suaod550'] / df['Total']
        df['rssaod550'] = df['ssaod550'] / df['Total']
        df = df.drop(['duaod550', 'omaod550', 'bcaod550', 'suaod550', 'ssaod550', 'Total'], axis=1)
        df_i.columns = ['dust', 'organic matter', 'black carbon', 'sufate', 'sea salt']
        df.columns = ['dust', 'organic matter', 'black carbon', 'sufate', 'sea salt']

    elif mode == 7:
        species = ['duaod550', 'omaod550', 'bcaod550', 'suaod550', 'ssaod550']
        df['Total'] = df['duaod550'] + df['omaod550'] + df['bcaod550'] + df['suaod550'] + df['ssaod550'] \
                      + df['niaod550'] + df['amaod550']
        df['rduaod550'] = df['duaod550'] / df['Total']
        df['romaod550'] = df['omaod550'] / df['Total']
        df['rbcaod550'] = df['bcaod550'] / df['Total']
        df['rsuaod550'] = df['suaod550'] / df['Total']
        df['rssaod550'] = df['ssaod550'] / df['Total']
        df['rniaod550'] = df['niaod550'] / df['Total']
        df['ramaod550'] = df['amaod550'] / df['Total']
        df = df.drop(['duaod550', 'omaod550', 'bcaod550', 'suaod550', 'ssaod550', 'niaod550', 'amaod550', 'Total'],
                     axis=1)
        df_i.columns = ['dust', 'organic matter', 'black carbon', 'sufate', 'sea salt', 'nitrate', 'ammonium']
        df.columns = ['dust', 'organic matter', 'black carbon', 'sufate', 'sea salt', 'nitrate', 'ammonium']

    return df


def plot_aod(filename, sitename, outdir):
    """
    Plot routine
    :param filename:
    :param sitename:
    :return: a PNG file
    """
    mode = get_mode(filename)

    if sitename=="guess":
        sitename = filename.split("/")[-1].split("_")[2]

    df_aod = get_df(filename)
    df_aod_ratio = get_ratios(df_aod, mode)

    fig, (ax1, ax2) = pl.subplots(2)

    if mode == 5:
        colors = ['tab:orange', 'tab:green', 'tab:grey', 'tab:red', 'tab:blue']

        df_aod.plot.area(stacked=True, ax=ax1, title=("CAMS AOD over %s (5-species)" % sitename), ylabel="AOD(550nm)",
                         figsize=(16, 8), color=colors).legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        df_aod_ratio.plot.area(stacked=True, ylim=(0, 1), ax=ax2, ylabel="Contribution to AOD(550nm) in %",
                               figsize=(16, 8),
                               color=colors).legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    elif mode == 7:
        colors = ['tab:orange', 'tab:green', 'tab:grey', 'tab:red', 'tab:blue', 'tab:cyan', 'tab:olive']

        df_aod.plot.area(stacked=True, ax=ax1, title=("CAMS AOD over %s (7-species)" % sitename), ylabel="AOD(550nm)",
                         figsize=(16, 8), color=colors).legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        df_aod_ratio.plot.area(stacked=True, ylim=(0, 1), ax=ax2, ylabel="Contribution to AOD(550nm) in %",
                               figsize=(16, 8),
                               color=colors).legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    pl.savefig("%s/%s_%s.png" % (outdir, sitename, mode))


def main():
    """
    For a given 'site', produce a plot of AOD along time
    :return: a PNG
    """
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="netCDF file produced by cams_extract_aod")
    parser.add_argument("--sitename", help="Name of the location (for plot title)", default="guess")
    parser.add_argument("--outdir", help="Path to output PNG", default=".")
    args = parser.parse_args()

    plot_aod(args.filename, args.sitename, args.outdir)

    sys.exit(0)


if __name__ == "__main__":
    main()
