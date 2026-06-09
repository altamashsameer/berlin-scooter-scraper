import os
from datetime import datetime
import time
import pandas as pd
import requests

URL = "https://nextbike.net"
CSV_FILE = "berlin_scooters_raw_data.csv"


def scrape_snapshot():
    try:
        response = requests.get(URL, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

    scooter_list = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for country in data.get("countries", []):
        for city in country.get("cities", []):
            for place in city.get("places", []):
                if "bike_list" in place:
                    for bike in place["bike_list"]:
                        scooter_list.append(
                            {
                                "timestamp": current_time,
                                "vehicle_id": bike.get("number"),
                                "lat": place.get("lat"),
                                "lon": place.get("lng"),
                                "battery_percent": bike.get("battery", 100),
                                "vehicle_type": bike.get("bike_type"),
                            }
                        )
    return pd.DataFrame(scooter_list)


print("Starting 1-hour collection window with 3-minute intervals...")

# Run 20 times (20 intervals * 3 minutes = 60 minutes)
for i in range(20):
    print(f"Cycle {i+1}/20 at {datetime.now().strftime('%H:%M:%S')}")
    new_data = scrape_snapshot()

    if not new_data.empty:
        file_exists = os.path.isfile(CSV_FILE)
        new_data.to_csv(CSV_FILE, mode="a", header=not file_exists, index=False)

    # Sleep for 3 minutes (180 seconds), except on the very last cycle
    if i < 19:
        time.sleep(180)

print("Collection window finished. Handing over to GitHub to save data.")
