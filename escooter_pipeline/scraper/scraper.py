import requests
import json
import os
from datetime import datetime

OPERATORS = {
    "tier": "https://data.tier-services.io/gbfs/2.2/wien/gbfs.json",
    "lime": "https://data.lime.bike/api/partners/v1/gbfs/wien/gbfs.json",
    "voi": "https://gbfs.voiapp.io/wien/gbfs.json",
    "bird": "https://gbfs.bird.co/wien/gbfs.json"
}



def fetch_json(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

def scrape_operator(name, root_url, save_dir):
    print(f"\nFetching {name}...")

    root = fetch_json(root_url)
    if not root:
        print(f"[FAIL] Could not fetch root GBFS for {name}")
        return

    # Find free_bike_status feed
    feeds = root.get("data", {}).get("en", {}).get("feeds", [])
    free_bike_url = None

    for feed in feeds:
        if feed["name"] == "free_bike_status":
            free_bike_url = feed["url"]

    if not free_bike_url:
        print(f"[FAIL] No free_bike_status feed for {name}")
        return

    bikes = fetch_json(free_bike_url)
    if not bikes:
        print(f"[FAIL] Could not fetch bikes for {name}")
        return

    # Save file
    timestamp = datetime.utcnow().strftime("%H-%M")
    filename = f"{name}_{timestamp}.json"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "w") as f:
        json.dump(bikes, f)

    count = len(bikes.get("data", {}).get("bikes", []))
    print(f"[OK] Saved {count} vehicles → {filepath}")

def main():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    save_dir = f"escooter_pipeline/data/raw/{today}"
    os.makedirs(save_dir, exist_ok=True)

    print("\n==============================")
    print(f"GBFS SCRAPE START: {datetime.utcnow()}")
    print("==============================")

    for name, url in OPERATORS.items():
        scrape_operator(name, url, save_dir)

    print("\nSCRAPE COMPLETE\n")

if __name__ == "__main__":
    main()
