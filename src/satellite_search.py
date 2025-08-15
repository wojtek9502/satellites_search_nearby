import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from skyfield import api
from skyfield.nutationlib import iau2000b
from skyfield.api import load, wgs84, EarthSatellite

from src import tle_database
from src.tle_fetcher import TLEFetcher

# ---- CONFIG ----
ts = load.timescale()
TLE_URL = os.environ["TLE_URL"]
SATELLITE_NAME = os.environ["SATELLITE_NAME"]
ELEVATION_M = 200

SEARCH_RANGE_DAYS = int(os.environ["SEARCH_RANGE_DAYS"])
if SEARCH_RANGE_DAYS > 31:
    print("Max SEARCH_RANGE_DAYS is 31 days. Set max value: 31 days")
    SEARCH_RANGE_DAYS = 31

ALT_DEGREES = -18
if os.environ['USE_CIVIL_TWILIGHT']:
    ALT_DEGREES = -6.0



class SatelliteSearch:
    def __init__(self, lat: float, lon: float, elev: int = 200):
        self.lat = lat
        self.lon = lon
        self.elev = elev

        self.planets_file = 'de421.bsp'
        self.planets = load(self.planets_file)
        self.sun = self.planets['sun']
        self.earth = self.planets['earth']

    def _is_civil_night(self, dt: datetime) -> bool:
        """
        Returns True if the given date and time correspond to civil night (Sun < -6°)
        dt: datetime with tzinfo or UTC
        lat, lon, elev: observer's coordinates
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        t = ts.from_datetime(dt)
        topos = api.Topos(latitude_degrees=self.lat, longitude_degrees=self.lon, elevation_m=self.elev)

        # calc position of the Sun
        t._nutation_angles = iau2000b(t.tt)
        alt_deg = (self.earth + topos).at(t).observe(self.sun).apparent().altaz()[0].degrees

        # civil night if alt_deg < -6°
        return alt_deg < ALT_DEGREES

    @staticmethod
    async def _get_satellite_tle_data(satellite_name: str):
        await TLEFetcher.get_latest_tle_data(tle_url=TLE_URL)
        tle_data = tle_database.get_latest_tle_record_for_satellite(satellite_name)
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
        satellites_passes_text = f"Passes of satellite {SATELLITE_NAME} over location ({self.lat}, {self.lon}) during the next {SEARCH_RANGE_DAYS} days"
        satellite = await self._get_satellite_object(satellite_name=SATELLITE_NAME)
        observer = wgs84.latlon(self.lat, self.lon, ELEVATION_M)

        dt_now = datetime.now(ZoneInfo(os.environ['TZ']))
        end_time = dt_now + timedelta(days=SEARCH_RANGE_DAYS)
        step = timedelta(minutes=1)

        single_passes_texts = []
        while dt_now <= end_time:
            tt = ts.utc(dt_now.year, dt_now.month, dt_now.day, dt_now.hour, dt_now.minute, dt_now.second)
            difference = satellite - observer
            topocentric = difference.at(tt)
            alt, az, distance = topocentric.altaz()

            # satellite above the horizon by 20 degrees and it is night
            if alt.degrees > 20 and self._is_civil_night(dt_now):
                single_pass_text = f"{dt_now} | altitude: {alt.degrees:.1f}°, azimuth: {az.degrees:.1f}°"
                single_passes_texts.append(single_pass_text)

            dt_now += step

        satellites_passes_text = satellites_passes_text + '\n' + '\n'.join(single_passes_texts)
        return satellites_passes_text