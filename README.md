# Labor Market Pulse (PoC)

Lightweight, US-only proof of concept for near-real-time labor market signals and role framing using only free sources. Modular, extendable, and includes a Streamlit dashboard as the primary interface.

## Scope
- Signals (initial): Unemployment, job openings, hires, quits, CPI from FRED.
- Role framing: Lightcast Open Skills taxonomy (free).
- Outputs: CSVs and a DuckDB file; Streamlit dashboard required.
- Latency: Daily refresh; series update weekly/monthly.

## Why This PoC
- Fast: Single-command refresh on any laptop.
- Modular: Add sources/metrics without rewrites.
- Shareable: Streamlit dashboard + CSV/DuckDB outputs.
- Vendor-ready: Clean seams to plug in paid data later.

## Architecture Overview
- Sources: Modular fetchers under `src/sources/` (FRED, Lightcast Open Skills).
- Storage adapters: CSV baseline, optional DuckDB for joins/snapshots.
- Transforms: Derived indices and market metrics under `src/transforms/`.
- Dashboard: Streamlit app in `app/`.

## Streamlit Dashboard
- Pages:
  - Market Tightness: Openings index (2019-12=100) vs Unemployment rate.
  - Churn Pressure: Quits vs Hires indices.
  - Real Trend: CPI-deflated openings.
  - Skills: Role-family overviews using Lightcast Open Skills taxonomy.
- Controls: Date range, baseline month, smoothing (MA3), show YoY toggles.

## Repository Structure
```
src/
  sources/
    fred.py                 # fetch FRED series to CSV/DuckDB
    lightcast_open_skills.py# load skills taxonomy
  transforms/
    build_market_metrics.py # compute indices and derived metrics
  utils/
    storage.py              # CSV and DuckDB writers/readers
    config.py               # env/config management
app/
  streamlit_app.py          # Streamlit dashboard
data/
  csv/                      # CSV outputs
  labor.duckdb              # DuckDB file (optional)
.env.example                # FRED_API_KEY, USE_DUCKDB
requirements.txt
Makefile
```

## Setup
Prereqs: Python 3.10+, pip

Install:
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Configure:
```
cp .env.example .env
# Add your FRED API key (free from fred.stlouisfed.org)
```
Optionally set `USE_DUCKDB=true` to also maintain `data/labor.duckdb`.

## Usage
- Refresh data and metrics:
```
make refresh
```
Runs FRED pulls → skills load → metrics build → writes CSVs and DuckDB tables.

- Launch dashboard:
```
make app
# or
streamlit run app/streamlit_app.py
```

## Initial FRED Series
- UNRATE — Unemployment Rate
- JTSJOL — Job Openings: Total
- JTSHIL — Hires: Total
- JTSQUL — Quits: Total
- CPIAUCSL — CPI All Urban Consumers
- Optional: ECIWAG — Employment Cost Index, Wages

## Tables and Files
- `data/csv/fred_series_values.csv` — long: `series_id,date,value`.
- `data/csv/market_metrics_daily.csv` — `date, unemp_rate, openings_index, hires_index, quits_index, cpi_index, real_openings_index`.
- `data/csv/skills_taxonomy.csv` — `skill_id,name,category,alt_labels,...`.
- `data/labor.duckdb` — mirrors CSVs as tables when enabled.

## Extending
- Add a FRED series: update `SERIES` in `src/sources/fred.py`.
- Add metrics: implement in `src/transforms/build_market_metrics.py`.
- Add a source: create `src/sources/<source>.py` and register in `Makefile`.

## Attribution
- Cite FRED and Lightcast Open Skills in any published outputs. No PII.

## Roadmap
- Phase 0: FRED + skills, indices, Streamlit MVP (this PoC).
- Phase 1: Add geo granularity (LAUS/JOLTS region), WARN.
- Phase 2: Paid postings vendor; title/skill normalization; role-geo pay benchmarks.

