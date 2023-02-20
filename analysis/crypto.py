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


def plot_signature_algorithm(df: pd.DataFrame, output_dir: str):

    df['signature_algorithm'] = df['signature_algorithm']\
        .fillna("unknown")
    df['signature_hash_algorithm'] = df['signature_hash_algorithm']\
        .fillna("unknown")

    # group the rows by the signature algorithm and count the number of certificates in each group

    certificates_by_signature_algo = df.groupby(
        by=['signature_algorithm']
    ).agg(
        count=('signature_algorithm', 'count')
    ).sort_values(
        by=['count'], ascending=False
    )

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("# of certificates")
    ax.set_xlabel("signature hash algorithm")
    # fig.autofmt_xdate(rotation=90)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(4)

    ax.bar(
        certificates_by_signature_algo.index,
        certificates_by_signature_algo.values.reshape(
            len(certificates_by_signature_algo)
        )
    )

    plt.savefig(f"{output_dir}/signature-hash-algorithm.png")

    # group the rows by the signature algorithm and count the number of certificates in each group
    certificates_by_signature_hash_algo = df.groupby(
        by=['signature_hash_algorithm']
    ).agg(
        count=('signature_hash_algorithm', 'count')
    ).sort_values(
        by=['count'], ascending=False
    )

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("# of certificates")
    ax.set_xlabel("hash algorithm")
    # fig.autofmt_xdate(rotation=45)

    # for tick in ax.xaxis.get_major_ticks():
    # tick.label.set_fontsize(4)

    ax.bar(
        certificates_by_signature_hash_algo.index,
        certificates_by_signature_hash_algo.values.reshape(
            len(certificates_by_signature_hash_algo)
        )
    )
    plt.savefig(f"{output_dir}/hash-algorithm.png")
