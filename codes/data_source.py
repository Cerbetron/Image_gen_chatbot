"""
In-memory CSV store.
Expected columns: Date, Score
"""

import pandas as pd, io
from functools import lru_cache
from datetime import date

__all__ = ["store_csv", "get_scores"]

@lru_cache(maxsize=1)
def _df():
    raise RuntimeError("CSV not loaded")

def store_csv(raw: bytes):
    df = pd.read_csv(io.BytesIO(raw))
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    _df.cache_clear()
    _df.__wrapped__ = lambda: df  # replace cached function

def get_scores(start: date, end: date) -> dict:
    df = _df()
    mask = (df["Date"] >= start) & (df["Date"] <= end)
    seg = df.loc[mask].sort_values("Date")
    labels = seg["Date"].dt.strftime("%a %-d")
    return dict(zip(labels, seg["Score"].astype(int)))
