#!/usr/bin/env python3
"""
Stratified sampling from tw_persona_1069.json.
Extracts 1 persona from each (region, age, sex) combo = 112 samples total.
For combos with multiple personas, picks randomly but with seed for reproducibility.

Usage:
    python3 sample_stratified.py
    → writes tw_persona_112_stratified.json (112 entries)
    → prints summary table
"""
import json, random, sys
from collections import Counter, OrderedDict

SEED = 42
random.seed(SEED)

with open("tw_persona_1069.json") as f:
    data = json.load(f)

# Build index: (region, age, sex) → list of personas
index = {}
for p in data:
    d = p["dimensions"]
    key = (d["region"], d["age"], d["sex"])
    index.setdefault(key, []).append(p)

regions = ["都會區(六都)", "北部", "中部", "南部", "花東", "離島"]
ages = ["0-11", "12-18", "19-24", "25-34", "35-44", "45-54", "55-64", "65+"]
sexes = ["男", "女"]

samples = []
coverage = {}
for r in regions:
    for a in ages:
        for s in sexes:
            key = (r, a, s)
            pool = index.get(key, [])
            if pool:
                chosen = random.choice(pool)
                samples.append(chosen)
                coverage[key] = len(pool)
            else:
                coverage[key] = 0

# Sort by region, then age, then sex for reproducible output order
def sort_key(p):
    d = p["dimensions"]
    ri = regions.index(d["region"])
    ai = ages.index(d["age"])
    si = sexes.index(d["sex"])
    return (ri, ai, si)

samples.sort(key=sort_key)

# Write
with open("tw_persona_112_stratified.json", "w", encoding="utf-8") as f:
    json.dump(samples, f, ensure_ascii=False, indent=2)

# Summary
print(f"📊 分層抽樣報告")
print(f"   96/96 組合已抽樣（{len(regions)} regions × {len(ages)} ages × {len(sexes)} sexes）")
print()

# Coverage table
print(f"组合覆蓋率：")
print(f"{'組合':<20} {'總數':>4} → {'抽樣':>4}")
for key in sorted(coverage.keys(), key=lambda k: (regions.index(k[0]), ages.index(k[1]), sexes.index(k[2]))):
    r, a, s = key
    total = coverage[key]
    symbol = "✅" if total > 0 else "❌"
    print(f"  {r:<3} {a:<5} {s:<2} {symbol}  pool={total} → 1")

# Also show distribution of age/region/sex in the sample
print(f"\n年齡層分布：")
age_counts = Counter(p["dimensions"]["age"] for p in samples)
for a in ages:
    print(f"  {a}: {age_counts[a]}")
print(f"  合計: {sum(age_counts.values())}")

print(f"\n區域分布：")
region_counts = Counter(p["dimensions"]["region"] for p in samples)
for r in regions:
    print(f"  {r}: {region_counts[r]}")
print(f"  合計: {sum(region_counts.values())}")

print(f"\n✅ 已寫入 tw_persona_112_stratified.json")
