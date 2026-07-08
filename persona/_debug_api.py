#!/usr/bin/env python3
"""Debug: check API region coverage."""
import requests, json
resp = requests.get("https://www.ris.gov.tw/rs-opendata/api/v1/datastore/ODRP014/11405", timeout=30)
data = resp.json().get("responseData", [])

cities = {}
for item in data:
    sid = item.get("site_id", "")
    # Extract first city/town name
    parts = sid.replace("台", "臺")
    city = parts[:3]
    cities[city] = cities.get(city, 0) + 1

print(f"Total records: {len(data)}")
for c in sorted(cities, key=lambda x: -cities[x]):
    print(f"  {c}: {cities[c]}")
