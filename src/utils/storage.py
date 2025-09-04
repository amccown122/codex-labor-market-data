from __future__ import annotations

import os
from typing import Optional

import pandas as pd

from .config import load_settings


def ensure_dirs() -> None:
    s = load_settings()
    os.makedirs(s.data_dir, exist_ok=True)
    os.makedirs(s.csv_dir, exist_ok=True)


def csv_path(filename: str) -> str:
    s = load_settings()
    ensure_dirs()
    return os.path.join(s.csv_dir, filename)


def write_csv(df: pd.DataFrame, filename: str) -> str:
    path = csv_path(filename)
    df.to_csv(path, index=False)
    return path


def read_csv(filename: str) -> Optional[pd.DataFrame]:
    path = csv_path(filename)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def duckdb_conn():
    s = load_settings()
    if not s.use_duckdb:
        return None
    try:
        import duckdb  # type: ignore
    except Exception:  # pragma: no cover - optional dependency at runtime
        return None
    ensure_dirs()
    return duckdb.connect(s.duckdb_path)


def write_duckdb_table(df: pd.DataFrame, table_name: str) -> None:
    con = duckdb_conn()
    if con is None:
        return
    # Replace table content with current DataFrame
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    con.close()

