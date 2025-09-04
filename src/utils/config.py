import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Settings:
    fred_api_key: str | None
    use_duckdb: bool
    data_dir: str
    csv_dir: str
    duckdb_path: str


def load_settings() -> Settings:
    # Load .env if present
    load_dotenv(override=False)

    fred_api_key = os.getenv("FRED_API_KEY")
    use_duckdb = os.getenv("USE_DUCKDB", "false").lower() in {"1", "true", "yes"}
    data_dir = os.getenv("DATA_DIR", "data")
    csv_dir = os.getenv("CSV_DIR", os.path.join(data_dir, "csv"))
    duckdb_path = os.getenv("DUCKDB_PATH", os.path.join(data_dir, "labor.duckdb"))

    return Settings(
        fred_api_key=fred_api_key,
        use_duckdb=use_duckdb,
        data_dir=data_dir,
        csv_dir=csv_dir,
        duckdb_path=duckdb_path,
    )

