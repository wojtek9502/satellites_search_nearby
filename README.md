## Satellite Passes Nearby

### Requirements
- Python 3.11+

### Details
This script allows you to calculate the passes of selected satellites and space objects based on the provided coordinates.  
  
Data is calculated for X consecutive days with a one-minute resolution. The script uses TLE files downloaded from the internet.  
  
To avoid a 403 error from the TLE page, the TLE file is stored in an SQLite database and updated only if the latest data in the database is older than 2 hours.  

Available objects  
- ISS (ZARYA)  
- CSS (TIANHE)  
- FREGAT DEB  
- CSS (WENTIAN)  
- CSS (MENGTIAN)  
- PROGRESS-MS 30  
- SOYUZ-MS 27  
- SHENZHOU-20 (SZ-20)  
- PROGRESS-MS 31  
- TIANZHOU-9  
- CREW DRAGON 11  

Enter one of these names in the .env file, along with the coordinates of your location.  

### Install
1. Install requirements
```shell
pip install -r requirements.txt
```

### Run
```shell
# usage: run.py [-h] --lat LAT --lon LON [--satellite_name SATELLITE_NAME] [--range_days RANGE_DAYS] [--elevation_m ELEVATION_M] [--min_culmination_altitude_deg MIN_CULMINATION_ALTITUDE_DEG] [--timezone TIMEZONE]
python run.py --satellite_name "ISS (ZARYA)" --lat "50.06143" --lon "19.93658"
python run.py --satellite_name "ISS (ZARYA)" --lat "50.06143" --lon "19.93658" --range_days 21 --timezone "Europe/Warsaw"
python run.py --satellite_name "ISS (ZARYA)" --lat "50.06143" --lon "19.93658" --range_days 21 --timezone "UTC" --min_culmination_altitude_deg 10.0
```

### Output
```shell
Load planets file...
Calculating the satellite passes...
You have the latest TLE record
Passes of satellite 'ISS (ZARYA)' over location (50.06143, 19.93658) during the next 31 days.

| Satellite   | Start (UTC)                | Altitude   | Azimuth   | Culmination (UTC)          | Altitude   | Azimuth   | End (UTC)                  | Altitude   | Azimuth   |
|-------------|----------------------------|------------|-----------|----------------------------|------------|-----------|----------------------------|------------|-----------|
| ISS (ZARYA) | 2026-04-21 02:38:54 +00:00 | 0.0°       | 219.6°    | 2026-04-21 02:44:06 +00:00 | 29.3°      | 146.4°    | 2026-04-21 02:49:21 +00:00 | -0.0°      | 73.5°     |
| ISS (ZARYA) | 2026-04-22 01:51:48 +00:00 | 0.0°       | 208.8°    | 2026-04-22 01:56:47 +00:00 | 20.5°      | 142.0°    | 2026-04-22 02:01:49 +00:00 | -0.0°      | 75.4°     |
| ISS (ZARYA) | 2026-04-23 02:40:22 +00:00 | 0.0°       | 239.0°    | 2026-04-23 02:45:47 +00:00 | 58.5°      | 155.8°    | 2026-04-23 02:51:14 +00:00 | -0.0°      | 72.7°     |
| ISS (ZARYA) | 2026-04-24 01:53:02 +00:00 | 0.0°       | 229.7°    | 2026-04-24 01:58:22 +00:00 | 41.8°      | 151.1°    | 2026-04-24 02:03:44 +00:00 | -0.0°      | 72.6°     |
| ISS (ZARYA) | 2026-04-25 01:05:46 +00:00 | 0.0°       | 219.7°    | 2026-04-25 01:10:58 +00:00 | 29.4°      | 146.5°    | 2026-04-25 01:16:12 +00:00 | -0.0°      | 73.5°     |
| ISS (ZARYA) | 2026-04-25 02:42:06 +00:00 | 0.0°       | 255.5°    | 2026-04-25 02:47:34 +00:00 | 84.4°      | 346.3°    | 2026-04-25 02:53:03 +00:00 | -0.0°      | 75.7°     |
| ISS (ZARYA) | 2026-04-26 00:18:37 +00:00 | 0.0°       | 208.9°    | 2026-04-26 00:23:36 +00:00 | 20.6°      | 142.0°    | 2026-04-26 00:28:37 +00:00 | -0.0°      | 75.4°     |
| ISS (ZARYA) | 2026-04-26 01:54:36 +00:00 | 0.0°       | 247.6°    | 2026-04-26 02:00:02 +00:00 | 78.1°      | 161.1°    | 2026-04-26 02:05:31 +00:00 | -0.0°      | 73.8°     |
| ISS (ZARYA) | 2026-04-27 01:07:08 +00:00 | 0.0°       | 239.1°    | 2026-04-27 01:12:32 +00:00 | 58.6°      | 156.0°    | 2026-04-27 01:17:59 +00:00 | -0.0°      | 72.8°     |
| ISS (ZARYA) | 2026-04-28 00:19:44 +00:00 | 0.0°       | 229.8°    | 2026-04-28 00:25:03 +00:00 | 41.8°      | 151.1°    | 2026-04-28 00:30:26 +00:00 | -0.0°      | 72.7°     |
| ISS (ZARYA) | 2026-04-28 01:56:20 +00:00 | 0.0°       | 262.6°    | 2026-04-28 02:01:47 +00:00 | 72.3°   
```