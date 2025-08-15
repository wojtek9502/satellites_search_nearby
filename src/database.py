import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from pydantic import BaseModel

class TleRecord(BaseModel):
    id: uuid.UUID
    satellite_name: str
    tle_line1: str
    tle_line2: str
    created_on: datetime


class TleDatabase:
    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_table_if_not_exists(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS TLE (
                    id TEXT PRIMARY KEY,
                    sat_name TEXT NOT NULL,
                    line1 TEXT NOT NULL,
                    line2 TEXT NOT NULL,
                    created_on TEXT NOT NULL
                )
            """)
            conn.commit()

    def insert_tle(self, sat_name, line1, line2) -> str:
        """Function to insert a TLE record into the database. Return tle id as str"""
        tle_id = str(uuid.uuid4())

        # Store timestamp in UTC
        created_on = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

        with self._connect() as conn:
            conn.execute("""
                INSERT INTO TLE (id, sat_name, line1, line2, created_on)
                VALUES (?, ?, ?, ?, ?)
            """, (tle_id, sat_name, line1, line2, created_on))
            conn.commit()
        return tle_id

    def _parse_row(self, row) -> TleRecord:
        id_, sat_name, line1, line2, created_on_utc = row
        return TleRecord(
            id=id_,
            satellite_name=sat_name,
            tle_line1=line1,
            tle_line2=line2,
            created_on=created_on_utc
        )

    def get_latest_tle_record_for_satellite(self, sat_name: str) -> Optional[Tuple]:
        """
        Function to get a TLE record by its satellite name
        returns TLERecord pydantic class or None if record does not exist:
        class TleRecord(BaseModel):
            id: uuid.UUID
            satellite_name: str
            tle_line1: str
            tle_line2: str
            created_on: datetime
        """
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT id, sat_name, line1, line2, created_on
                FROM TLE
                WHERE sat_name = ?
                ORDER BY created_on DESC
                LIMIT 1
            """, (sat_name,))
            row = cursor.fetchone()
            if row:
                return row
            return None

    def get_latest_tle_record(self) -> Optional[TleRecord]:
        """
            Return the latest TLE record regardless of satellite name
            returns TLERecord pydantic class or None if record does not exist:
            class TleRecord(BaseModel):
                id: uuid.UUID
                satellite_name: str
                tle_line1: str
                tle_line2: str
                created_on: datetime
        """
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT id, sat_name, line1, line2, created_on
                FROM TLE
                ORDER BY created_on DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return self._parse_row(row)
            return None

    def get_unique_satellite_names(self) -> List[str]:
        """Return a list of unique satellite names in the table"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT DISTINCT sat_name
                FROM TLE
            """)
            return [row[0] for row in cursor.fetchall()]