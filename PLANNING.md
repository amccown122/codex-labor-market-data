# PLANNING: Labor Market Pulse PoC

Goal: Ship a small, dependable Streamlit dashboard with daily-refresh free signals and static skills framing.

## Milestones
- M0: Project skeleton, env, requirements, Makefile.
- M1: FRED ingestion (UNRATE, JTSJOL, JTSHIL, JTSQUL, CPIAUCSL).
- M2: Skills taxonomy load (Lightcast Open Skills).
- M3: Metrics transform (indices, YoY, CPI deflation).
- M4: Streamlit MVP (4 pages + controls).
- M5: Polish, docs, optional scheduler (GitHub Actions).

## Task Checklist
### Core
- [ ] Create repo structure and `requirements.txt`.
- [ ] `.env.example` with `FRED_API_KEY`, `USE_DUCKDB`.
- [ ] `src/utils/config.py` for env parsing.
- [ ] `src/utils/storage.py` for CSV + DuckDB I/O.

### Ingestion
- [ ] `src/sources/fred.py` generic fetcher with `SERIES` list.
- [ ] Dedup by `series_id,date`; write to CSV/DB.
- [ ] `src/sources/lightcast_open_skills.py` to load taxonomy.

### Transform
- [ ] `src/transforms/build_market_metrics.py`.
- [ ] Normalize to baseline (default 2019-12=100).
- [ ] Compute YoY and CPI-deflated indices.

### Streamlit
- [ ] `app/streamlit_app.py` with sidebar controls.
- [ ] Page: Market Tightness (Openings index vs UNRATE).
- [ ] Page: Churn Pressure (Quits vs Hires).
- [ ] Page: Real Trend (CPI-deflated openings).
- [ ] Page: Skills (taxonomy cards for role families).

### DX/Packaging
- [ ] `Makefile` (`refresh`, `app`).
- [ ] README polish with screenshots placeholders.
- [ ] Optional: GitHub Action cron to run `make refresh` and push CSV artifacts.

## Data Contracts
- `fred_series_values`: `series_id (str)`, `date (date)`, `value (float)`.
- `market_metrics_daily`: `date`, `unemp_rate`, `openings_index`, `hires_index`, `quits_index`, `cpi_index`, `real_openings_index`, `yoy_openings`, `yoy_unrate`.
- `skills_taxonomy`: `skill_id (str)`, `name (str)`, `category (str)`, `alt_labels (array|str)`, `source (str)`.

## Defaults and Controls
- Baseline month: 2019-12.
- Smoothing: optional 3-month moving average.
- Date range: default last 5 years.
- Storage: CSV required; DuckDB optional via `USE_DUCKDB`.

## Risks/Notes
- FRED: Monthly series; “daily refresh” means checking for new months.
- CPI deflation approximates “real” postings signal; can swap to PCE if needed.
- Skills taxonomy is static in PoC (no postings yet).

## Future Enhancements
- LAUS state/MSA unemployment; regional JOLTS.
- WARN layoff events.
- Vendor postings feed; title/skill normalization; pay ranges.

