from datetime import timezone
from zoneinfo import ZoneInfo

from skyfield import api
from skyfield.nutationlib import iau2000b
from skyfield.api import load, EarthSatellite
from skyfield.toposlib import Topos
from tabulate import tabulate

from src import TleDatabase, TLE_DATABASE_PATH
from src.database import TleRecord
from src.tle_fetcher import TLEFetcher

# ---- CONFIG ----
ts = load.timescale()


class SatelliteSearch:
    def __init__(self, tle_url: str, satellite_name: str, lat: float, lon: float, elev: int = 200, timezone_param: str = "UTC", min_culmination_altitude_deg: float = 15.0, range_days: int = 20):
        self.tle_url = tle_url
        self.satellite_name = satellite_name
        self.lat = lat
        self.lon = lon
        self.elev = elev
        self.timezone = timezone_param
        self.min_culmination_altitude_deg = min_culmination_altitude_deg

        self.planets_file = 'de421.bsp'
        self.planets = load(self.planets_file)
        self.sun = self.planets['sun']
        self.earth = self.planets['earth']

        self.range_days = range_days
        if range_days > 31:
            print("Max SEARCH_RANGE_DAYS is 31 days. Set max value: 31 days")
            self.range_days = 31

    async def _get_satellite_tle_data(self):
        await TLEFetcher().get_latest_tle_data(tle_url=self.tle_url)
        tle_database = TleDatabase(db_path=str(TLE_DATABASE_PATH))
        db_tle_row = tle_database.get_latest_tle_record_for_satellite(self.satellite_name)

        id_, sat_name, line1, line2, created_on_utc = db_tle_row
        tle_data = TleRecord(
            id=id_,
            satellite_name = self.satellite_name,
            tle_line1 = line1,
            tle_line2 = line2,
            created_on = created_on_utc
        )

        return tle_data
    
    @staticmethod
    def is_passed_during_night(data) -> bool:
        """
        Returns True if the given date and time correspond to the night in the observer location
        """
        dt = data['dt']
        lat = data['lat']
        lon = data['lon']
        elev = data['elev']
        earth = data['earth']
        sun = data['sun']

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        t = ts.from_datetime(dt)
        topos = api.Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elev)

        # calc position of the Sun
        t._nutation_angles = iau2000b(t.tt)
        alt_deg = (earth + topos).at(t).observe(sun).apparent().altaz()[0].degrees

        # the night is when alt_deg < -6
        return alt_deg < -6

    def _to_local_time(self, t):
        dt = t.utc_datetime()
        if self.timezone != "UTC":
            dt = dt.astimezone(ZoneInfo(self.timezone))
        return dt.strftime("%Y-%m-%d %H:%M:%S %z")[:-2] + ":" + dt.strftime("%z")[-2:]

    def _alt_az_calc(self, satellite, observer, t):
        alt, az, _ = (satellite - observer).at(t).altaz()
        return alt.degrees, az.degrees

    def _find_passes(self, satellite, observer, start_time, end_time, earth, sun):
        times, events = satellite.find_events(
            observer, start_time, end_time,
            altitude_degrees=0
        )

        passes = []
        current_pass = {}
        night_check = None

        for t, event in zip(times, events):
            if event == 0:  # Start
                alt, az = self._alt_az_calc(satellite, observer, t)
                current_pass["start_time"] = self._to_local_time(t)
                current_pass["start_altitude"] = f"{alt:.1f}°"
                current_pass["start_azimuth"] = f"{az:.1f}°"

            elif event == 1:  # Culmination
                alt, az = self._alt_az_calc(satellite, observer, t)
                culm_time = self._to_local_time(t)

                current_pass.update({
                    "culmination_time": culm_time,
                    "culmination_altitude": f"{alt:.1f}°",
                    "culmination_altitude_float": float(alt),
                    "culmination_azimuth": f"{az:.1f}°"
                })

                night_check = dict(
                    dt=t.utc_datetime(),
                    lat=self.lat,
                    lon=self.lon,
                    elev=self.elev,
                    earth=earth,
                    sun=sun,
                )

            elif event == 2:  # End
                alt, az = self._alt_az_calc(satellite, observer, t)
                current_pass["end_time"] = self._to_local_time(t)
                current_pass["end_altitude"] = f"{alt:.1f}°"
                current_pass["end_azimuth"] = f"{az:.1f}°"

                if all(k in current_pass for k in ("start_time", "culmination_time", "end_time")):
                    if (self.is_passed_during_night(night_check) and current_pass["culmination_altitude_float"] >= self.min_culmination_altitude_deg):
                        passes.append({
                            "satellite_name": self.satellite_name,
                            "start_time": current_pass["start_time"],
                            "start_altitude": current_pass["start_altitude"],
                            "start_azimuth": current_pass["start_azimuth"],
                            "culmination_time": current_pass["culmination_time"],
                            "culmination_altitude": current_pass["culmination_altitude"],
                            "culmination_azimuth": current_pass["culmination_azimuth"],
                            "end_time": current_pass["end_time"],
                            "end_altitude": current_pass["end_altitude"],
                            "end_azimuth": current_pass["end_azimuth"],
                        })

                current_pass.clear()
                night_check = None

        return passes

    def next_pass_details(self, tle_line1: str, tle_line2: str):
        planets = load('de421.bsp')
        earth = planets['earth']
        sun = planets['sun']
        satellite = EarthSatellite(tle_line1, tle_line2)
        observer = Topos(latitude_degrees=self.lat, longitude_degrees=self.lon)

        start_time = ts.now()
        days = self.range_days
        end_time = start_time + float(1.0 * days)
        return self._find_passes(satellite, observer, start_time, end_time, earth, sun)
    

    
    async def calculate_satellites_nearby(self) -> str:
        satellites_passes_text = f"Passes of satellite '{self.satellite_name}' over location ({self.lat}, {self.lon}) during the next {self.range_days} days."
        tle_data = await self._get_satellite_tle_data()
        next_passes_details = self.next_pass_details(
            tle_line1=tle_data.tle_line1,
            tle_line2=tle_data.tle_line2
        )

        table_data = []
        table_header = ['Satellite', f'Start ({self.timezone})', 'Altitude', 'Azimuth', f'Culmination ({self.timezone})', 'Altitude', 'Azimuth', f'End ({self.timezone})', 'Altitude', 'Azimuth']
        for next_pass in next_passes_details:
            table_data.append(next_pass.values())

        passes_table_text =  str(tabulate(table_data, headers=table_header, tablefmt='github'))
        satellites_passes_text += '\n\n' + passes_table_text + '\n'
        return satellites_passes_text