"""
In-memory CSV store.
Expected columns: Date, Score
"""

import pandas as pd
import io
from functools import lru_cache
from datetime import date
import pathlib
from .config import CACHE_FILE, CACHE_DIR

__all__ = ["store_csv", "get_scores", "get_last_date", "load_cached"]

@lru_cache(maxsize=1)
def _df():
    raise RuntimeError("CSV not loaded")

def load_cached() -> bool:
    """Load last uploaded CSV from disk if available."""
    if CACHE_FILE.exists():
        store_csv(CACHE_FILE.read_bytes())
        return True
    return False

def store_csv(raw: bytes):
    CACHE_DIR.mkdir(exist_ok=True, parents=True)
    pathlib.Path(CACHE_FILE).write_bytes(raw)

    df = pd.read_csv(io.BytesIO(raw))
    raw_dates = df["Date"].astype(str).str.strip()
    if raw_dates.apply(str.isdigit).all():
        today = date.today()
        df["Date"] = raw_dates.astype(int).apply(lambda d: date(today.year, today.month, d))
    else:
        df["Date"] = pd.to_datetime(raw_dates).dt.date
    _df.cache_clear()
    _df.__wrapped__ = lambda: df  # replace cached function

def get_last_date() -> date:
    """Return the last date present in the loaded CSV or today's date."""
    try:
        df = _df()
    except RuntimeError:
        return date.today()
    return df["Date"].max()

def get_scores(start: date, end: date) -> dict:
    try:
        df = _df()
    except RuntimeError:
        return {}
    mask = (df["Date"] >= start) & (df["Date"] <= end)
    seg = df.loc[mask].sort_values("Date")
    labels = seg["Date"].apply(lambda d: d.strftime("%a %-d"))
    return dict(zip(labels, seg["Score"].astype(int)))
