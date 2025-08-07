"""
This script is used to convert csv files to dat files.
"""

import pandas as pd
import argparse

def csv2dat(csv_file, dat_file):
    """
    This function is used to convert csv files to dat files.
    """
    df = pd.read_csv(csv_file)
    df.to_csv(dat_file, index=False, header=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert csv files to dat files")
    parser.add_argument("csv_file", type=str, help="The csv file to convert")
    parser.add_argument("dat_file", type=str, help="The dat file to save")
    args = parser.parse_args()
    csv2dat(args.csv_file, args.dat_file)
    print("Conversion complete!")
    