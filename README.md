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
# Set satellite name and your locations
# usage: run.py [-h] --lat LAT --lon LON [--satellite_name SATELLITE_NAME] [--range_days RANGE_DAYS] [--calc_resolution_min CALC_RESOLUTION_MIN] [--elevation_m ELEVATION_M] [--min_above_horizon_deg MIN_ABOVE_HORIZON_DEG] [--timezone TIMEZONE]

python run.py --satellite_name 'ISS (ZARYA)' --lat '50.06143' --lon '19.93658'
python run.py --satellite_name 'ISS (ZARYA)' --lat '50.06143' --lon '19.93658' --range_days 5 --timezone 'Europe/Warsaw' --calc_resolution_min 1
```

