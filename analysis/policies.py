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


def plot_ev_certificates(df: pd.DataFrame, output_dir: str):
    df['EXTENSION_CERTIFICATE_POLICIES_EV'] = df['EXTENSION_CERTIFICATE_POLICIES_EV'].fillna(
        False)
    ev_count = len(df[df['EXTENSION_CERTIFICATE_POLICIES_EV'] == True])
    dv_count = len(df[df['EXTENSION_CERTIFICATE_POLICIES_EV'] == False])

    assert ev_count + dv_count == len(df)

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("# of certificates")
    # ax.set_xlabel("# crl distribution points")
    # fig.autofmt_xdate(rotation=45)

    ax.bar(
        ["DV certificates", "EV certificates"],
        [dv_count, ev_count]
    )
    plt.savefig(f"{output_dir}/ev-dv.png")


def count_certificate_policies(df: pd.DataFrame):

    # ev_count = len(df[df['EXTENSION_CERTIFICATE_POLICIES_EV'] == True])
    # total_count = len(df)
    # print(
    #     f"{ev_count} / {total_count}, {ev_count/total_count * 100}%"
    # )

    # sort the rows by the number of policies
    print(
        df.sort_values(
            by=['EXTENSION_CERTIFICATE_POLICIES_COUNT'], ascending=False
        )
    )
