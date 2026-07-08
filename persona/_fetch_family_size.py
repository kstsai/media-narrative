#!/usr/bin/env python3
"""Fetch real household size distribution from ODRP025 API."""
import requests, json
from collections import Counter

print("Fetching ODRP025 (household structure)...")
resp = requests.get("https://www.ris.gov.tw/rs-opendata/api/v1/datastore/ODRP025/114", timeout=30)
data = resp.json().get("responseData", [])

# Map API fields to family size
fields = {
    "household_single_total": "1",
    "home_group_02": "2",
    "home_group_03": "3",
    "home_group_04": "4",
    "home_group_05": "5+",
    "home_group_06": "5+",
    "home_group_07": "5+",
    "home_group_08": "5+",
    "home_group_09": "5+",
    "home_group_10up": "5+",
}

total_hh_by_size = Counter()
for item in data:
    for api_field, size_cat in fields.items():
        val = int(item.get(api_field, 0) or 0)
        if val > 0:
            total_hh_by_size[size_cat] += val

total = sum(total_hh_by_size.values())
print(f"\nTotal households: {total:,}")
print()
print("Real household size distribution:")
for c in ["1", "2", "3", "4", "5+"]:
    pct = total_hh_by_size[c] / total * 100
    bar = "█" * int(pct / 2)
    print(f"  {c}人: {pct:5.1f}% ({total_hh_by_size[c]:>8,}) {bar}")

# Output as Python dict for copy-paste
print()
print("FAMILY_SIZE_REAL = {")
for c in ["1", "2", "3", "4", "5+"]:
    pct = total_hh_by_size[c] / total
    print(f'    "{c}": {pct:.4f},')
print("}")
