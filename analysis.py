import click
import os
from typing import Tuple, List, Dict, Any
import pandas as pd
from tqdm import tqdm
import matplotlib as plt
import numpy as np

from analysis.validity_days import plot_validity_days
from analysis.domains import plot_domain_count, count_num_no_common
from analysis.basic_constraints import count_ca_enabled_certs
from analysis.key_usage import count_key_usages
from analysis.location import count_issuer_subject_country_matches

# Create new `pandas` methods which use `tqdm` progress
# (can use tqdm_gui, optional kwargs, etc.)
# (https://stackoverflow.com/a/34365537/2897827)
tqdm.pandas()


def ensure_dir_exists(path: str):
    if not os.path.exists(path):
        os.mkdir(path)

    elif not os.path.isdir(path):
        raise Exception(
            f"Expected '{path}' to either not exist or to be a directory"
        )


@click.command()
# positional arguments
# the input path, either a csv file or a parquet file
@click.argument('input_file', type=click.Path(exists=True))
# output must be a folder
@click.argument('output_dir')
# flags / options
@click.option('--validity-days', 'analysis', flag_value='validity-days', default=True)
@click.option('--domain-count', 'analysis', flag_value='domain-count')
@click.option('--no-common-name-count', 'analysis', flag_value='no-common-name')
@click.option('--ca-enabled-count', 'analysis', flag_value='ca-enabled-count')
@click.option('--key-usage-count', 'analysis', flag_value='key-usage-count')
@click.option('--issuer-subject-country-matches', 'analysis', flag_value='issuer-subject-country-matches')
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
        ensure_dir_exists(f"{output_dir}/validity/")
        plot_validity_days(df, f"{output_dir}/validity/")
    elif analysis == "domain-count":
        ensure_dir_exists(f"{output_dir}/domains/")
        plot_domain_count(df, f"{output_dir}/domains/")
    elif analysis == "no-common-name-count":
        count_num_no_common(df)
    elif analysis == "ca-enabled-count":
        count_ca_enabled_certs(df)
    elif analysis == "key-usage-count":
        count_key_usages(df)
    elif analysis == "issuer-subject-country-matches":
        count_issuer_subject_country_matches(df)
    else:
        raise Exception(f"Unimplemented analysis method '{analysis}'")


if __name__ == '__main__':
    main()
