from datetime import datetime, time, timezone

from skyfield.api import load
from skyfield.nutationlib import iau2000b
from skyfield.sgp4lib import EarthSatellite
from skyfield.toposlib import Topos
from skyfield import api


ts = load.timescale()


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

def next_pass_details(tle_line1, tle_line2, observer_location):
    ts = load.timescale()
    planets = load('de421.bsp')
    earth = planets['earth']
    sun = planets['sun']
    satellite = EarthSatellite(tle_line1, tle_line2)
    observer = Topos(latitude_degrees=observer_location[0], longitude_degrees=observer_location[1])

    start_time = ts.now()
    days = 10
    end_time = start_time + float(1.0 * days)  # Look 24 hours ahead

    culmination_time = None
    altitude_km = -1

    times, events = satellite.find_events(observer, start_time, end_time, altitude_degrees=10.0)
    passes = []
    for time, event in zip(times, events):
        if event == 1:  # Culmination
            culmination_time = time
            alt, az, _ = (satellite - observer).at(culmination_time).altaz()

            data = dict()
            data['dt'] = culmination_time.utc_datetime()
            data['lat'] = observer_location[0]
            data['lon'] = observer_location[1]
            data['elev'] = 200
            data['earth'] = earth
            data['sun'] = sun

            if is_passed_during_night(data):
                passes.append({
                    'culmination_time': culmination_time.utc_strftime('%Y-%m-%d %H:%M:%S'),
                    'altitude': f"{alt.degrees:.1f}°",
                    'azimuth': f"{az.degrees:.1f}°"
                })

    if len(passes):
        return passes
    return None

tle = [
    'ISS (ZARYA)',
    '1 25544U 98067A   25227.50399417  .00010432  00000+0  19089-3 0  9995',
    '2 25544  51.6349  13.0597 0003557 220.9474 139.1248 15.49942616524368'
]
observer_location = (51.6349, 13.0597)
passes = next_pass_details(tle[1], tle[2], observer_location)
print(passes)