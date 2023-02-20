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


def is_valid_input(input_path: str):

    if not os.path.isfile(input_path):
        return False

    if not input_path.endswith(".gz"):
        return False

    return True


@ click.command()
# positional arguments
# the input paths, can either be a directory or a single file
@ click.argument('inputs', type=click.Path(exists=True), nargs=-1)
@ click.argument('lookup_id', type=int)
def main(inputs: List[str], lookup_id: str):

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
    for input_file in input_files:
        print(f"Reading file '{input_file}'..")

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

        cert = df[df['id'] == lookup_id]

        if (len(cert) > 0):
            print(
                "-----BEGIN CERTIFICATE-----\n" +
                cert.iloc[0]['certificate_base64'] +
                "\n-----END CERTIFICATE-----"
            )
            print("-" * 50)
            chain = ([
                "-----BEGIN CERTIFICATE-----\n" +
                c +
                "\n-----END CERTIFICATE-----"
                for c in cert.iloc[0]['certificate_chain_base64'].split(";")
            ])
            for c in chain:
                print(c)

            exit()

    print(f"Could not find any entry with id {lookup_id}")


if __name__ == '__main__':
    main()
