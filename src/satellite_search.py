from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from skyfield import api
from skyfield.nutationlib import iau2000b
from skyfield.api import load, wgs84, EarthSatellite

from src import TleDatabase, TLE_DATABASE_PATH
from src.database import TleRecord
from src.tle_fetcher import TLEFetcher

# ---- CONFIG ----
ts = load.timescale()


class SatelliteSearch:
    def __init__(self, tle_url: str, satellite_name: str, lat: float, lon: float, elev: int = 200, timezone_param: str = "UTC", min_above_horizon_deg: int = 20, range_days: int = 20, calc_resolution_min: int = 10):
        self.tle_url = tle_url
        self.satellite_name = satellite_name
        self.lat = lat
        self.lon = lon
        self.elev = elev
        self.timezone = timezone_param
        self.min_above_horizon_deg = min_above_horizon_deg
        self.calc_resolution_min = calc_resolution_min

        self.planets_file = 'de421.bsp'
        self.planets = load(self.planets_file)
        self.sun = self.planets['sun']
        self.earth = self.planets['earth']

        self.range_days = range_days
        if range_days > 31:
            print("Max SEARCH_RANGE_DAYS is 31 days. Set max value: 31 days")
            self.range_days = 31


    def _is_passed_during_night(self, dt: datetime) -> bool:
        """
        Returns True if the given date and time correspond to the night in the observer location
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        t = ts.from_datetime(dt)
        topos = api.Topos(latitude_degrees=self.lat, longitude_degrees=self.lon, elevation_m=self.elev)

        # calc position of the Sun
        t._nutation_angles = iau2000b(t.tt)
        alt_deg = (self.earth + topos).at(t).observe(self.sun).apparent().altaz()[0].degrees

        # the night is when alt_deg < -12
        return alt_deg < -12


    async def _get_satellite_tle_data(self, satellite_name: str):
        await TLEFetcher().get_latest_tle_data(tle_url=self.tle_url)
        tle_database = TleDatabase(db_path=str(TLE_DATABASE_PATH))
        db_tle_row = tle_database.get_latest_tle_record_for_satellite(satellite_name)

        id_, sat_name, line1, line2, created_on_utc = db_tle_row
        tle_data = TleRecord(
            id=id_,
            satellite_name = sat_name,
            tle_line1 = line1,
            tle_line2 = line2,
            created_on = created_on_utc
        )

        if self.timezone != "UTC":
            dt_utc = datetime.fromisoformat(created_on_utc.replace("Z", "+00:00"))
            # Convert to local timezone
            timezone_str = self.timezone
            dt_local = dt_utc.astimezone(ZoneInfo(timezone_str))
            tle_data = TleRecord(
                id=id_,
                satellite_name=sat_name,
                tle_line1=line1,
                tle_line2=line2,
                created_on=dt_local
            )

        return tle_data

    async def _get_satellite_object(self, satellite_name: str) -> EarthSatellite:
        tle_data = await self._get_satellite_tle_data(satellite_name)
        if not tle_data:
            raise ValueError(f"Not found satellite '{satellite_name}' in DB")

        l1 = tle_data.tle_line1
        l2 = tle_data.tle_line2
        name = tle_data.satellite_name
        return EarthSatellite(l1, l2, name, ts)

    async def calculate_satellites_nearby(self) -> str:
        satellites_passes_text = f"Passes of satellite '{self.satellite_name}' over location ({self.lat}, {self.lon}) during the next {self.range_days} days. With calculation every {self.calc_resolution_min} minutes."
        satellite = await self._get_satellite_object(satellite_name=self.satellite_name)
        observer = wgs84.latlon(self.lat, self.lon, self.elev)

        dt_now = datetime.now(ZoneInfo(self.timezone))
        end_time = dt_now + timedelta(days=self.range_days)
        step = timedelta(minutes=self.calc_resolution_min)

        single_passes_texts = []
        while dt_now <= end_time:
            tt = ts.utc(dt_now.year, dt_now.month, dt_now.day, dt_now.hour, dt_now.minute, dt_now.second)
            difference = satellite - observer
            topocentric = difference.at(tt)
            alt, az, distance = topocentric.altaz()

            # satellite above the horizon by 20 degrees and it is night
            if alt.degrees > self.min_above_horizon_deg and self._is_passed_during_night(dt_now):
                single_pass_text = f"{dt_now} | altitude: {alt.degrees:.1f}°, azimuth: {az.degrees:.1f}°"
                single_passes_texts.append(single_pass_text)

            dt_now += step

        satellites_passes_text = satellites_passes_text + '\n' + '\n'.join(single_passes_texts)
        return satellites_passes_text