from pathlib import Path

from src.database import TleDatabase

PROJECT_DIR = Path(__file__).parent.parent.resolve()
TEMP_FILES_DIR = Path(PROJECT_DIR, "temp_files")
TEMP_FILES_DIR.mkdir(exist_ok=True, parents=True)

TLE_DATABASE_PATH = Path(TEMP_FILES_DIR, "tle_data.sqlite")
tle_database = TleDatabase(str(TLE_DATABASE_PATH))
tle_database.create_table_if_not_exists()