#!/usr/bin/env python3
"""Find the top 10 most populous persona combinations from real Taiwan population data."""
import requests, json, re, sys
from collections import defaultdict

def api_age_to_rfc(age):
    if age <= 11: return "0-11"
    if 12 <= age <= 18: return "12-18"
    if 19 <= age <= 24: return "19-24"
    if 25 <= age <= 34: return "25-34"
    if 35 <= age <= 44: return "35-44"
    if 45 <= age <= 54: return "45-54"
    if 55 <= age <= 64: return "55-64"
    return "65+"

def city_to_rfc_region(city):
    north = ["臺北市", "新北市", "基隆市"]
    taoyuan = ["桃園市", "新竹市", "新竹縣", "苗栗縣"]
    central = ["臺中市", "彰化縣", "南投縣"]
    south_west = ["雲林縣"]
    south = ["臺南市", "高雄市", "嘉義市", "嘉義縣", "屏東縣"]
    east = ["宜蘭縣", "花蓮縣", "臺東縣"]
    island = ["澎湖縣", "金門縣", "連江縣"]

    for c in north:
        if c in city: return "北北基"
    for c in taoyuan:
        if c in city: return "桃竹苗"
    for c in central:
        if c in city: return "中彰投"
    for c in south_west:
        if c in city: return "雲嘉南"
    for c in south:
        if c in city: return "高屏"
    for c in east:
        if c in city: return "宜花東"
    for c in island:
        if c in city: return "離島"
    return "其他"

print("Fetching ODRP014...", file=sys.stderr)
resp = requests.get("https://www.ris.gov.tw/rs-opendata/api/v1/datastore/ODRP014/11405", timeout=30)
data = resp.json().get("responseData", [])

age_pattern = re.compile(r'^people_age_(\d+)_([mf])$')
counts = defaultdict(int)

for item in data:
    site_id = item.get("site_id", "")
    region = city_to_rfc_region(site_id)
    for col, val in item.items():
        m = age_pattern.match(col)
        if m and val:
            age = int(m.group(1))
            sex = "男" if m.group(2) == "m" else "女"
            pop = int(val)
            if pop > 0:
                rfc_age = api_age_to_rfc(age)
                key = (region, rfc_age, sex)
                counts[key] += pop

sorted_items = sorted(counts.items(), key=lambda x: -x[1])
total_pop = sum(counts.values())

print(f"\n{'='*70}")
print(f"  TOP 10 人口組合 (by 區域 x 年齡 x 性別)")
print(f"{'='*70}")
print(f"  {'#':<3s} {'區域':<8s} {'年齡':<6s} {'性別':<4s} {'人口':>10s} {'佔比':>8s}")
print(f"  {'-'*50}")

for i, ((region, age, sex), pop) in enumerate(sorted_items[:15], 1):
    pct = pop / total_pop * 100
    print(f"  {i:<3d} {region:<8s} {age:<6s} {sex:<4s} {pop:>10,d} {pct:>7.2f}%")

print(f"\n  Total: {total_pop:,}")
print(f"{'='*70}")

# Output JSON
result = [{"rank": i+1, "region": r, "age": a, "sex": s, "population": p, "pct": round(p/total_pop*100, 2)}
          for i, ((r, a, s), p) in enumerate(sorted_items[:10])]
with open("/home/ubuntu/.hermes/cache/top10_persona_combos.json", "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\nJSON saved to /home/ubuntu/.hermes/cache/top10_persona_combos.json")
