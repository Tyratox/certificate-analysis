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

SECONDS_PER_DAY = 60 * 60 * 24


def plot_validity_days(df: pd.DataFrame, output_dir: str):

    # round to full days
    df['validity_days'] = (df['validity_time'] / SECONDS_PER_DAY).round()

    # first a basic plot with the number of certificates per validity time in days
    count_by_days = df['validity_days']\
        .groupby(df['validity_days']).size()

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("# of certificates")
    ax.set_xlabel("validity time in days")
    # ax.bar(count_by_days.index, count_by_days)
    ax.plot(count_by_days.index, count_by_days)
    plt.savefig(f"{output_dir}/validity-days.png")

    # check how many different unique domains issue certificates for a given
    # validity time

    # fill NAs with empty arrays
    df['subject_COMMON_NAME'] = df['subject_COMMON_NAME']\
        .apply(lambda x: x if not x is None else [])

    common_names_per_day = df.groupby(['validity_days'])\
        .agg({'subject_COMMON_NAME': lambda x: list(chain.from_iterable(x))})

    # count total domains per validity_time
    common_names_per_day['subject_COMMON_NAME_total_count'] = common_names_per_day['subject_COMMON_NAME']\
        .apply(lambda x: len(x) if not x is None else 0)

    # prune duplicates
    common_names_per_day['subject_COMMON_NAME'] = common_names_per_day['subject_COMMON_NAME']\
        .apply(lambda x: list(set(x)) if not x is None else list())

    # count unique domains names per validity_time
    common_names_per_day['subject_COMMON_NAME_unique_count'] = common_names_per_day['subject_COMMON_NAME']\
        .apply(lambda x: len(x) if not x is None else 0)

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("# distinct subject COMMON_NAMEs")
    ax.set_xlabel("validity time in days")
    # ax.bar(count_by_days.index, count_by_days)
    ax.plot(
        count_by_days.index,
        common_names_per_day['subject_COMMON_NAME_unique_count']
    )
    plt.savefig(f"{output_dir}/validity-days-unique.png")

    # last but not least plot the number of certificates / unique domain names
    common_names_per_day['certs_per_unique_subject_COMMON_NAME'] = count_by_days / \
        common_names_per_day['subject_COMMON_NAME_unique_count']

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("log")
    ax.set_ylabel("average # of certificates per unique domain name")
    ax.set_xlabel("validity time in days")
    ax.plot(
        count_by_days.index,
        common_names_per_day['certs_per_unique_subject_COMMON_NAME']
    )
    plt.savefig(f"{output_dir}/validity-days-certs-per-unique.png")

    # print days with the most certificates
    # print(
    #     common_names_per_day[['subject_COMMON_NAME_total_count']].sort_values(
    #         by=['subject_COMMON_NAME_total_count'],
    #         ascending=False
    #     ).head(20)
    # )

    # sort by certs_per_unique_subject_COMMON_NAME in descending order
    # print(
    #     common_names_per_day.sort_values(
    #         by=['certs_per_unique_subject_COMMON_NAME'],
    #         ascending=False
    #     )
    # )

    # plot the average validity days per issuer
    days_by_issuer = df.explode('issuer_COMMON_NAME')\
        .groupby(['issuer_COMMON_NAME'])\
        .agg(avg_validity_days=('validity_days', np.mean), count=('validity_days', 'count'))\
        .sort_values(by=['count'], ascending=False)

    days_by_top_issuer = days_by_issuer.head(10).sort_values(
        by=['avg_validity_days'], ascending=True)

    fig, ax = plt.subplots(dpi=300)
    ax.set_yscale("linear")
    ax.set_ylabel("# of certificates")
    ax.set_xlabel("issuer common name sorted by average validity days")
    fig.autofmt_xdate(rotation=45)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(4)

    # exit()
    rects = ax.bar(
        days_by_top_issuer.index,
        days_by_top_issuer['count']
    )
    for rect, avg in zip(rects, days_by_top_issuer['avg_validity_days']):
        ax.annotate(
            '{}'.format(str(int(np.round(avg)))),
            xy=(rect.get_x() + rect.get_width() / 2, 5000),
            ha='center',
            fontsize=8,
            color='white'
        )

    plt.savefig(f"{output_dir}/validity-days-per-issuer.png")
