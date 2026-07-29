import pandas as pd

from analysis.metrics import METRICS


def make_dataframe(days):

    rows = []

    for day in days:

        row = {
            "date": day["calendarDate"]
        }

        for key, _ in METRICS:
            row[key] = day.get(key)

        rows.append(row)

    return pd.DataFrame(rows)