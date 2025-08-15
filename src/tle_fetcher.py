from datetime import datetime, timezone, timedelta
from pathlib import Path

import aiohttp
import aiofiles

from src import TEMP_FILES_DIR, tle_database
from src.database import TleDatabase


class TLEFetcherLimiter:
    """
        TLE page has timeout, we can download TLE files only few times per 2 hours
        Here we will check the database and search the latest TLE record
        if record's created_on is older than 2h we download the new TLE file
    """

    @staticmethod
    def is_tle_fetch_allowed(db: TleDatabase) -> bool:
        latest_tle_db_record = db.get_latest_tle_record()
        if latest_tle_db_record is None:
            return True

        latest_tle_record_created_on = latest_tle_db_record.created_on
        datetime_now = datetime.now(timezone.utc)
        diff = abs(datetime_now - latest_tle_record_created_on)
        return diff > timedelta(hours=2)

class TLEFetcher:
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

    @classmethod
    async def get_latest_tle_data(cls, tle_url: str):
        if not TLEFetcherLimiter.is_tle_fetch_allowed(db=tle_database):
            return "You have the latest TLE record"

        async with aiohttp.ClientSession() as session:
            tle_text = await cls._fetch_tle_file_content(session, tle_url)

            # save in db
            lines = tle_text.strip().splitlines()
            for i in range(0, len(lines), 3):
                satellite_name = lines[i].strip()
                l1 = lines[i + 1].strip()
                l2 = lines[i + 2].strip()
                tle_database.insert_tle(satellite_name, l1, l2)

            local_tle_path = str(Path(TEMP_FILES_DIR, 'latest_tle.txt'))
            await cls._write_tle_file_locally(
                file_path=local_tle_path,
                tle_file_content=tle_text
            )

        return "Latest TLE record downloaded and saved in the db"