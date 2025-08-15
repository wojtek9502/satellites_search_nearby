import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

import dotenv
from pydantic import BaseModel

dotenv.load_dotenv(override=True)


class TleRecord(BaseModel):
    id: uuid.UUID
    satellite_name: str
    tle_line1: str
    tle_line2: str
    created_on: datetime


class TleDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.local_tz = ZoneInfo(os.environ['TZ'])

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

    def _row_with_local_time(self, row) -> TleRecord:
        """
            Convert created_on from UTC to local timezone
            returns TLERecord pydantic class:
            class TleRecord(BaseModel):
                id: uuid.UUID
                satellite_name: str
                tle_line1: str
                tle_line2: str
                created_on: datetime
        """
        id_, sat_name, line1, line2, created_on_utc = row
        # Remove 'Z' and parse as UTC datetime
        dt_utc = datetime.fromisoformat(created_on_utc.replace("Z", "+00:00"))
        # Convert to local timezone
        dt_local = dt_utc.astimezone(self.local_tz)
        return TleRecord(
            id=id_,
            satellite_name=sat_name,
            tle_line1=line1,
            tle_line2=line2,
            created_on=dt_local
        )

    def get_tle_by_id(self, tle_id: str) -> Optional[TleRecord]:
        """
            Function to get a TLE record by its id
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
                WHERE id = ?
            """, (tle_id,))
            row = cursor.fetchone()
            if row:
                return self._row_with_local_time(row)
            return None

    def get_latest_tle_record_for_satellite(self, sat_name: str) -> Optional[TleRecord]:
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
                return self._row_with_local_time(row)
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
                return self._row_with_local_time(row)
            return None

    def get_unique_satellite_names(self) -> List[str]:
        """Return a list of unique satellite names in the table"""
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT DISTINCT sat_name
                FROM TLE
            """)
            return [row[0] for row in cursor.fetchall()]