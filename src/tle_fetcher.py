from datetime import datetime, timezone, timedelta
from pathlib import Path

import aiohttp
import aiofiles

from src import TEMP_FILES_DIR, TLE_DATABASE_PATH
from src.database import TleDatabase


class TLEFetcherLimiter:
    """
        The TLE pages have limits; we can download TLE files only a few times per 2 hours.
        Here we will check the database and search the latest TLE record
        If the record's created_on is older than 2h, we will download the new TLE file.
    """

    def __init__(self, db):
        self.tle_database = db

    def is_tle_fetch_allowed(self) -> bool:
        latest_tle_db_record = self.tle_database.get_latest_tle_record()
        if latest_tle_db_record is None:
            return True

        latest_tle_record_created_on = latest_tle_db_record.created_on
        datetime_now = datetime.now(timezone.utc)
        diff = abs(datetime_now - latest_tle_record_created_on)
        return diff > timedelta(hours=2)

class TLEFetcher:
    def __init__(self):
        self.tle_database = TleDatabase(db_path=str(TLE_DATABASE_PATH))

    @staticmethod
    async def _write_tle_file_locally(file_path: str, tle_file_content: str):
        async with aiofiles.open(file_path, "w") as out:
            await out.write(tle_file_content)
            await out.flush()

    @staticmethod
    async def _fetch_tle_file_content(session, url):
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def get_latest_tle_data(self, tle_url: str):
        if not TLEFetcherLimiter(self.tle_database).is_tle_fetch_allowed():
            return "You have the latest TLE record"

        async with aiohttp.ClientSession() as session:
            tle_text = await self._fetch_tle_file_content(session, tle_url)

            # save in db
            lines = tle_text.strip().splitlines()
            for i in range(0, len(lines), 3):
                satellite_name = lines[i].strip()
                l1 = lines[i + 1].strip()
                l2 = lines[i + 2].strip()
                self.tle_database.insert_tle(satellite_name, l1, l2)

            local_tle_path = str(Path(TEMP_FILES_DIR, 'latest_tle.txt'))
            await self._write_tle_file_locally(
                file_path=local_tle_path,
                tle_file_content=tle_text
            )

        return "Latest TLE record downloaded and saved in the db"