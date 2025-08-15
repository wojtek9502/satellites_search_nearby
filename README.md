## Satellite Passes Nearby

### Requirements
- Python 3.11+

### Details
This script allows you to calculate the passes of selected satellites and space objects based on the provided coordinates.  
Data is calculated for X consecutive days with a one-minute resolution.  

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
python app.py
