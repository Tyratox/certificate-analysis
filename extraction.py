import os
import pandas as pd
import click
from typing import Tuple, List, Dict, Any
from tqdm import tqdm

# custom imports
from extraction_helpers import is_valid_input_file, map_certificate_row

# Create new `pandas` methods which use `tqdm` progress
# (can use tqdm_gui, optional kwargs, etc.)
# (https://stackoverflow.com/a/34365537/2897827)
tqdm.pandas()


def derive_output(output: str, suffix: str, extension=".csv") -> str:
    "Derives a new output pathname by appending a suffix after the filename but before the extension"
    return output.removesuffix(
        os.path.basename(output)
    ) + \
        os.path.basename(output).removesuffix(extension) + \
        f"-{suffix}{extension}"


@click.command()
# positional arguments
# the input path, can either be a directory or a single file
@click.argument('input', type=click.Path(exists=True))
@click.argument('output')
# flags / options
@click.option('--csv', 'fmt', flag_value='csv', default=True)
@click.option('--parquet', 'fmt', flag_value='parquet')
# @click.option('--name', prompt='Your name', help='The person to greet.')
def main(input: str, output: str, fmt: str):
    if fmt == 'parquet':
        extension = '.parquet'
    else:
        extension = ".csv"

    # first validate the arguments
    input_files = []
    # check if the input is a single file or a directory
    if os.path.isdir(input):
        # walk input directory and retrive the list of all valid input files
        for root, dirs, files in os.walk(input):
            input_files += [
                # map each file to its full filename
                root + "/" + f
                for f in files
                # filter out invalid input files
                if is_valid_input_file(f)
            ]

    elif is_valid_input_file(input):
        input_files = [input]

    if len(input_files) == 0:
        raise Exception(
            f"Did not find any valid input files given the path '{input}'"
        )

    if not output.endswith(extension):
        raise Exception(
            f"Output path must end on '{extension}', '{output}' given"
        )

    # read all input files, parse them and extract all useful data
    for input_file in input_files:
        print(f"Reading compressed csv '{input_file}'")
        df = pd.read_csv(
            input_file,
            # inputs do not contain any headers
            header=None,
            # name columns manually
            names=[
                'log_url',
                'id',
                'hash',
                'certificate_base64',
                'certificate_chain_base64',
                'domains',
                'ts1',
                'ts2'
            ],
            # files are gzipped
            compression='gzip'
        )
        # reduce dataframe to required columns
        df = df[['certificate_base64', 'certificate_chain_base64']]
        # convert certificate chain to list column
        df['certificate_chain_base64'] = df['certificate_chain_base64'].apply(
            lambda chain: chain.split(";"))

        # store copy of original df with whole certificates
        cert_df = df

        # reduce dataset for testing purposes
        # df = df.head(100)

        # extract the certificate data and show a loading bar as it might take a minute
        df: pd.DataFrame = df.progress_apply(
            map_certificate_row,
            axis=1,
            result_type='expand'
        )

        # drop all columns where all entries are empty / None
        df = df.dropna(axis=1, how='all')

        # find all rows that are empty
        empty_row_indices = df.index[df.isna().all(axis=1)].tolist()
        invalid_certificates = cert_df.iloc[empty_row_indices]
        # drop all of the empty rows
        df = df.drop(index=empty_row_indices)

        # check which columns only consist of one single value
        # (https://stackoverflow.com/a/54405767/2897827)
        def single_value_cols(df):
            a = df.to_numpy()  # df.values (pandas<0.24)
            return (a[0] == a).all(0)

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

        # derive output paths for the single-valued entries and the invalid certificate
        # by appending a suffix to the filename
        single_valued_output = derive_output(
            output,
            "single-valued",
            ".csv"
        )
        invalid_output = derive_output(
            output,
            "invalid",
            ".csv"
        )

        # store all of the computed data on disk in the given format
        if fmt == "parquet":
            df.to_parquet(output, index=False)
        else:
            df.to_csv(output, index=False)

        # single valued output and invalid certificates are always stored as csv, they are usually small
        pd.DataFrame([single_valued]).to_csv(single_valued_output, index=False)
        invalid_certificates.to_csv(invalid_output, index=False)
        break


if __name__ == '__main__':
    main()
