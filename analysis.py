import click
import os
from typing import Tuple, List, Dict, Any
import pandas as pd
from tqdm import tqdm
import matplotlib as plt
import numpy as np

from analysis.validity_days import plot_validity_days
from analysis.domains import plot_domain_count

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
@click.option('--validity-days', 'analysis', flag_value='validity-days', default=True)
@click.option('--domain-count', 'analysis', flag_value='domain-count', default=True)
def main(input_file: str, output_dir: str, analysis: str):
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

    if analysis == "validity-days":
        plot_validity_days(df, output_dir)
    elif analysis == "domain-count":
        plot_domain_count(df, output_dir)
    else:
        raise Exception(f"Unimplemented analysis method '{analysis}'")


if __name__ == '__main__':
    main()
