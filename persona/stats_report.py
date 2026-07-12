#!/usr/bin/env python3
"""Generate distribution stats for the current 997 personas."""
import json
from collections import Counter, defaultdict

with open("tw_persona_997.json") as f:
    data = json.load(f)

print("# TW Persona DB — 997 統計分布")
print()

# 1. Age x Sex
print("## 1. 年齡 x 性別")
agesex = Counter()
for p in data:
    d = p["dimensions"]
    agesex[(d["age"], d["sex"])] += 1
for a in ["0-11","12-18","19-24","25-34","35-44","45-54","55-64","65+"]:
    m = agesex.get((a,"男"),0)
    f = agesex.get((a,"女"),0)
    bar = "█" * ((m+f)//5)
    print(f"  {a:<6s}: {m+f:>3d}人 (男{m} 女{f}) {bar}")

# 2. Region
print()
print("## 2. 區域")
regions = Counter(p["dimensions"]["region"] for p in data)
for r in ["北北基","桃竹苗","中彰投","雲嘉南","高屏","宜花東","離島"]:
    c = regions[r]
    bar = "█" * (c//5)
    print(f"  {r:<6s}: {c:>3d}人 ({c/997*100:.1f}%) {bar}")

# 3. Occupation
print()
print("## 3. 職業")
occs = Counter(p["dimensions"]["occupation"] for p in data)
for o,c in sorted(occs.items(), key=lambda x:-x[1]):
    print(f"  {o}: {c}人 ({c/997*100:.1f}%)")

# 4. Income
print()
print("## 4. 個人收入")
incs = Counter(p["dimensions"]["income"] for p in data)
for k in ["無收入","<3萬","3-8萬",">8萬"]:
    c = incs.get(k,0)
    print(f"  {k}: {c}人 ({c/997*100:.1f}%)")

# 5. Family Income (new 5-tier)
print()
print("## 5. 家庭可支配所得（新5級）")
fincs = Counter(p["dimensions"]["family_income"] for p in data)
for k in ["<1萬","1-3萬","3-7萬","7萬","百萬"]:
    c = fincs.get(k,0)
    print(f"  {k}: {c}人 ({c/997*100:.1f}%)")

# 6. Marriage
print()
print("## 6. 婚姻狀況")
mars = Counter(p["dimensions"]["marriage"] for p in data)
for k in ["未婚","已婚","離婚","鰥寡"]:
    c = mars.get(k,0)
    print(f"  {k}: {c}人 ({c/997*100:.1f}%)")

# 7. Politics (age-gated)
print()
print("## 7. 政治傾向")
pols = Counter()
for p in data:
    d = p["dimensions"]
    if d["age"] not in ("0-11","12-18"):
        pols[d["politics"]] += 1
    else:
        pols["(未成年不標籤)"] += 1
for k,c in sorted(pols.items(), key=lambda x:-x[1]):
    print(f"  {k}: {c}人 ({c/997*100:.1f}%)")

# 8. Media Diet
print()
print("## 8. 媒體習慣")
meds = Counter(p["dimensions"]["media_diet"] for p in data)
for k,c in sorted(meds.items(), key=lambda x:-x[1]):
    print(f"  {k}: {c}人 ({c/997*100:.1f}%)")

# 9. Education
print()
print("## 9. 教育程度")
edus = Counter(p["dimensions"]["education"] for p in data)
for k,c in sorted(edus.items(), key=lambda x:-x[1]):
    print(f"  {k}: {c}人 ({c/997*100:.1f}%)")

# 10. Family Size
print()
print("## 10. 家庭口數")
fams = Counter(p["dimensions"]["family_size"] for p in data)
for k,c in sorted(fams.items(), key=lambda x:-x[1]):
    print(f"  {k}: {c}人 ({c/997*100:.1f}%)")

# 11. Names
print()
print("## 11. 名字唯一性")
names = Counter(p["name"] for p in data)
print(f"  不重複名字: {len(names)}個 ({len(names)/997*100:.1f}%)")
top = names.most_common(1)[0]
print(f"  最高頻: {top[0]}({top[1]}次)")

# 12. Background stories
print()
print("## 12. 背景故事多樣性")
sents = Counter()
for p in data:
    for seg in p["dimensions"]["background_story"].replace("。","\n").split("\n"):
        seg = seg.strip()
        if seg:
            sents[seg] += 1
unique_stories = len(set(p["dimensions"]["background_story"] for p in data))
print(f"  唯一句子: {len(sents)} 個")
print(f"  完整故事唯一組合: {unique_stories} 組 (共 997 人)")

# 13. Cross-check: tech + low education
print()
print("## 13. 交叉：科技業 x 教育程度")
oe = Counter()
for p in data:
    d = p["dimensions"]
    oe[(d["occupation"], d["education"])] += 1
print(f"  科技 + 高中以下: {oe.get(('科技','高中以下'),0)} 人 [子 agent指出問題]")
print(f"  科技 + 大學:     {oe.get(('科技','大學'),0)} 人")
print(f"  科技 + 研究所:   {oe.get(('科技','研究所以上'),0)} 人")

# 14. 0-11 Media Diet
print()
print("## 14. 0-11 媒體習慣 [子 agent指出問題]")
meds011 = Counter()
for p in data:
    if p["dimensions"]["age"] == "0-11":
        meds011[p["dimensions"]["media_diet"]] += 1
for k,c in sorted(meds011.items(), key=lambda x:-x[1]):
    note = "不合理" if k == "社群為主" else ("合理" if k in ("家長主導","兒童內容") else "?")
    print(f"  {k}: {c}人 ({c/110*100:.1f}%)")

# 15. 1人+已婚
print()
print("## 15. 1人家庭+已婚 [子 agent指出問題]")
alone_married = sum(1 for p in data if p["dimensions"]["family_size"]=="1" and p["dimensions"]["marriage"]=="已婚")
alone_divorced = sum(1 for p in data if p["dimensions"]["family_size"]=="1" and p["dimensions"]["marriage"]=="離婚")
print(f"  1人+已婚: {alone_married} 人 — 背景故事沒提配偶")
print(f"  1人+離婚: {alone_divorced} 人")

# 16. 0-11 hobbies check
print()
print("## 16. 0-11 興趣檢查 [子 agent指出問題]")
hobbies011 = Counter()
for p in data:
    if p["dimensions"]["age"] == "0-11":
        for h in p["dimensions"]["hobby"]:
            hobbies011[h] += 1
print("  0-11 興趣分布:")
for h,c in sorted(hobbies011.items(), key=lambda x:-x[1]):
    note = ""
    if h in ("泡茶","登山"):
        note = " [子 agent: 對幼童不合理]"
    print(f"    {h}: {c}回{note}")
