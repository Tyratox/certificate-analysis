import os
from typing import Tuple, List, Dict, Any
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from itertools import chain

# Create new `pandas` methods which use `tqdm` progress
# (can use tqdm_gui, optional kwargs, etc.)
# (https://stackoverflow.com/a/34365537/2897827)
tqdm.pandas()


def plot_domain_count(df: pd.DataFrame, output_dir: str):

    # duplicate rows for each subject common name and subject alternative name
    # print(df.columns)
    # count the number of common names + subject alternative names per certificate
    df['subject_COMMON_NAME_count'] = df['subject_COMMON_NAME'].apply(
        lambda x: len(x) if not x is None else 0
    )
    df['EXTENSION_SUBJECT_ALTERNATIVE_NAME_count'] = df['EXTENSION_SUBJECT_ALTERNATIVE_NAME'].apply(
        lambda x: len(x) if not x is None else 0
    )

    df['name_count'] = df['subject_COMMON_NAME_count'] + \
        df['EXTENSION_SUBJECT_ALTERNATIVE_NAME_count']

    # basic plot with the number of certificates per # of domains
    count_by_domains = df['name_count'].groupby(df['name_count']).size()

    # print largest name counts
    # print(
    #     df.sort_index(ascending=False).head(10)
    # )

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("# of certificates")
    ax.set_xlabel("# of domains (CN + SANs)")
    # ax.bar(count_by_days.index, count_by_days)
    ax.plot(count_by_domains.index, count_by_domains)
    plt.savefig(f"{output_dir}/domain-counts.png")

    # df.explode('subject_COMMON_NAME').explode('EXTENSION_SUBJECT_ALTERNATIVE_NAME')
    # print(df['EXTENSION_SUBJECT_ALTERNATIVE_NAME'].dropna())


def count_num_no_common(df: pd.DataFrame):
    print(df['subject_COMMON_NAME'].isna().sum())
