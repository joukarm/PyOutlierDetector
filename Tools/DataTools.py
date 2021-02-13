"""
Includes modules for listing and reading data from csv files.
"""

import glob
import pandas as pd


def read_csv_file(file_name):
    return pd.read_csv(file_name)


def get_csv_files():
    return [f for f in glob.glob(r"data\*.csv")]
