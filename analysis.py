import os
import pandas as pd
import click
from typing import Tuple

# custom imports
from helpers import is_valid_input_file, map_certificate_row


@click.command()
# positional arguments
# the input path, can either be a directory or a single file
@click.argument('input', type=click.Path(exists=True))
@click.argument('output')
# flags / options
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name', help='The person to greet.')
def main(input: str, output: str):
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
            f"Did not find any valid input files given the path '{input}'")

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

        # for testing just use the first row
        df = df.head(100)
        df = df.apply(map_certificate_row, axis=1, result_type='expand')
        print(df)
        df.to_csv(output)
        break


if __name__ == '__main__':
    main()
