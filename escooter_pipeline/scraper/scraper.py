import requests
import json
import os
from datetime import datetime
import time

# -----------------------------
# CONFIG
# -----------------------------
OPERATORS = {
    "tier": "https://api.tier-services.io/v1/vehicle?lat=52.5200&lng=13.4050",
    "lime": "https://data.lime.bike/api/partners/v1/vehicles",
    "voi": "https://api.voiapp.io/v1/vehicle/status/geo",
    "bolt": "https://bolt.eu/api/v1/scooters?lat=52.5200&lng=13.4050"
}

OUTPUT_DIR = "escooter_pipeline/data/raw"


# -----------------------------
# SAFE REQUEST WITH RETRIES
# -----------------------------
def fetch_with_retries(url, retries=3):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[WARN] Status {response.status_code} on attempt {attempt}")
        except Exception as e:
            print(f"[ERROR] Attempt {attempt} failed: {e}")

        time.sleep(3 if attempt == 1 else 5)

    print("[FAIL] All retries failed")
    return None


# -----------------------------
# SCHEMA-AGNOSTIC PARSING
# -----------------------------
def extract_vehicles(data):
    if not data:
        return []

    # Try common patterns
    return (
        data.get("vehicles")
        or data.get("data")
        or data.get("items")
        or data.get("result")
        or []
    )


# -----------------------------
# SAVE JSON WITH TIMESTAMP
# -----------------------------
def save_json(operator, vehicles):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    timestamp = datetime.utcnow().strftime("%H-%M")

    folder = os.path.join(OUTPUT_DIR, today)
    os.makedirs(folder, exist_ok=True)

    filename = f"{operator}_{timestamp}.json"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w") as f:
        json.dump(vehicles, f)

    print(f"[OK] Saved {len(vehicles)} vehicles → {filepath}")


# -----------------------------
# MAIN SCRAPER LOOP
# -----------------------------
def scrape_once():
    print("\n==============================")
    print("SCRAPE START:", datetime.utcnow())
    print("==============================")

    for operator, url in OPERATORS.items():
        print(f"\nFetching {operator}...")

        data = fetch_with_retries(url)
        vehicles = extract_vehicles(data)

        if len(vehicles) == 0:
            print(f"[WARN] No vehicles found for {operator}")

        save_json(operator, vehicles)

    print("\nSCRAPE COMPLETE\n")


if __name__ == "__main__":
    scrape_once()
