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


def count_ca_enabled_certs(df: pd.DataFrame):

    print(
        len(df[df['EXTENSION_BASIC_CONSTRAINTS_CA'] == True])
    )

    # print(df[df['id'].isna()]["id"])

    # there are some certificartes without the basic_constraints extension
    # but this is fine as this results in the flag being set to false
    # https://www.rfc-editor.org/rfc/rfc5280#section-4.2.1.9
    # print(df[df['EXTENSION_BASIC_CONSTRAINTS_CA'].isna()]["id"])
    print(len(df[df['EXTENSION_BASIC_CONSTRAINTS_CA'].isna()]))
