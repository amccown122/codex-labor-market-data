# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Data Refresh and Application
```bash
# Refresh all data sources (FRED, Lightcast) and rebuild metrics
make refresh

# Refresh individual components (modular approach)
make refresh-fred     # Just FRED data
make refresh-skills   # Just skills taxonomy (optional)
make refresh-metrics  # Just rebuild metrics

# Launch enhanced dashboard (recommended)
make app
# Alternative:
python3 -m streamlit run app/Home.py

# Launch classic single-page dashboard
make app-classic
# Alternative:
python3 -m streamlit run app/streamlit_app.py
```

### Environment Setup
```bash
# Create virtual environment and install dependencies
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements.txt

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

3. **Signals** (`src/signals/`) - Advanced market intelligence
   - `market_conditions.py`: Calculates Employer Power Index, Talent Velocity, headwind/tailwind classification

4. **Storage** (`src/utils/storage.py`) - Dual storage strategy
   - Primary: CSV files in `data/csv/`
   - Optional: DuckDB file at `data/labor.duckdb` (controlled by `USE_DUCKDB` env var)

5. **Dashboard** - Multi-page interactive visualization
   - **Enhanced Dashboard** (`app/Home.py`): Executive overview with market signals
     - Market Signals page: Headwind/tailwind analysis with strategic recommendations
     - Employer Power Index and Talent Velocity calculations
     - Real-time market condition classification
   - **Classic Dashboard** (`app/streamlit_app.py`): Traditional single-page view
     - Market Tightness, Churn Pressure, Real Trend analysis
     - User-selected baseline month calculations

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

## Troubleshooting

### Common Issues
1. **Streamlit date slider error**: Fixed by converting Pandas Timestamps to Python datetime objects in app/streamlit_app.py:99-104
2. **Lightcast skills URL 404**: This is optional - dashboard works without skills data. URL may need updating from https://github.com/lightcast/open-skills
3. **Python command not found**: Use `python3` instead of `python` on macOS/Linux

## Modular Design for Extensibility

### Adding New Data Sources
1. Create a new module in `src/sources/` following the pattern:
   - Fetch data from external API/source
   - Normalize to consistent schema
   - Merge with existing data (incremental updates)
   - Write to CSV and optionally DuckDB
   - Return 0 on success, handle errors gracefully

2. Add to Makefile with individual target:
```makefile
refresh-newsource:
	$(PY) -m src.sources.newsource
```

3. Update the main `refresh` target to include it

### Adding New Metrics
1. Edit `src/transforms/build_market_metrics.py`
2. Add column mappings in `build_metrics()` function
3. Compute derived metrics using normalized indices
4. Include in final column order

### Making Components Optional
- Return exit code 0 even on failure for optional components (see lightcast_open_skills.py:55)
- Use `-` prefix in Makefile to ignore errors: `-$(PY) -m src.sources.optional_source`
- Dashboard should handle missing data gracefully

## GitHub Actions

Automated nightly refresh at `.github/workflows/refresh.yml`:
- Runs daily at 07:00 UTC
- Requires `FRED_API_KEY` secret in repository settings
- Uploads artifacts: `labor-market-csv` and `labor-market-duckdb`
- Python version fixed at 3.11 for consistency