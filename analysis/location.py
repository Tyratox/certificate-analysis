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


def country_match(row):
    # de-duplicate
    subject_countries = [] if row['subject_COUNTRY_NAME'] is None else list(
        set(row['subject_COUNTRY_NAME']))

    issuer_countries = [] if row['issuer_COUNTRY_NAME'] is None else list(
        set(row['issuer_COUNTRY_NAME']))

    # if there is just one country each return true
    if len(subject_countries) == 1 and \
            len(issuer_countries) == 1 and \
            subject_countries[0] == issuer_countries[0]:
        return True

    # else return false
    # print(f"sub: {len(subject_countries)}, issuer: {len(issuer_countries)}")
    return False


def count_issuer_subject_country_matches(df: pd.DataFrame):

    # drop all rows where the country is empty
    count_all = len(df)

    count_countries_set = len(df)
    # print(df['subject_COUNTRY_NAME'])
    # print(df['issuer_COUNTRY_NAME'])
    # exit()

    df['country_match'] = df.apply(
        country_match,
        axis=1
    )

    print(
        f"{len(df[df['country_match'] == True])} / {count_countries_set}"
    )
