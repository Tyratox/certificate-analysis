import os
import pandas as pd
import numpy as np
import click
from typing import Tuple, List, Dict, Any
from tqdm import tqdm

# Create new `pandas` methods which use `tqdm` progress
# (can use tqdm_gui, optional kwargs, etc.)
# (https://stackoverflow.com/a/34365537/2897827)
tqdm.pandas()


def get_sibling_paths(input_path: str, suffixes: List[str]):

    basename = os.path.basename(input_path)\
        .removesuffix(".csv")\
        .removesuffix(".parquet")

    path = input_path.removesuffix(os.path.basename(input_path))

    return [f"{path}{basename}-{suffix}" for suffix in suffixes]


def is_valid_input(input_path: str):

    if not os.path.isfile(input_path):
        return False

    if not input_path.endswith(".csv") and not input_path.endswith(".parquet"):
        return False

    paths = get_sibling_paths(
        input_path,
        ["invalid.csv", "single-valued.csv"]
    )

    for p in paths:
        if not os.path.isfile(p):
            return False

    return True

# check which columns only consist of one single value
# (https://stackoverflow.com/a/54405767/2897827)


def single_value_cols(df):

    return [
        # for lists we cannot perform a comparison!
        False if (isinstance(df[c].iloc[0], np.ndarray) or isinstance(df[c].iloc[0], list)) else
        # for non lists, check if all elements match
        df[c].eq(df[c].iloc[0]).all()
        for c in df.columns
    ]


@ click.command()
# positional arguments
# the input paths, can either be a directory or a single file
@ click.argument('inputs', type=click.Path(exists=True), nargs=-1)
@ click.argument('output', type=click.Path(exists=False))
def main(inputs: List[str], output: str):

    # first validate the arguments
    input_files = []
    for input_path in inputs:
        # check if the input is a single file or a directory
        if os.path.isdir(input_path):
            # walk input directory and retrive the list of all valid input files
            for root, dirs, files in os.walk(input_path):
                input_files += [
                    # map each file to its full filename
                    f"{root}/{f}"
                    for f in files
                    # filter out invalid input files
                    if is_valid_input(f"{root}/{f}")
                ]

        elif is_valid_input(input_path):
            input_files += [input_path]

    if len(input_files) == 0:
        joined_paths = "', '".join(inputs)

        raise Exception(
            f"Did not find any valid input files given the paths '{joined_paths}'"
        )

    df = None

    # read all input files, parse them and extract all useful data
    for i, input_file in enumerate(input_files):
        print(f"Reading file '{input_file}'..")

        if input_file.endswith(".csv"):
            df_in = pd.read_csv(input_file)
        elif input_file.endswith(".parquet"):
            df_in = pd.read_parquet(input_file)
        else:
            raise Exception(f"Unkown input format for file {input_file}''")

        single_valued_path = get_sibling_paths(
            input_file,
            ["single-valued.csv"]
        )[0]

        df_single_valued = pd.read_csv(single_valued_path)
        for column in df_single_valued.columns:
            df_in[column] = df_single_valued.iloc[0][column]

        if i == 0:
            df = df_in
        else:
            df = pd.concat([df, df_in], ignore_index=True)

    # array of booleans indicating whether a column only contains a single value
    is_single_value_col = single_value_cols(df)
    # list of column names that are single-valued, will be populated in the loop below
    single_valued_columns: List[str] = []
    # create a dictionary mapping from column name to value for the columns that
    # only contain a single value. will be populated in the loop below
    single_valued: Dict[str, Any] = {}

    # get any row to retrieve that one value
    first_row = df.iloc[0]

    # fill 'single_valued_columns' and 'single_valued' by iterating over the
    # set of all column names and the is_single_value_col array
    for single_value, column_name in zip(is_single_value_col, df.columns):
        if single_value:
            single_valued_columns.append(column_name)
            single_valued[column_name] = first_row[column_name]

    # drop all single-valued columns
    df = df.drop(single_valued_columns, axis=1)

    # store df without single-valued columns
    if output.endswith(".parquet"):
        df.to_parquet(output, index=False)
    elif output.endswith(".csv"):
        df.to_csv(output, index=False)
    else:
        raise Exception(f"Unkown output format '{output}'")

    single_valued_path = get_sibling_paths(
        output,
        ["single-valued.csv"]
    )[0]

    pd.DataFrame([single_valued]).to_csv(single_valued_path, index=False)


if __name__ == '__main__':
    main()
