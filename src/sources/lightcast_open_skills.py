from __future__ import annotations

import io
import sys
from typing import Optional

import pandas as pd
import requests

from src.utils.storage import read_csv, write_csv, write_duckdb_table


# Public Lightcast Open Skills dataset (CSV). If this URL changes, update here.
OPEN_SKILLS_CSV = (
    "https://raw.githubusercontent.com/lightcast/open-skills/main/data/skills.csv"
)


def fetch_open_skills(url: str = OPEN_SKILLS_CSV) -> Optional[pd.DataFrame]:
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        # Some CSVs may be large; read via BytesIO
        data = io.BytesIO(r.content)
        df = pd.read_csv(data)
        return df
    except Exception as e:
        print(f"Failed to download Open Skills: {e}")
        return None


def normalize_skills(df: pd.DataFrame) -> pd.DataFrame:
    # Expect columns like: id, name, type, categories, description, ...
    # Keep a concise schema for PoC
    cols = {
        "id": "skill_id",
        "name": "name",
        "type": "category",
        "categories": "categories",
        "alt_names": "alt_labels",
        "description": "description",
    }
    for c in cols:
        if c not in df.columns:
            df[c] = None
    out = df[list(cols.keys())].rename(columns=cols)
    out["source"] = "lightcast_open_skills"
    return out


def main() -> int:
    df = fetch_open_skills()
    if df is None or df.empty:
        print("Open Skills: no data fetched.")
        return 1
    norm = normalize_skills(df)
    existing = read_csv("skills_taxonomy.csv")
    if existing is not None and not existing.empty:
        combined = pd.concat([existing, norm], ignore_index=True).drop_duplicates(
            subset=["skill_id"], keep="last"
        )
    else:
        combined = norm

    combined = combined.sort_values(["category", "name"]).reset_index(drop=True)
    write_csv(combined, "skills_taxonomy.csv")
    write_duckdb_table(combined, "skills_taxonomy")
    print(f"Open Skills: wrote {len(combined)} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

