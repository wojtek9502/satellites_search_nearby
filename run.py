import asyncio
import os

import dotenv

from src.satellite_search import SatelliteSearch

dotenv.load_dotenv(override=True)

async def main():
    satellite_search = SatelliteSearch(
        lat=float(os.environ['LATITUDE']),
        lon=float(os.environ['LONGITUDE']),
    )

    print("Calculating satellite passes...")
    passes_text = await satellite_search.calculate_satellites_nearby()
    print(passes_text)

if __name__ == "__main__":
    asyncio.run(main())
