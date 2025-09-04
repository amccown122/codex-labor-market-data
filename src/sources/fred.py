from __future__ import annotations

import sys
from datetime import date
from typing import List

import pandas as pd
import requests

from src.utils.config import load_settings
from src.utils.storage import read_csv, write_csv, write_duckdb_table


FRED_API = "https://api.stlouisfed.org/fred/series/observations"

# Initial series set
SERIES: List[str] = [
    "UNRATE",   # Unemployment Rate
    "JTSJOL",  # Job Openings: Total
    "JTSHIL",  # Hires: Total
    "JTSQUL",  # Quits: Total
    "CPIAUCSL",# CPI All Urban Consumers
    # "ECIWAG", # Employment Cost Index, Wages (optional)
]


def fetch_series(series_id: str, api_key: str | None) -> pd.DataFrame:
    params = {
        "series_id": series_id,
        "file_type": "json",
    }
    if api_key:
        params["api_key"] = api_key

    resp = requests.get(FRED_API, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    obs = data.get("observations", [])
    df = pd.DataFrame(obs)
    if df.empty:
        return pd.DataFrame(columns=["series_id", "date", "value"])  # empty
    df = df[["date", "value"]]
    df["series_id"] = series_id
    # Cast types
    df["date"] = pd.to_datetime(df["date"]).dt.date
    # Some series have "." for missing
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])  # drop missing values
    return df[["series_id", "date", "value"]]


def main() -> int:
    settings = load_settings()
    frames = []
    for sid in SERIES:
        try:
            frames.append(fetch_series(sid, settings.fred_api_key))
        except Exception as e:
            print(f"Failed to fetch {sid}: {e}")
    if not frames:
        print("No data fetched from FRED.")
        return 1

    new_df = pd.concat(frames, ignore_index=True)

    # Merge with existing CSV to preserve history and deduplicate
    existing = read_csv("fred_series_values.csv")
    if existing is not None and not existing.empty:
        combined = pd.concat([existing, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=["series_id", "date"], keep="last")
    else:
        combined = new_df

    combined = combined.sort_values(["series_id", "date"]).reset_index(drop=True)
    write_csv(combined, "fred_series_values.csv")
    write_duckdb_table(combined, "fred_series_values")
    print(f"FRED: wrote {len(combined)} rows across {combined['series_id'].nunique()} series.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

