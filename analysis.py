import click
import os
from typing import Tuple, List, Dict, Any
import pandas as pd
from tqdm import tqdm

# Create new `pandas` methods which use `tqdm` progress
# (can use tqdm_gui, optional kwargs, etc.)
# (https://stackoverflow.com/a/34365537/2897827)
tqdm.pandas()


@click.command()
# positional arguments
# the input path, either a csv file or a parquet file
@click.argument('input_file', type=click.Path(exists=True))
# output must be a folder
@click.argument('output_dir')
# flags / options
# @click.option('--csv', 'fmt', flag_value='csv', default=True)
def main(input_file: str, output_dir: str):
    if not os.path.isfile(input_file):
        raise Exception(f"Input path has to be a file")

    filename = os.path.basename(input_file)

    if filename.endswith(".csv"):
        df = pd.read_csv(input_file)
    elif filename.endswith(".parquet"):
        df = pd.read_parquet(input_file)
    else:
        raise Exception(
            f"Unsupported format, only .csv and .parquet files are currently supported"
        )

    if not os.path.isdir(output_dir):
        raise Exception(f"Output path must point to a directory")

    print(df)

    pass


if __name__ == '__main__':
    main()
