from __future__ import annotations

import sys
from typing import Dict

import pandas as pd

from src.utils.storage import read_csv, write_csv, write_duckdb_table


BASELINE = pd.Timestamp("2019-12-01").date()


def pivot_series(df: pd.DataFrame) -> pd.DataFrame:
    # Expect long format: series_id, date, value
    wide = df.pivot_table(index="date", columns="series_id", values="value", aggfunc="last")
    wide = wide.sort_index()
    wide.index = pd.to_datetime(wide.index).date
    wide = wide.reset_index()
    wide.rename(columns={
        "index": "date",
    }, inplace=True)
    return wide


def normalize_index(series: pd.Series, baseline_date: pd.Timestamp | pd.Timestamp.date) -> pd.Series:
    if series is None or series.empty:
        return series
    # Find baseline value (closest on/after baseline)
    try:
        s = series.copy()
        base_val = s.loc[series.index.get_loc(baseline_date, method="nearest")] if hasattr(series.index, 'get_loc') else s.iloc[0]
    except Exception:
        base_val = series.dropna().iloc[0]
    if base_val == 0 or pd.isna(base_val):
        return series * 0.0
    return (series / base_val) * 100.0


def build_metrics(wide: pd.DataFrame) -> pd.DataFrame:
    # Map columns for readability
    colmap: Dict[str, str] = {
        "UNRATE": "unemp_rate",
        "JTSJOL": "job_openings",
        "JTSHIL": "hires",
        "JTSQUL": "quits",
        "CPIAUCSL": "cpi",
    }
    for src, dst in colmap.items():
        if src in wide.columns:
            wide[dst] = wide[src]

    # Build indices normalized to baseline
    df = wide[["date"] + [c for c in ["unemp_rate", "job_openings", "hires", "quits", "cpi"] if c in wide.columns]].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.sort_values("date")

    # CPI index
    if "cpi" in df.columns:
        df["cpi_index"] = normalize_index(df["cpi"], BASELINE)

    # Openings, hires, quits indices
    for col in ["job_openings", "hires", "quits"]:
        if col in df.columns:
            df[f"{col}_index"] = normalize_index(df[col], BASELINE)

    # Real openings index (deflate by CPI index)
    if "job_openings_index" in df.columns and "cpi_index" in df.columns:
        # Avoid division by zero
        df["real_openings_index"] = df["job_openings_index"] / (df["cpi_index"] / 100.0)

    # YoY changes for selected
    df = df.set_index(pd.to_datetime(df["date"]))
    for col in ["unemp_rate", "job_openings_index"]:
        if col in df.columns:
            df[f"yoy_{col}"] = df[col].pct_change(periods=12) * 100.0
    df = df.reset_index(drop=True)

    # Final column order
    cols = ["date", "unemp_rate", "job_openings_index", "hires_index", "quits_index", "cpi_index", "real_openings_index", "yoy_unemp_rate", "yoy_job_openings_index"]
    # Adapt to what exists
    cols = [c for c in cols if c in df.columns]
    return df[cols]


def main() -> int:
    long = read_csv("fred_series_values.csv")
    if long is None or long.empty:
        print("No FRED data available. Run sources first.")
        return 1
    wide = pivot_series(long)
    metrics = build_metrics(wide)
    write_csv(metrics, "market_metrics_daily.csv")
    write_duckdb_table(metrics, "market_metrics_daily")
    print(f"Metrics: wrote {len(metrics)} rows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

