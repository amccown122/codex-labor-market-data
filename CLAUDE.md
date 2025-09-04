# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Data Refresh and Application
```bash
# Refresh all data sources (FRED, Lightcast) and rebuild metrics
make refresh

# Launch Streamlit dashboard
make app
# Alternative:
streamlit run app/streamlit_app.py
```

### Environment Setup
```bash
# Create virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure environment (required before running)
cp .env.example .env
# Add FRED_API_KEY from https://fred.stlouisfed.org
```

## Architecture

### Data Pipeline Flow
1. **Sources** (`src/sources/`) - Fetch external data and store in CSV/DuckDB
   - `fred.py`: Fetches FRED economic series (UNRATE, JTSJOL, JTSHIL, JTSQUL, CPIAUCSL)
   - `lightcast_open_skills.py`: Downloads skills taxonomy from GitHub

2. **Transforms** (`src/transforms/`) - Process raw data into market metrics
   - `build_market_metrics.py`: Creates indices normalized to baseline (Dec 2019), computes real values deflated by CPI

3. **Storage** (`src/utils/storage.py`) - Dual storage strategy
   - Primary: CSV files in `data/csv/`
   - Optional: DuckDB file at `data/labor.duckdb` (controlled by `USE_DUCKDB` env var)

4. **Dashboard** (`app/streamlit_app.py`) - Interactive visualization
   - Computes metrics dynamically based on user-selected baseline month
   - Provides multiple views: Market Tightness, Churn Pressure, Real Trend, Skills

### Key Design Patterns

**Incremental Data Updates**: Both FRED and skills sources merge new data with existing CSV files to preserve history while deduplicating on `(series_id, date)` or `skill_id`.

**Flexible Index Calculation**: The dashboard recomputes indices on-the-fly based on user-selected baseline dates, while `build_market_metrics.py` provides pre-computed defaults using Dec 2019 as baseline.

**Environment-Based Configuration**: All settings flow through `src/utils/config.py` which reads from `.env` file, with sensible defaults for missing values.

## Data Schema

### fred_series_values.csv
Long format: `series_id, date, value`
- Contains all FRED time series data in unified format

### market_metrics_daily.csv  
Wide format with computed metrics:
- `date, unemp_rate, job_openings_index, hires_index, quits_index, cpi_index, real_openings_index`
- Indices normalized to baseline month (default Dec 2019)

### skills_taxonomy.csv
`skill_id, name, category, categories, alt_labels, description, source`
- Unified skills taxonomy from Lightcast Open Skills

## Adding New Features

### Add FRED Series
Update `SERIES` list in `src/sources/fred.py`:
```python
SERIES = [
    "UNRATE",
    "JTSJOL", 
    # Add new series ID here
]
```

### Add New Metrics
Implement in `src/transforms/build_market_metrics.py`:
1. Add column mapping in `build_metrics()` function
2. Compute derived metric using existing data
3. Include in final column order

### Add New Data Source
1. Create `src/sources/<source_name>.py` with main() function
2. Follow pattern: fetch → normalize → merge with existing → write to CSV/DuckDB
3. Register in Makefile under `refresh` target

## GitHub Actions

Automated nightly refresh at `.github/workflows/refresh.yml`:
- Runs daily at 07:00 UTC
- Requires `FRED_API_KEY` secret in repository settings
- Uploads artifacts: `labor-market-csv` and `labor-market-duckdb`