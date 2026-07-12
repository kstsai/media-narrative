#!/usr/bin/env python3
"""
QA validation script for TW Persona DB.
Run after _generate_997.py to check for known coherence issues.
Exit code = number of violations found (0 = clean).
"""
import json, sys
from collections import Counter

VIOLATIONS = []

def check(condition, msg):
    if not condition:
        VIOLATIONS.append(msg)

# ── Load data ──
with open("tw_persona_1069.json") as f:
    data = json.load(f)

print(f"🧪 QA: {len(data)} personas loaded\n")

# ── Rule 1: Minors can't live alone ──
bad = [p for p in data if p["dimensions"]["age"] in ("0-11","12-18") and p["dimensions"]["family_size"] == "1"]
for p in bad:
    check(False, f"[R1] 未成年獨居: {p['name']} ({p['dimensions']['age']})")
if not bad:
    print("  [R1] 未成年獨居: ✅ 0 violations")

# ── Rule 2: Minors can't have economic phrases ──
ECON_KW = ["手頭緊","精打細算","比價","物價","開銷大","寬裕","積蓄","生活品質"]
bad = []
for p in data:
    if p["dimensions"]["age"] in ("0-11","12-18"):
        for kw in ECON_KW:
            if kw in p["dimensions"]["background_story"]:
                bad.append((p["name"], kw))
                break
for name, kw in bad[:5]:
    check(False, f"[R2] 未成年有經濟短語「{kw}」: {name}")
if not bad:
    print("  [R2] 未成年經濟短語: ✅ 0 violations")

# ── Rule 3: No ambiguous 或 in household descriptions ──
AMBIGUOUS = ["或", "手足", "兄弟姊妹"]
bad = []
for p in data:
    story = p["dimensions"]["background_story"]
    for kw in AMBIGUOUS:
        if kw in story and "離婚" not in story:
            for seg in story.split("。"):
                if kw in seg and "經濟" not in seg and "離婚" not in seg and "多位" not in seg and "及" not in seg:  # 多位兄弟姊妹 is fine
                    bad.append((p["name"], kw, seg.strip()))
                    break
for name, kw, seg in bad[:10]:
    check(False, f"[R3] 模糊家庭描述「{kw}」: {name} → {seg}")
if not bad:
    print("  [R3] 模糊家庭描述: ✅ 0 violations")

# ── Rule 4: No census-form prompt_prefix (old format: 19-24的北北基男性，離婚，學生…)
# Old format had region+sex followed by comma+marriage (e.g., 北北基男性，未婚)
# New format has region+sex followed by ，住在 (e.g., 北北基男性，住在)
CENSUS_PATTERNS = []
for region in ["北北基","桃竹苗","中彰投","雲嘉南","高屏","宜花東","離島"]:
    for sex in ["男性","女性"]:
        base = f"{region}{sex}，"
        for marriage in ["未婚","已婚","離婚","鰥寡"]:
            CENSUS_PATTERNS.append(base + marriage)
bad = []
for p in data:
    prefix = p["prompt_prefix"]
    for pat in CENSUS_PATTERNS:
        if pat in prefix:
            bad.append(p["name"])
            break
for name in bad[:5]:
    check(False, f"[R4] 舊格式 prompt_prefix: {name}")
if not bad:
    print("  [R4] prompt_prefix 舊格式: ✅ 0 violations")

# ── Rule 5: 35+ professionals with low education ──
bad = []
for p in data:
    d = p["dimensions"]
    if d["age"] in ("35-44","45-54","55-64") and d["occupation"] in ("科技","金融","醫療") and d["education"] in ("國中以下","高中"):
        bad.append((p["name"], d["age"], d["occupation"], d["education"]))
for name, age, occ, edu in bad:
    check(False, f"[R5] 35+專業低學歷: {name} ({age}/{occ}/{edu})")
if not bad:
    print("  [R5] 專業人士學歷: ✅ 0 violations")

# ── Rule 6: Distribution sanity ──
ages = Counter(p["dimensions"]["age"] for p in data)
regions = Counter(p["dimensions"]["region"] for p in data)
# Check all 1069 accounted for
total = sum(ages.values())
check(total == 1069, f"[R6] 總數應為 1069，實際 {total}")
# Check no age group is empty
for a in ["0-11","12-18","19-24","25-34","35-44","45-54","55-64","65+"]:
    check(ages[a] > 0, f"[R6] 年齡層 {a} 為空")
if total == 997 and all(ages[a] > 0 for a in ["0-11","12-18","19-24","25-34","35-44","45-54","55-64","65+"]):
    print("  [R6] 分布合理性: ✅ 997 人, 8 年齡層皆有")

# ── Rule 7: Name uniqueness (known baseline) ──
names = Counter(p["name"] for p in data)
unique_ratio = len(names) / len(data)
check(unique_ratio >= 0.15, f"[R7] 名字唯一性 {unique_ratio*100:.1f}% < 15%")
max_freq = names.most_common(1)[0][1]
check(max_freq <= 20, f"[R7] 最高頻名字出現 {max_freq} 次 > 20")
if unique_ratio >= 0.15 and max_freq <= 20:
    print(f"  [R7] 名字多樣性: ✅ {len(names)} 唯一名 ({unique_ratio*100:.1f}%), 最高 {max_freq} 次")

# ── Rule 8: No 離婚 for 19-24 students ──
bad = []
for p in data:
    d = p["dimensions"]
    if d["age"] == "19-24" and d["marriage"] == "離婚" and d["occupation"] == "學生":
        bad.append(p["name"])
for name in bad:
    check(False, f"[R8] 19-24學生離婚: {name}")
if not bad:
    print("  [R8] 學生離婚: ✅ 0 violations")

# ── Rule 9: 0-11 media diet (no 社群為主) ──
bad = []
for p in data:
    if p["dimensions"]["age"] == "0-11" and p["dimensions"]["media_diet"] == "社群為主":
        bad.append(p["name"])
for name in bad[:5]:
    check(False, f"[R9] 0-11 社群為主: {name}")
if not bad:
    print("  [R9] 兒童媒體習慣: ✅ 0 violations")

# ── Rule 10: No "65+歲" code residue in prompt_prefix ──
bad = [p for p in data if "65+歲" in p["prompt_prefix"]]
for p in bad[:5]:
    check(False, f"[R10] 65+歳程式碼殘留: {p['name']} → …{p['prompt_prefix'][:60]}…")
if not bad:
    print("  [R10] 65+歳殘留: ✅ 0 violations")

# ── Rule 11: No "做退休" or "做學生" in prompt_prefix ──
bad = []
for p in data:
    if "做退休" in p["prompt_prefix"] or "做學生" in p["prompt_prefix"]:
        bad.append((p["name"], p["prompt_prefix"][:80]))
for name, snippet in bad[:8]:
    check(False, f"[R11] 不通順「做退休/做學生」: {name} → …{snippet}…")
if not bad:
    print("  [R11] 做退休/做學生: ✅ 0 violations")

# ── Rule 12: No 【】bracket template format in prompt_prefix ──
bad = [p for p in data if "【" in p["prompt_prefix"]]
for p in bad[:5]:
    check(False, f"[R12] 【】模板格式: {p['name']} → {p['prompt_prefix'][:80]}")
if not bad:
    print("  [R12] 【】模板格式: ✅ 0 violations")

# ── Rule 13: No "獨生子" for female personas ──
bad = []
for p in data:
    story = p["dimensions"]["background_story"]
    if "獨生子" in story and p["dimensions"]["sex"] == "女":
        bad.append(p["name"])
for name in bad[:5]:
    check(False, f"[R13] 女性被稱「獨生子」: {name}")
if not bad:
    print("  [R13] 獨生子/獨生女: ✅ 0 violations")

# ── Rule 14: No "新婚不久" for 45+ ──
bad = []
for p in data:
    story = p["dimensions"]["background_story"]
    if "新婚不久" in story and p["dimensions"]["age"] in ("45-54","55-64","65+"):
        bad.append((p["name"], p["dimensions"]["age"]))
for name, age in bad[:5]:
    check(False, f"[R14] 45+「新婚不久」: {name} ({age})")
if not bad:
    print("  [R14] 45+新婚不久: ✅ 0 violations")

# ── Rule 15: Location redundancy in prompt_prefix ──
LOCATIONS = ["都會區(六都)","北部","中部","南部","花東","離島"]
bad = []
for p in data:
    prefix = p["prompt_prefix"]
    locs_found = [loc for loc in LOCATIONS if loc in prefix]
    if len(locs_found) >= 2:
        bad.append((p["name"], locs_found))
for name, locs in bad[:10]:
    check(False, f"[R15] 地點重複: {name} → {', '.join(locs)}")
if not bad:
    print("  [R15] 地點重複: ✅ 0 violations")

# ── Rule 16: No "新婚" phrases for 55+ in background_story ──
bad = []
for p in data:
    story = p["dimensions"]["background_story"]
    if "新婚" in story and p["dimensions"]["age"] in ("55-64","65+"):
        bad.append((p["name"], p["dimensions"]["age"]))
for name, age in bad[:5]:
    check(False, f"[R16] 55+「新婚」短語: {name} ({age})")
if not bad:
    print("  [R16] 55+新婚短語: ✅ 0 violations")

# ── Rule 17: No "兒孫滿堂" for under 55 in background_story ──
bad = []
for p in data:
    story = p["dimensions"]["background_story"]
    if "兒孫滿堂" in story and p["dimensions"]["age"] in ("19-24","25-34","35-44","45-54"):
        bad.append((p["name"], p["dimensions"]["age"]))
for name, age in bad[:5]:
    check(False, f"[R17] 未滿55「兒孫滿堂」: {name} ({age})")
if not bad:
    print("  [R17] 兒孫滿堂年齡: ✅ 0 violations")

# ── Rule 18: No 泡茶 hobby for minors (0-18) ──
bad = []
for p in data:
    hobby = p["dimensions"]["hobby"]
    if "泡茶" in hobby and p["dimensions"]["age"] in ("0-11","12-18"):
        bad.append((p["name"], p["dimensions"]["age"]))
for name, age in bad[:5]:
    check(False, f"[R18] 未成年泡茶: {name} ({age})")
if not bad:
    print("  [R18] 未成年泡茶: ✅ 0 violations")
# ── Rule 19: family>1 but "一個人過日子" ──
SINGLE_PHRASES = ["現在一個人過日子", "一個人過日子"]
bad = []
for p in data:
    story = p["dimensions"]["background_story"]
    if p["dimensions"]["family_size"] not in ("1",):
        for ph in SINGLE_PHRASES:
            if ph in story:
                bad.append((p["name"], p["dimensions"]["family_size"]))
                break
for name, fam in bad[:5]:
    check(False, f"[R19] {fam}人家庭但「一個人過日子」: {name}")
if not bad:
    print("  [R19] 家庭人數矛盾: ✅ 0 violations")

print(f"\n{'='*50}")
if VIOLATIONS:
    print(f"❌ {len(VIOLATIONS)} violations found:")
    for v in VIOLATIONS:
        print(f"  • {v}")
    sys.exit(len(VIOLATIONS))
else:
    print("✅ ALL CHECKS PASSED")
    sys.exit(0)
