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


def plot_certificate_transparency_data(df: pd.DataFrame, output_dir: str):

    df['EXTENSION_PRECERT_POISON'] = df['EXTENSION_PRECERT_POISON'].fillna(
        False
    )

    poison_count = len(df[df['EXTENSION_PRECERT_POISON'] == True])
    nonpoison_count = len(df[df['EXTENSION_PRECERT_POISON'] == False])

    assert poison_count + nonpoison_count == len(df)

    print(
        f"Certificates with precert poison: {poison_count} / {len(df)}, {poison_count / len(df) * 100}%"
    )

    df['EXTENSION_PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS'] = df['EXTENSION_PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS']\
        .fillna(0)

    # sort the rows by the number of distribution points
    certificates_by_sct_count = df.groupby(
        by=['EXTENSION_PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS']
    ).agg(
        count=('EXTENSION_PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS', 'count')
    ).sort_values(
        by=['count'], ascending=False
    )

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("# of certificates")
    ax.set_xlabel("# SCTs")
    # force integer ticks
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # fig.autofmt_xdate(rotation=45)

    ax.bar(
        certificates_by_sct_count.index,
        certificates_by_sct_count.values.reshape(
            len(certificates_by_sct_count)
        ).astype(int)
    )
    plt.savefig(f"{output_dir}/scts.png")

    # check if the certificates with scts and without precert poison coincide
    # print(len(df[df['EXTENSION_PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS'] > 0]))
    # print(nonpoison_count)

    # print(
    #     len(
    #         df[
    #             (df['EXTENSION_PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS'] > 0) &
    #             (df['EXTENSION_PRECERT_POISON'] == False)
    #         ]
    #     )
    # )

    # get the ones where they don't

    # certificates that are poisoned should not contain scts!
    assert len(
        df[
            (df['EXTENSION_PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS'] > 0) &
            (df['EXTENSION_PRECERT_POISON'] == True)
        ]
    ) == 0

    # but ones without might not contain any scts?
    # print(
    #     df[
    #         (df['EXTENSION_PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS'] == 0) &
    #         (df['EXTENSION_PRECERT_POISON'] == False)
    #     ]['id']
    # )
