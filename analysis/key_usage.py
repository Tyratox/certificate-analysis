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


def count_key_usages(df: pd.DataFrame):

    columns = [
        col for col in df.columns
        if col.startswith("EXTENSION_KEY_USAGE") or col.startswith("EXTENSION_EXTENDED")
    ]

    counts: Dict[str, int] = {}

    for col in columns:
        df[col].fillna(False)
        counts[col] = len(df[df[col] == True])

    counts["TOTAL"] = len(df)

    print(counts)
