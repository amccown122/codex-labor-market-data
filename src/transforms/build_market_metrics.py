from __future__ import annotations

import sys
from typing import Dict

import pandas as pd

from src.utils.storage import read_csv, write_csv, write_duckdb_table


BASELINE = pd.Timestamp("2019-12-01")


def pivot_series(df: pd.DataFrame) -> pd.DataFrame:
    # Expect long format: series_id, date, value
    wide = df.copy()
    wide["date"] = pd.to_datetime(wide["date"]).dt.to_period("M").dt.to_timestamp()
    wide = wide.pivot_table(index="date", columns="series_id", values="value", aggfunc="last").sort_index().reset_index()
    wide.rename(columns={
        "index": "date",
    }, inplace=True)
    return wide


def normalize_index(series: pd.Series, baseline_ts: pd.Timestamp) -> pd.Series:
    if series is None or series.empty:
        return series
    s = series.copy()
    if not isinstance(s.index, pd.DatetimeIndex):
        s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    # Prefer value at/before baseline; fallback to first after
    before = s.loc[s.index <= baseline_ts]
    if not before.empty:
        base_val = before.iloc[-1]
    else:
        after = s.loc[s.index >= baseline_ts]
        base_val = after.iloc[0] if not after.empty else s.dropna().iloc[0]
    if pd.isna(base_val) or base_val == 0:
        return s * 0.0
    return (s / base_val) * 100.0


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
    df["date"] = pd.to_datetime(df["date"])  # monthly-aligned
    df = df.sort_values("date")

    # CPI index
    if "cpi" in df.columns:
        s = df.set_index("date")["cpi"]
        df["cpi_index"] = normalize_index(s, BASELINE).reindex(df["date"]).values

    # Openings, hires, quits indices
    for col in ["job_openings", "hires", "quits"]:
        if col in df.columns:
            s = df.set_index("date")[col]
            df[f"{col}_index"] = normalize_index(s, BASELINE).reindex(df["date"]).values

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
