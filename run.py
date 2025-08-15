import asyncio
import argparse

import dotenv

from src.satellite_search import SatelliteSearch

dotenv.load_dotenv(override=True)

# Set your own URL if you need
TLE_URL = 'https://celestrak.org/NORAD/elements/stations.txt'


def parse_args():
    parser = argparse.ArgumentParser(description="Satellite pass prediction parameters")

    parser.add_argument(
        "--lat",
        type=str,
        required=True,
        help="Latitude of the observer (e.g., '50.0647N')"
    )
    parser.add_argument(
        "--lon",
        type=str,
        required=True,
        help="Longitude of the observer (e.g., '19.9450E')"
    )
    parser.add_argument(
        "--satellite_name",
        type=str,
        required=False,
        default="ISS (ZARYA)",
        help="Name of the satellite to track (default: ISS (ZARYA))"
    )
    parser.add_argument(
        "--range_days",
        type=int,
        default=10,
        help="Number of days to search for satellite passes (default: 10)"
    )
    parser.add_argument(
        "--elevation_m",
        type=int,
        default=200,
        help="Observer's elevation in meters (default: 200)"
    )
    parser.add_argument(
        "--min_above_horizon_deg",
        type=int,
        default=20,
        help="Minimum satellite altitude above horizon in degrees (default: 20)"
    )
    parser.add_argument(
        "--timezone",
        type=str,
        default="UTC",
        help="Timezone for the observer (default: UTC)"
    )

    return parser.parse_args()

async def main():
    args = parse_args()
    satellite_search = SatelliteSearch(
        tle_url=TLE_URL,
        satellite_name=args.satellite_name,
        lat=float(args.lat),
        lon=float(args.lon),
        calc_resolution_min=1,
        timezone_param=args.timezone,
        elev=int(args.elevation_m),
        min_above_horizon_deg=int(args.min_above_horizon_deg),
        range_days=int(args.range_days)
    )

    print("Calculating satellite passes...")
    passes_text = await satellite_search.calculate_satellites_nearby()
    print(passes_text)

if __name__ == "__main__":
    asyncio.run(main())
