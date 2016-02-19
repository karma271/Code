#!/usr/local/bin/python

import pandas as pd # Pandas for data structures useful this program
import numpy as np # Numpy for various math structures and functions
from scipy import stats # Scipy statistics functions
import os, sys # Base functions for accessing data on the computer
import argparse # For parsing input arguments from the commandline
from natsort import natsorted
from xlsxwriter.utility import xl_rowcol_to_cell

class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))

def is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname

def get_args():
    """Get CLI arguments and options"""
    parser = argparse.ArgumentParser()

    parser.add_argument('EXPROOTPATH',
                        help="path to files and folders for the experiment",
                        action=FullPaths, type=is_dir)

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    results = parser.parse_args()

    return results

def read_angiotool_files():
    """ Read in the AngioTool data for each device"""
    # Retrive the file names and full file paths of the excel files with the data
    fpath = []
    fnames = []
    dnames = []

    for root, dirs, files in os.walk(EXPROOTPATH, topdown=False):
        for fn in files:
            if fn.endswith(".xls") and not fn.endswith("data.xls"):
                fpath.append(os.path.join(root, fn))
                fnames.append(fn)
        for dn in dirs:
            dnames.append(dn)

    # Remove the excel and plots directory from the list if it exists
    os.chdir(EXPROOTPATH)
    if os.path.isdir('plots'):
        dnames.remove('plots')

    if os.path.isdir('excel'):
        dnames.remove('excel')

    # Set device names based on directory names
    dev_names = dnames

    # Determine the Device Intervals from the excel file names
    dev_int = []
    for item in fnames:
        # Strip the .xls off the file names and use these as the intervals
        dev_int.append(os.path.splitext(item)[0])
    # Remove Duplicate Items
    dev_int = list(set(dev_int))
    # Sort the list
    dev_int = natsorted(dev_int)

    # Import the excel data
    # Create an index for the file paths to the excel files
    i_fp = 0
    # Create a blank dictionary to add the imported excel data to
    all_dict = {}

    # test to make sure there's the correct number of files to avoid issues
    if len(fpath) == len(dev_names) * len(dev_int):
        for item_dn in dev_names: # For each device
            for item_di in dev_int: # For each device interval
                item_fp = fpath[i_fp] # Get the file path based on the index
                all_dict[(item_di, item_dn)] = pd.read_excel(item_fp,
                                                             header=2,
                                                             convert_float=False,
                                                             na_values=['NA'])
                i_fp += 1 # increment the file path index
    else: # throw an error
        sys.exit("Error : The program has stopped because there's an excel file missing.\n"
                 "The total number of files for the devices does not equal the devices\n"
                 "mutltiplied by the intervals.  Please place a dummy file in the\n"
                 "appropriate directory.")

    # Place the dictionary data into a dataframe
    dev_data = pd.concat(all_dict, axis=0, names=['interval', 'device', 'well'])
    dev_data.columns.names = ['field']

    # Determine number of wells
    n_wells = len(dev_data.index.levels[2])

    # Replace Junctions values of 0 with 1 to avoid NaNs
    index = dev_data['Total Number of Junctions'] <= 0
    dev_data.loc[index, 'Total Number of Junctions'] = 1
    index = dev_data['Junctions density'] <= 0
    dev_data.loc[index, 'Junctions density'] = 1

    return dev_data, n_wells

def sort_nat(dev_data):
    """Sort dev_data naturally"""
    dev_data = dev_data.reindex(index=natsorted(dev_data.index))
    return dev_data

def rm_nan(df):
    """Get rid of data that isn't a number"""
    df = df.select_dtypes(include=[np.number])
    return df

def norm_to_0hr(df):
    """Normalize to the 0 hr value"""
    df = df.T.stack(level=['device', 'well'])
    df = df.divide(df['0hr'], axis=0).stack().unstack(-2)
    return df

def calc_stats(df, n_wells):
    """Calculate Mean, StDev, and Standard Error"""
    df2 = pd.DataFrame(index=df.index, columns=['mean', 'stdev', 'stErr'])
    df2['mean'] = df.ix[:, 0:n_wells].mean(axis=1)
    df2['stdev'] = df.ix[:, 0:n_wells].std(axis=1)
    df2['stErr'] = df.ix[:, 0:n_wells].apply(stats.sem, axis=1)
    return df2

def norm_to_avg(df):
    """Normalize values to average of control"""
    df = df.unstack(['device', 'well']).stack(['field']).reorder_levels(['field', 'interval'])
    avg = df['Control'].mean(axis=1)
    df = df.divide(avg, axis=0)*100
    df = df.stack(['device'])
    df = df.reorder_levels(['field', 'device', 'interval'], axis=0)
    df = df.sort()
    return df

def t_test(df):
    """Perform a t-test"""
    df = df.reorder_levels(['field', 'interval', 'device']).sort()
    df2 = pd.DataFrame(index=df.index, columns=['p-value'])

    for i in set(df.index.get_level_values(0)):
        for j in set(df.index.get_level_values(1)):
            for k in set(df.index.get_level_values(2)):
                [t, p] = stats.ttest_ind(df.loc[(i, j, 'Control')],
                                         df.loc[(i, j, k)], 0, equal_var=True)
                df2.loc[(i, j, k), 'p-value'] = p
    df2 = df2.reorder_levels(['field', 'device', 'interval']).sort()
    return df2

def write_excel_data(dev_data, norm_to_ctrl, norm_to_mean):
    """Write data into a file"""

    # Define excel directory
    xls_dir = "./excel"

    # Change directory to EXPROOTPATH
    os.chdir(EXPROOTPATH)

    # Check to see if excel directory exists and if it doesn't make it
    try:
        os.makedirs(xls_dir)
    except OSError:
        if not os.path.isdir(xls_dir):
            raise

    # Reorder
    dev_data = dev_data.reorder_levels(['device', 'interval', 'well'])
    norm_to_ctrl = norm_to_ctrl.stack().unstack(-4).reorder_levels(['device', 'interval', 2]) #.sort_index(0)
    norm_to_mean = norm_to_mean.stack().unstack(-4).reorder_levels(['device', 'interval', 2])

    # Sort
    dev_data = dev_data.reindex(index=natsorted(dev_data.index))
    norm_to_ctrl = norm_to_ctrl.reindex(index=natsorted(norm_to_ctrl.index))
    norm_to_mean = norm_to_mean.reindex(index=natsorted(norm_to_mean.index))

    # Create the Excel Workbook
    writer = pd.ExcelWriter(xls_dir+"/"+'data.xlsx', engine='xlsxwriter')

    # Write the data to the Excel Workbook
    dev_data.to_excel(writer, sheet_name='Raw_Device_Data')
    norm_to_ctrl.to_excel(writer, sheet_name='Ratio_to_Control')
    norm_to_mean.to_excel(writer, sheet_name='Ratio_to_Control_2')

def write_excel_plots(plot_key, norm_to_ctrl):
    """plot data in excel"""

    # Define excel directory
    xls_dir = "./excel"

    # Change directory to EXPROOTPATH
    os.chdir(EXPROOTPATH)

    # Check to see if excel directory exists and if it doesn't make it
    try:
        os.makedirs(xls_dir)
    except OSError:
        if not os.path.isdir(xls_dir):
            raise

    # Set color palette
    #colors = ['#A8C16C', '#CA625C', '#5D93C5', '#9078AE', '#58B8CE']

    # Create the Excel Workbook
    writer = pd.ExcelWriter(xls_dir+"/"+'plots.xlsx', engine='xlsxwriter')

    for each in plot_key:

        df = norm_to_ctrl.loc[each].unstack().stack(0)
        df1 = df.xs('mean', level=1)
        df2 = df.xs('stdev', level=1)
        df = pd.concat([df1, df2],keys=['mean','stdev'])
        df = df.reindex(columns=natsorted(df.columns))

        df.to_excel(writer, sheet_name=each+'_Data')

        # Access the Workbook Object
        workbook = writer.book

        # Create a Chart Sheet
        chartsheet = workbook.add_chartsheet(each+' Line')

        i = 0
        n_intervals = len(df.columns)
        n_dev = len(df.reorder_levels([1,0]).sort().index.levels[0])
        dev_names = list(df.reorder_levels([1,0]).sort().index.levels[0])

        # Create a Chart
        chart = workbook.add_chart({'type': 'line'})


        for eachDevName in dev_names:

            # This mess is building a string to put into the plus / minus
            # values for the y error bars.  It won't take row line/numbers
            # like the other keys.  It requires excel syntax.
            err_bar_sheet = '\''+each+'_Data\'!'
            err_bar_start = xl_rowcol_to_cell(2+n_dev+i, 2, row_abs=True, col_abs=True)
            err_bar_end = xl_rowcol_to_cell(2+n_dev+i, 2+n_intervals, row_abs=True, col_abs=True)
            err_bar_ref = '='+err_bar_sheet+err_bar_start+':'+err_bar_end

            chart.add_series({
                'categories' : [each+'_Data', 0, 2, 0, 2+(n_intervals-1)],
                'values' : [each+'_Data', 2+i, 2, 2+i, 2+(n_intervals-1)],
                'name' : [each+'_Data', 2+i, 1],
                'marker': {'type': 'circle', 'size': 4},
                'line':   {'width': 2.0},
                'y_error_bars': {
                    'type': 'custom',
                    'plus_values': err_bar_ref,
                    'minus_values': err_bar_ref}
            })

            i += 1

        chart.set_x_axis({'text_axis': True})
        chart.set_y_axis({'name': each+' Relative to Control', 'min': 0})
        chart.set_legend({'position': 'bottom'})
        chart.set_title({'name': each+' Relative to Control'})

        # Place the Chart on the Chart Sheet
        chartsheet.set_chart(chart)

    # Write the Data to Disk
    writer.save()


def main():
    """ Get and parse command line inputs EXPROOTPATH is the root
    directory where all your data is The path to the directory it's
    suggested it not have spaces in it.  For example the folder
    'SomeExperiment' is ok, but 'Some Experiment' in not preferred.
    This directory should contain folder with the device names.  For
    example: SomeExperiment should contain Device1, Device2, etc.
    Each Device Folder should contain the .xls files with output
    from angioTool.  The .xls files should be named based on the
    interval (e.g. 0hr.xls, 24hr.xls, etc.)"""

    global EXPROOTPATH

    results = get_args()
    EXPROOTPATH = results.EXPROOTPATH

    # Read the data in from excel
    [dev_data, n_wells] = read_angiotool_files()

    # Remove non-numbers
    dev_data = rm_nan(dev_data)

    #
    # Calculations and Stats
    #

    # Normalize Values to 0hr
    norm_to_ctrl = norm_to_0hr(dev_data)
    # Normalize Values to Mean of Wells
    norm_to_mean = norm_to_avg(dev_data)
    # Cacluate Stats on 0hr Normalized Values
    norm_to_ctrl_stats = calc_stats(norm_to_ctrl, n_wells)
    # Caculate Stats on Mean Normalized Vales
    norm_to_mean_stats = calc_stats(norm_to_mean, n_wells)
    # Perform a t-Test on Mean Normalized Values
    norm_to_ctrl_pval = t_test(norm_to_mean)

    #
    # Concatenate for writing to excel
    #
    norm_to_ctrl = pd.concat([norm_to_ctrl, norm_to_ctrl_stats], axis=1)
    norm_to_mean = pd.concat([norm_to_mean, norm_to_mean_stats, norm_to_ctrl_pval], axis=1)

    #
    # Write data out out excel sheet
    #
    write_excel_data(dev_data, norm_to_ctrl, norm_to_mean)
    # Write excel charts
    plot_keys = ['Total Vessels Length', 'Total Number of End Points', 'Total Number of Junctions']
    write_excel_plots(plot_keys, norm_to_ctrl)

if __name__ == "__main__":
    main()
