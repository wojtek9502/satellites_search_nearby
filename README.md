## Satellite Passes Nearby

### Requirements
- Python 3.11+

### Details
Details
This script allows you to calculate the passes of selected satellites and space objects based on the provided coordinates.  
  
Data is calculated for X consecutive days with a one-minute resolution. The script uses TLE files downloaded from the internet.  
  
To avoid overloading the TLE server, TLE data is stored in an SQLite database and updated only if the latest data in the database is older than 2 hours.  

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
2. Check and update .env file if necessary

### Run
```shell
# usage: run.py [-h] --lat LAT --lon LON [--satellite_name SATELLITE_NAME] [--range_days RANGE_DAYS] [--elevation_m ELEVATION_M] [--min_culmination_altitude_deg MIN_CULMINATION_ALTITUDE_DEG] [--timezone TIMEZONE]
python run.py --satellite_name 'ISS (ZARYA)' --lat '50.06143' --lon '19.93658'
python run.py --satellite_name 'ISS (ZARYA)' --lat '50.06143' --lon '19.93658' --range_days 5 --timezone 'Europe/Warsaw'
python run.py --satellite_name 'ISS (ZARYA)' --lat '50.06143' --lon '19.93658' --range_days 5 --timezone 'UTC' --min_culmination_altitude_deg 10.0
```

### Output
```shell
Calculating the satellite passes...
Passes of satellite 'ISS (ZARYA)' over location (50.06143, 19.93658) during the next 10 days.

| Satellite   | Start (Europe/Warsaw)      | Altitude   | Azimuth   | Culmination (Europe/Warsaw)   | Altitude   | Azimuth   | End (Europe/Warsaw)        | Altitude   | Azimuth   |
|-------------|----------------------------|------------|-----------|-------------------------------|------------|-----------|----------------------------|------------|-----------|
| ISS (ZARYA) | 2025-08-19 04:55:23 +02:00 | 0.0°       | 201.3°    | 2025-08-19 05:00:10 +02:00    | 16.1°      | 139.2°    | 2025-08-19 05:04:59 +02:00 | -0.0°      | 77.3°     |
| ISS (ZARYA) | 2025-08-20 04:07:39 +02:00 | 0.0°       | 188.2°    | 2025-08-20 04:11:59 +02:00    | 10.5°      | 134.7°    | 2025-08-20 04:16:20 +02:00 | -0.0°      | 81.6°     |
| ISS (ZARYA) | 2025-08-21 04:54:29 +02:00 | 0.0°       | 222.6°    | 2025-08-21 04:59:44 +02:00    | 32.4°      | 147.7°    | 2025-08-21 05:05:00 +02:00 | -0.0°      | 73.2°     |
| ISS (ZARYA) | 2025-08-22 04:06:22 +02:00 | 0.0°       | 211.6°    | 2025-08-22 04:11:25 +02:00    | 22.4°      | 143.1°    | 2025-08-22 04:16:29 +02:00 | -0.0°      | 74.8°     |
| ISS (ZARYA) | 2025-08-23 03:18:23 +02:00 | 0.0°       | 199.5°    | 2025-08-23 03:23:07 +02:00    | 15.2°      | 138.6°    | 2025-08-23 03:27:52 +02:00 | -0.0°      | 77.8°     |
| ISS (ZARYA) | 2025-08-23 04:53:56 +02:00 | 0.0°       | 240.8°    | 2025-08-23 04:59:22 +02:00    | 62.4°      | 156.8°    | 2025-08-23 05:04:49 +02:00 | -0.0°      | 72.9°     |
| ISS (ZARYA) | 2025-08-24 04:05:33 +02:00 | 0.0°       | 231.3°    | 2025-08-24 04:10:55 +02:00    | 44.2°      | 151.8°    | 2025-08-24 04:16:17 +02:00 | -0.0°      | 72.6°     |
| ISS (ZARYA) | 2025-08-25 03:17:15 +02:00 | 0.0°       | 221.0°    | 2025-08-25 03:22:29 +02:00    | 30.7°      | 147.0°    | 2025-08-25 03:27:44 +02:00 | -0.0°      | 73.4°     |
| ISS (ZARYA) | 2025-08-25 04:53:34 +02:00 | 0.0°       | 256.4°    | 2025-08-25 04:59:01 +02:00    | 82.6°      | 345.9°    | 2025-08-25 05:04:30 +02:00 | -0.0°      | 76.0°     |
| ISS (ZARYA) | 2025-08-26 02:29:04 +02:00 | 0.0°       | 209.8°    | 2025-08-26 02:34:05 +02:00    | 21.2°      | 142.4°    | 2025-08-26 02:39:06 +02:00 | -0.0°      | 75.2°     |
| ISS (ZARYA) | 2025-08-26 04:05:01 +02:00 | 0.0°       | 248.3°    | 2025-08-26 04:10:28 +02:00    | 79.6°      | 161.1°    | 2025-08-26 04:15:56 +02:00 | -0.0°      | 73.9°     |
```