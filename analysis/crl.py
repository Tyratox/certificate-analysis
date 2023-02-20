import os
from typing import Tuple, List, Dict, Any
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from itertools import chain

# Create new `pandas` methods which use `tqdm` progress
# (can use tqdm_gui, optional kwargs, etc.)
# (https://stackoverflow.com/a/34365537/2897827)
tqdm.pandas()


def plot_crl_distribution_points(df: pd.DataFrame, output_dir: str):

    df['EXTENSION_CRL_DISTRIBUTION_POINTS_COUNT'] = df['EXTENSION_CRL_DISTRIBUTION_POINTS_COUNT'].fillna(
        0)

    # sort the rows by the number of distribution points
    certificates_by_crl_distribution_count = df.groupby(
        by=['EXTENSION_CRL_DISTRIBUTION_POINTS_COUNT']
    ).agg(
        count=('EXTENSION_CRL_DISTRIBUTION_POINTS_COUNT', 'count')
    ).sort_values(
        by=['count'], ascending=False
    )

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("# of certificates")
    ax.set_xlabel("# crl distribution points")
    # force integer ticks
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # fig.autofmt_xdate(rotation=45)

    ax.bar(
        certificates_by_crl_distribution_count.index,
        certificates_by_crl_distribution_count.values.reshape(
            len(certificates_by_crl_distribution_count)
        ).astype(int)
    )
    plt.savefig(f"{output_dir}/distribution-points.png")
