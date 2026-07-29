import json
from pathlib import Path
import pandas as pd
CACHE = Path("cache")


def load(time, email):

    file = CACHE / f"{time}_{email}.csv"

    if file.exists():

            return pd.read_csv(file)

    return False


def save(time, data, email):

    CACHE.mkdir(exist_ok=True)
    data.to_csv(f'{CACHE}/{time}_{email}.csv')