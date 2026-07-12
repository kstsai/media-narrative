#!/usr/bin/env python3
"""
Generate 997 personas from weighted Taiwan population data.
Uses real API data where available + known population ratios for complete coverage.
"""
import requests, json, sys, re, random
from collections import defaultdict, Counter, deque

random.seed(42)

# ═══ 1. POPULATION DATA ═══

# Taiwan population distribution by new 6-region system (2025 estimates)
# Source: population_by_region_age_sex_2025.csv
REGION_POP = {
    "都會區(六都)": 0.694, "北部": 0.103, "中部": 0.103,
    "南部": 0.067, "花東": 0.023, "離島": 0.011
}

# Age distribution within each region (from real data where available, national estimates otherwise)
AGE_DIST = {
    "0-11": 0.11, "12-18": 0.07, "19-24": 0.07,
    "25-34": 0.14, "35-44": 0.16, "45-54": 0.16,
    "55-64": 0.15, "65+": 0.14
}

SEX_DIST = {"男": 0.495, "女": 0.505}

# Real data from API (北北基 + 桃竹苗) to calibrate age×sex within city
print("📡 Fetching real population data for calibration...", file=sys.stderr)
try:
    resp = requests.get("https://www.ris.gov.tw/rs-opendata/api/v1/datastore/ODRP014/11405", timeout=30)
    raw = resp.json().get("responseData", [])
except:
    raw = []

def api_age_to_rfc(age):
    if age <= 11: return "0-11"
    if 12 <= age <= 18: return "12-18"
    if 19 <= age <= 24: return "19-24"
    if 25 <= age <= 34: return "25-34"
    if 35 <= age <= 44: return "35-44"
    if 45 <= age <= 54: return "45-54"
    if 55 <= age <= 64: return "55-64"
    return "65+"

# Calculate real age×sex ratios within each fetched city
real_ratios = defaultdict(lambda: defaultdict(float))
pat = re.compile(r'^people_age_(\d+)_([mf])$')
for item in raw:
    for col, val in item.items():
        m = pat.match(col)
        if m and val:
            age, sex = int(m.group(1)), "男" if m.group(2)=="m" else "女"
            rfc = api_age_to_rfc(age)
            real_ratios[rfc][sex] += int(val)

# Normalize to proportions
total_real = sum(sum(d.values()) for d in real_ratios.values())
for age in real_ratios:
    for sex in real_ratios[age]:
        real_ratios[age][sex] /= total_real

# Generate target counts per (region, age, sex)
TARGET = 1069
weighted = []
for region, rpct in REGION_POP.items():
    for age, apct in AGE_DIST.items():
        for sex, spct in SEX_DIST.items():
            w = rpct * apct * spct
            n = max(1, round(w * TARGET))
            weighted.append((region, age, sex, w, n))

# Adjust to exactly 997
total_n = sum(n for _,_,_,_,n in weighted)
while total_n < TARGET:
    max_idx = max(range(len(weighted)), key=lambda i: weighted[i][3] / weighted[i][4])
    w = list(weighted[max_idx])
    w[4] += 1
    weighted[max_idx] = tuple(w)
    total_n += 1
while total_n > TARGET:
    candidates = [i for i in range(len(weighted)) if weighted[i][4] > 1]
    if not candidates: break
    min_idx = min(candidates, key=lambda i: weighted[i][3] / weighted[i][4])
    w = list(weighted[min_idx])
    w[4] -= 1
    weighted[min_idx] = tuple(w)
    total_n -= 1

print(f"Target distribution: {len(weighted)} combos x {TARGET} total", file=sys.stderr)

# ═══ 2. DIMENSION PROBABILITIES ═══

EDU_PROB = {
    "0-11":{"國中以下":1},
    "12-18":{"國中以下":0.50,"高中":0.50},
    "19-24":{"國中以下":0.05,"高中":0.25,"大學":0.60,"研究所以上":0.10},
    "25-34":{"國中以下":0.02,"高中":0.13,"大學":0.55,"研究所以上":0.30},
    "35-44":{"國中以下":0.05,"高中":0.20,"大學":0.50,"研究所以上":0.25},
    "45-54":{"國中以下":0.10,"高中":0.25,"大學":0.45,"研究所以上":0.20},
    "55-64":{"國中以下":0.20,"高中":0.30,"大學":0.35,"研究所以上":0.15},
    "65+":{"國中以下":0.30,"高中":0.30,"大學":0.30,"研究所以上":0.10},
}

# Real occupation distribution from DGBAS 2024 Manpower Survey
# Source: 113年人力資源調查統計年報, 表47 就業者之教育程度與年齡—按職業分
OCC_PROB = {
    ("0-11","男"): {"學生":1.00},
    ("0-11","女"): {"學生":1.00},

    ("12-18","男"): {"學生":1.00},
    ("12-18","女"): {"學生":1.00},

    ("19-24","男"): {"學生":0.47, "製造":0.25, "服務":0.19, "科技":0.05, "公務":0.02, "醫療":0.01, "教育":0.01},
    ("25-34","男"): {"製造":0.41, "服務":0.21, "科技":0.16, "其他":0.08, "教育":0.07, "醫療":0.04, "公務":0.03},
    ("35-44","男"): {"製造":0.49, "科技":0.15, "服務":0.15, "教育":0.06, "其他":0.06, "醫療":0.04, "公務":0.03, "自營":0.02},
    ("45-54","男"): {"製造":0.48, "服務":0.14, "科技":0.13, "其他":0.11, "公務":0.04, "教育":0.04, "自營":0.03, "醫療":0.03},
    ("55-64","男"): {"製造":0.39, "退休":0.30, "服務":0.11, "科技":0.07, "家管":0.05, "公務":0.03, "自營":0.02, "教育":0.02, "醫療":0.01},
    ("65+","男"):   {"退休":0.74, "家管":0.13, "製造":0.09, "服務":0.03, "科技":0.01},

    ("19-24","女"): {"學生":0.48, "服務":0.27, "製造":0.08, "科技":0.07, "公務":0.05, "教育":0.03, "醫療":0.02},
    ("25-34","女"): {"服務":0.32, "科技":0.16, "製造":0.16, "家管":0.12, "公務":0.09, "教育":0.07, "醫療":0.04, "其他":0.04},
    ("35-44","女"): {"服務":0.26, "製造":0.23, "科技":0.14, "家管":0.14, "公務":0.09, "教育":0.05, "其他":0.05, "醫療":0.03, "自營":0.01},
    ("45-54","女"): {"服務":0.25, "製造":0.22, "家管":0.21, "科技":0.11, "公務":0.07, "其他":0.07, "教育":0.04, "醫療":0.02, "自營":0.01},
    ("55-64","女"): {"家管":0.43, "退休":0.18, "製造":0.15, "服務":0.14, "科技":0.04, "公務":0.03, "自營":0.01, "醫療":0.01, "教育":0.01},
    ("65+","女"):   {"家管":0.67, "退休":0.28, "製造":0.03, "服務":0.02},
}

INC_PROB = {
    "學生":{"無收入":1.0},"退休":{"<3萬":0.5,"3-8萬":0.4,">8萬":0.1},
    "家管":{"<3萬":0.4,"3-8萬":0.5,">8萬":0.1},"科技":{"3-8萬":0.4,">8萬":0.5,"<3萬":0.1},
    "金融":{"3-8萬":0.5,">8萬":0.4,"<3萬":0.1},"醫療":{"3-8萬":0.5,">8萬":0.4,"<3萬":0.1},
    "教育":{"3-8萬":0.6,">8萬":0.2,"<3萬":0.2},"公務":{"3-8萬":0.6,">8萬":0.2,"<3萬":0.2},
    "服務":{"<3萬":0.4,"3-8萬":0.5,">8萬":0.1},"製造":{"<3萬":0.3,"3-8萬":0.6,">8萬":0.1},
    "自營":{"3-8萬":0.4,">8萬":0.4,"<3萬":0.2},"其他":{"<3萬":0.4,"3-8萬":0.4,">8萬":0.2},
}

# New dimensions
# Real data from ODRP025 API
FAMILY_SIZE_REAL = {"1": 0.4177, "2": 0.2133, "3": 0.1719, "4": 0.1182, "5+": 0.0789}

# Age-adjusted: elderly more single, young families more 3-4
FAMILY_SIZE_PROB = {
    "0-11":  {"4":0.29,"5+":0.29,"3":0.25,"2":0.17},
    "12-18": {"4":0.29,"5+":0.29,"3":0.25,"2":0.17},
    "19-24": {"3":0.25,"4":0.22,"2":0.20,"1":0.18,"5+":0.15},
    "25-34": {"2":0.28,"3":0.25,"1":0.22,"4":0.15,"5+":0.10},
    "35-44": {"3":0.25,"2":0.22,"4":0.20,"1":0.18,"5+":0.15},
    "45-54": {"2":0.25,"3":0.22,"4":0.20,"1":0.18,"5+":0.15},
    "55-64": {"1":0.30,"2":0.28,"3":0.18,"4":0.14,"5+":0.10},
    "65+":   {"1":0.45,"2":0.25,"3":0.15,"4":0.10,"5+":0.05},
}

FAMILY_INCOME_PROB = {
    # Low personal income → mostly low family income, occasional mid
    ("<3萬","學生"):{"<1萬":0.10,"1-3萬":0.60,"3-7萬":0.25,"7萬":0.04,"百萬":0.01},
    ("<3萬","退休"):{"<1萬":0.20,"1-3萬":0.50,"3-7萬":0.20,"7萬":0.08,"百萬":0.02},
    ("<3萬","服務"):{"<1萬":0.10,"1-3萬":0.50,"3-7萬":0.30,"7萬":0.08,"百萬":0.02},
    ("<3萬","製造"):{"<1萬":0.05,"1-3萬":0.40,"3-7萬":0.40,"7萬":0.12,"百萬":0.03},
    # Mid personal income → mostly mid family income, some high
    ("3-8萬","科技"):{"<1萬":0.10,"1-3萬":0.10,"3-7萬":0.40,"7萬":0.28,"百萬":0.12},
    ("3-8萬","金融"):{"<1萬":0.10,"1-3萬":0.10,"3-7萬":0.40,"7萬":0.28,"百萬":0.12},
    ("3-8萬","公務"):{"<1萬":0.05,"1-3萬":0.15,"3-7萬":0.50,"7萬":0.22,"百萬":0.08},
    ("3-8萬","教育"):{"<1萬":0.05,"1-3萬":0.15,"3-7萬":0.55,"7萬":0.18,"百萬":0.07},
    ("3-8萬","醫療"):{"<1萬":0.05,"1-3萬":0.10,"3-7萬":0.50,"7萬":0.25,"百萬":0.10},
    # High personal income → mostly high family income
    (">8萬","科技"):{"<1萬":0,"1-3萬":0.10,"3-7萬":0.30,"7萬":0.35,"百萬":0.25},
    (">8萬","金融"):{"<1萬":0,"1-3萬":0.10,"3-7萬":0.30,"7萬":0.35,"百萬":0.25},
    (">8萬","醫療"):{"<1萬":0,"1-3萬":0.10,"3-7萬":0.40,"7萬":0.30,"百萬":0.20},
    (">8萬","自營"):{"<1萬":0.05,"1-3萬":0.10,"3-7萬":0.35,"7萬":0.30,"百萬":0.20},
}

HOBBY_POOL = {
    "young":   {"打電動":0.20,"追劇":0.18,"球類":0.15,"閱讀":0.10,"登山":0.08,"逛街購物":0.08,"烹飪":0.05,"游泳":0.05,"音樂":0.05,"園藝":0.03,"打牌":0.01},
    "adult":   {"追劇":0.18,"登山":0.15,"閱讀":0.14,"球類":0.12,"逛街購物":0.10,"打電動":0.08,"園藝":0.07,"烹飪":0.06,"游泳":0.05,"泡茶":0.03,"打牌":0.01,"下棋":0.01},
    "senior_m":{"閱讀":0.18,"登山":0.15,"泡茶":0.14,"追劇":0.10,"園藝":0.09,"下棋":0.08,"球類":0.07,"打牌":0.06,"逛街購物":0.04,"烹飪":0.03,"打電動":0.03,"游泳":0.03},
    "senior_f":{"追劇":0.18,"閱讀":0.14,"園藝":0.12,"逛街購物":0.12,"登山":0.10,"泡茶":0.08,"烹飪":0.08,"打牌":0.06,"廣場舞":0.05,"球類":0.03,"下棋":0.02,"打電動":0.02},
    "kid":     {"打電動":0.25,"球類":0.20,"閱讀":0.12,"追劇":0.12,"繪畫":0.10,"登山":0.06,"逛街購物":0.05,"游泳":0.04,"烹飪":0.03,"園藝":0.02,"音樂":0.01},
}

# Marriage status by age
# Real marriage status distribution from MOI 2024 data
MARRIAGE_PROB = {
    "0-11":  {"未婚":1.0000, "已婚":0, "離婚":0, "鰥寡":0},
    "12-18": {"未婚":1.0000, "已婚":0, "離婚":0, "鰥寡":0},
    "19-24": {"未婚":0.9700, "已婚":0.0266, "離婚":0.0034, "鰥寡":0},
    "25-34": {"未婚":0.7456, "已婚":0.2392, "離婚":0.0088, "鰥寡":0.0064},
    "35-44": {"未婚":0.4238, "已婚":0.5466, "離婚":0.0102, "鰥寡":0.0194},
    "45-54": {"未婚":0.3243, "已婚":0.6250, "離婚":0.0063, "鰥寡":0.0444},
    "55-64": {"未婚":0.2319, "已婚":0.6967, "離婚":0.0030, "鰥寡":0.0684},
    "65+":   {"未婚":0.2237, "已婚":0.5875, "離婚":0.0009, "鰥寡":0.1878},
}
MARRIAGE_PROB_MALE = {
    "0-11":  {"未婚":1.0000, "已婚":0, "離婚":0, "鰥寡":0},
    "12-18": {"未婚":1.0000, "已婚":0, "離婚":0, "鰥寡":0},
    "19-24": {"未婚":0.9791, "已婚":0.0186, "離婚":0.0023, "鰥寡":0},
    "25-34": {"未婚":0.7886, "已婚":0.2004, "離婚":0.0074, "鰥寡":0.0036},
    "35-44": {"未婚":0.4628, "已婚":0.5157, "離婚":0.0097, "鰥寡":0.0118},
    "45-54": {"未婚":0.3533, "已婚":0.6171, "離婚":0.0070, "鰥寡":0.0226},
    "55-64": {"未婚":0.2269, "已婚":0.7372, "離婚":0.0038, "鰥寡":0.0321},
    "65+":   {"未婚":0.1954, "已婚":0.7543, "離婚":0.0014, "鰥寡":0.0489},
}
MARRIAGE_PROB_FEMALE = {
    "0-11":  {"未婚":1.0000, "已婚":0, "離婚":0, "鰥寡":0},
    "12-18": {"未婚":1.0000, "已婚":0, "離婚":0, "鰥寡":0},
    "19-24": {"未婚":0.9601, "已婚":0.0353, "離婚":0.0047, "鰥寡":0},
    "25-34": {"未婚":0.6996, "已婚":0.2808, "離婚":0.0102, "鰥寡":0.0094},
    "35-44": {"未婚":0.3848, "已婚":0.5775, "離婚":0.0107, "鰥寡":0.0271},
    "45-54": {"未婚":0.2967, "已婚":0.6325, "離婚":0.0057, "鰥寡":0.0651},
    "55-64": {"未婚":0.2366, "已婚":0.6588, "離婚":0.0022, "鰥寡":0.1023},
    "65+":   {"未婚":0.2469, "已婚":0.4507, "離婚":0.0005, "鰥寡":0.3018},
}

def pick_hobbies(age, sex, occ):
    if age in ("0-11",): pool = HOBBY_POOL["kid"]
    elif age in ("12-18",): pool = HOBBY_POOL["young"]
    elif age in ("19-24","25-34"): pool = HOBBY_POOL["young"]
    elif age in ("35-44","45-54"): pool = HOBBY_POOL["adult"]
    elif age in ("55-64",):
        pool = HOBBY_POOL["senior_m"] if sex == "男" else HOBBY_POOL["senior_f"]
    else:
        pool = HOBBY_POOL["senior_m"] if sex == "男" else HOBBY_POOL["senior_f"]
    
    ks, vs = zip(*pool.items())
    count = random.randint(2, 3)
    chosen = set()
    for _ in range(count * 2):  # ample tries
        h = random.choices(ks, weights=vs, k=1)[0]
        chosen.add(h)
        if len(chosen) >= count:
            break
    # Adjust for occ
    if occ in ("科技","工程") and "打電動" not in chosen and random.random() < 0.4:
        chosen.add("打電動")
    if occ in ("教育","醫療") and "閱讀" not in chosen and random.random() < 0.3:
        chosen.add("閱讀")
    return list(chosen)[:count]

POL_PROB = {
    "都會區(六都)": {"泛綠":0.32,"泛藍":0.30,"無政治傾向":0.25,"白/第三勢力":0.13},
    "北部":         {"泛藍":0.32,"無政治傾向":0.30,"泛綠":0.25,"白/第三勢力":0.13},
    "中部":         {"泛藍":0.30,"泛綠":0.28,"無政治傾向":0.30,"白/第三勢力":0.12},
    "南部":         {"泛綠":0.38,"無政治傾向":0.30,"泛藍":0.22,"白/第三勢力":0.10},
    "花東":         {"泛藍":0.35,"無政治傾向":0.35,"泛綠":0.20,"白/第三勢力":0.10},
    "離島":         {"泛藍":0.40,"無政治傾向":0.35,"泛綠":0.15,"白/第三勢力":0.10},
}

# ── 戶籍地 (registered residence) mapping: region → list of cities/counties ──
REGION_TO_CITIES = {
    "都會區(六都)": ["台北市","新北市","桃園市","台中市","台南市","高雄市"],
    "北部": ["基隆市","新竹縣","新竹市","苗栗縣","宜蘭縣"],
    "中部": ["彰化縣","南投縣","雲林縣"],
    "南部": ["嘉義市","嘉義縣","屏東縣"],
    "花東": ["花蓮縣","台東縣"],
    "離島": ["澎湖縣","金門縣","連江縣"],
}

# ── 家戶所得分級 based on residence (2024主計總處) ──
# 調整 FAMILY_INCOME_PROB 的選取機率
HH_INCOME_TIER = {
    "新竹縣": "極高", "新竹市": "極高", "台北市": "極高",
    "桃園市": "高", "新北市": "高", "嘉義市": "高", "台中市": "高",
    "高雄市": "中", "基隆市": "中", "台南市": "中", "宜蘭縣": "中",
    "屏東縣": "中低", "苗栗縣": "中低", "花蓮縣": "中低",
    "嘉義縣": "中低", "南投縣": "中低", "雲林縣": "中低",
    "彰化縣": "中低", "金門縣": "中低",
    "台東縣": "低", "連江縣": "低", "澎湖縣": "低",
}

def adjust_family_income_by_tier(base_fam_inc, hh_tier):
    """Shift family_income probability based on city household income level."""
    shifts = {
        "極高": {"<1萬":("1-3萬",0.5),"1-3萬":("3-7萬",0.4)},
        "高":   {"<1萬":("1-3萬",0.3),"1-3萬":("3-7萬",0.2)},
        "中":   {},
        "中低": {"百萬":("7萬",0.3),"7萬":("3-7萬",0.2)},
        "低":   {"百萬":("3-7萬",0.4),"7萬":("3-7萬",0.3),"3-7萬":("1-3萬",0.15)},
    }
    adjustments = shifts.get(hh_tier, {})
    if base_fam_inc in adjustments:
        target, prob = adjustments[base_fam_inc]
        if random.random() < prob:
            return target
    return base_fam_inc

# ── 物價分級 (平均每人月消費支出, 113年度主計總處) ──
# 高(>112%), 中高(102-112%), 中(90-102%), 低(80-90%), 極低(<80%)
PRICE_TIER = {
    "台北市": "高", "新竹縣": "高",
    "新竹市": "中高", "台中市": "中高", "新北市": "中高", "嘉義市": "中高",
    "高雄市": "中", "桃園市": "中", "基隆市": "中",
    "宜蘭縣": "低", "台南市": "低", "屏東縣": "低", "苗栗縣": "低",
    "花蓮縣": "低", "嘉義縣": "低",
    "金門縣": "極低", "雲林縣": "極低", "彰化縣": "極低",
    "澎湖縣": "極低", "連江縣": "極低", "台東縣": "極低", "南投縣": "極低",
}

MEDIA_PROB = {
    "0-11":{"家長主導":0.55,"兒童內容為主":0.30,"混合":0.10,"傳統媒體為主":0.05},
    "12-18":{"社群為主":0.7,"混合":0.25,"傳統媒體為主":0.05},
    "19-24":{"社群為主":0.6,"混合":0.3,"傳統媒體為主":0.05,"國際來源":0.05},
    "25-34":{"社群為主":0.45,"混合":0.35,"傳統媒體為主":0.1,"國際來源":0.1},
    "35-44":{"混合":0.4,"社群為主":0.35,"傳統媒體為主":0.2,"國際來源":0.05},
    "45-54":{"混合":0.35,"傳統媒體為主":0.35,"社群為主":0.25,"國際來源":0.05},
    "55-64":{"傳統媒體為主":0.5,"混合":0.3,"社群為主":0.15,"國際來源":0.05},
    "65+":   {"傳統媒體為主":0.7,"混合":0.2,"社群為主":0.1},
}

# Political stance enrichment — adds credibility signals per leaning
POLITICAL_STANCES = {
    "泛綠": {"stances": ["支持最近的大罷免行動，認為這是民主機制","認同執政黨的整體路線，反對在野黨杯葛","關注社會正義議題，認同轉型正義方向","對藍白合作持反對態度，認為是政治分贓","支持台灣主權立場，關注國防自主"],"issues": ["大罷免","轉型正義","國防自主","社會福利"]},
    "泛藍": {"stances": ["反對大罷免，認為浪費社會資源","支持藍白合作，認為這是制衡執政黨","批評執政黨施政，關注經濟和兩岸","認為在野黨應該團結","關注兩岸和平交流"],"issues": ["藍白合作","兩岸交流","經濟民生","反對大罷免"]},
    "白/第三勢力": {"stances": ["認為柯文哲案是政治迫害，司法被政治干預","雖然柯文哲有爭議，但司法程序應公正透明","厭惡藍綠惡鬥，支持第三勢力制衡","關注司法獨立和程序正義","認為台灣需要超越藍綠的第三條路"],"issues": ["柯文哲案","司法獨立","第三勢力","超越藍綠"]},
    "無政治傾向": {"stances": ["對政治沒什麼興趣，誰執政生活都差不多","藍綠都一樣爛，不想浪費時間關注","只看政績不看黨派，誰做得好就支持誰","政治離生活太遠，比較在意物價和薪水","覺得新聞都在亂報，不如不要看"],"issues": ["民生","物價","無感"]},
}

# Occupation-grouped stances — more specific than generic leaning stances
# Key: (politics, occ_group) where occ_group maps from actual occupation
# Uses income & age context for finer targeting
OCC_GROUP_MAP = {
    "科技":"科技金融", "金融":"科技金融",
    "醫療":"專業", "教育":"專業", "公務":"專業",
    "服務":"服務",
    "製造":"勞動",
    "自營":"自營",
    "學生":"學生",
    "退休":"退休家管", "家管":"退休家管",
    "其他":"其他",
}

POLITICAL_STANCES_CROSS = {
    # ── 泛綠 ──
    ("泛綠","科技金融"): [
        "支持國防自主和半導體供應鏈本土化，關注產業競爭力",
        "重視台灣在全球供應鏈的角色，支持產業升級",
        "對關鍵技術自主有切身感受，支持科技研發投資",
    ],
    ("泛綠","專業"): [
        "關心醫療/教育資源分配，支持社會福利擴張",
        "認同轉型正義方向，關注制度改革",
        "支持政府對公共服務的投資和改革",
    ],
    ("泛綠","服務"): [
        "支持大罷免，希望改善低薪問題和勞動權益",
        "認為基本工資應該再提高，服務業很辛苦",
    ],
    ("泛綠","勞動"): [
        "關注製造業轉型和就業機會，擔心產業外移",
        "希望政府對傳統產業有更多補助和輔導",
    ],
    ("泛綠","自營"): [
        "支持本土產業發展，希望稅制和法規更友善",
        "關注中小企業的生存空間，希望政府簡化行政流程",
    ],
    ("泛綠","學生"): [
        "關注居住正義和學貸問題，支持教育改革",
        "支持台灣主權立場，但更擔心兵役和未來發展",
    ],
    ("泛綠","退休家管"): [
        "關心長照政策和退休金制度改革",
        "支持社會福利，但擔心政府財政能否負擔",
    ],
    # ── 泛藍 ──
    ("泛藍","科技金融"): [
        "關注兩岸經貿穩定和產業供應鏈韌性",
        "批評政府能源政策，擔心產業競爭力受影響",
    ],
    ("泛藍","專業"): [
        "反對年金改革，認為政府違背對公務人員的承諾",
        "批評執政黨的治理能力，關注行政效率",
    ],
    ("泛藍","服務"): [
        "批評執政黨施政，覺得物價一直漲但薪水沒漲",
        "支持藍白合作，希望制衡一黨獨大",
    ],
    ("泛藍","勞動"): [
        "擔心中美貿易戰對傳產的衝擊，希望兩岸關係緩和",
        "批評政府能源轉型政策，擔心電價上漲影響生計",
    ],
    ("泛藍","自營"): [
        "希望兩岸關係緩和，促進經貿交流和觀光",
        "批評政府施政影響做生意，支持政黨輪替",
    ],
    ("泛藍","學生"): [
        "關注兩岸和平和兵役制度改革",
        "認為政府應該專注經濟民生，不要搞意識形態",
    ],
    ("泛藍","退休家管"): [
        "維護退休金權益，反對政府砍福利",
        "批評政府施政，認為以前比較好",
    ],
    # ── 白/第三勢力 ──
    ("白/第三勢力","科技金融"): [
        "關注司法改革和財政紀律，支持公開透明",
        "厭惡藍綠惡鬥，認為台灣需要專業導向政治",
    ],
    ("白/第三勢力","專業"): [
        "支持超越藍綠，關注制度和程序正義",
        "認為柯文哲案凸顯司法獨立的重要性",
    ],
    ("白/第三勢力","服務"): [
        "厭惡藍綠惡鬥，支持第三勢力制衡",
        "覺得藍綠都在分贓，需要第三條路",
    ],
    ("白/第三勢力","勞動"): [
        "對藍綠都沒信心，支持經濟民生優先",
        "厭倦政治惡鬥，誰做得好就支持誰",
    ],
    ("白/第三勢力","自營"): [
        "希望政府效率提升、簡化行政流程",
        "支持財政紀律和公開透明的政府",
    ],
    ("白/第三勢力","學生"): [
        "支持超越藍綠，關注居住正義和學貸",
        "認為台灣需要打破藍綠壟斷的政治結構",
    ],
    ("白/第三勢力","退休家管"): [
        "認為柯文哲案是政治迫害，司法被政治干預",
        "關心司法獨立和程序正義",
    ],
}

# Income-aware stance enrichment for high-income contexts
HIGH_INCOME_STANCES = {
    "泛綠": "關注產業競爭力，支持投資人才和研發",
    "泛藍": "關心稅制和經濟政策，希望政府減少干預",
    "白/第三勢力": "支持財政紀律和經濟自由化",
}

LOW_INCOME_STANCES = {
    "泛綠": "希望改善低薪問題和社會安全網",
    "泛藍": "批評物價飛漲，生活越來越難過",
    "白/第三勢力": "關心社會福利和居住正義",
}

def wchoice(opts):
    ks, vs = zip(*opts.items())
    return random.choices(ks, weights=vs, k=1)[0]

# ═══ 3. NAME GENERATORS (per-combo cycling pool) ═══

def _build_name_pool(age, sex, occ):
    """Build the shuffled name pool for a given (age, sex, occ) combo.
    Each pool has ~16 names to ensure cycling diversity for high-count combos."""
    if age == "0-11":
        pool = ["糖糖","果果","樂樂","星星","蜜蜜","嘟嘟","妮妮","寶寶",
                "可可","芽芽","米米","豆豆","萌萌","天天","亮亮","晴晴"]
    elif age == "12-18":
        pool = ["小莓","星醬","芽泉","糖球","小雲","夢醬","莓果","星月",
                "小桃","蜜糖","泡泡","小葵","雨醬","熙熙","芯芯","學妹"]
    elif age == "65+":
        if sex == "男":
            pool = ["春伯","福伯","金伯","天伯","榮伯","有伯","萬伯","土伯","坤伯",
                    "松伯","柏伯","柳伯","茂伯","竹伯","梅伯"]
        else:
            pool = ["春姨","麗媽","秀姨","阿好嬸","金花嬸","素蘭嬸","阿桃","阿滿","阿鳳",
                    "銀嬸","玉嬸","碧嬸","月嬸","秀嬸","鳳嬸"]
    elif age in ("55-64",):
        if sex == "男":
            pool = ["信宏","坤成","明德","永昌","國華","耀宗","萬生","進福",
                    "清輝","德勝","添財","榮發","金水","木火","朝陽"]
        else:
            pool = ["秀英","玉蘭","碧霞","玉琴","素雲","月鳳","金蓮","秀美",
                    "含笑","美雲","彩華","阿緞","玉葉","寶珠","秀琴"]
    elif (age == "19-24" and sex == "男") or (age == "25-34" and sex == "男"):
        if occ in ("科技","金融"):
            pool = ["阿睿","阿凱","馬克","大衛","文森","阿誠","小光","傑森",
                    "艾力克","理察","丹尼爾","班","傑","洛克","諾亞","歐文"]
        else:
            pool = ["小宇","小安","阿杰","阿豪","阿翔","小陳","阿元","阿明",
                    "小傑","小林","阿峰","阿緯","小白","阿宏","大雄","小胖"]
    elif (age == "19-24" and sex == "女") or (age == "25-34" and sex == "女"):
        pool = ["小艾","艾倫","莉亞","若希","安妮","凱琳","可恩","小曦",
                "愛莎","小莉","小薇","小彤","小奈","米亞","菲菲","柔伊"]
    elif age in ("35-44","45-54") and sex == "男":
        pool = ["志豪","大仁","建宏","強哥","文彬","明義","世昌","志強",
                "永信","俊傑","正雄","文龍","瑞宏","協明","福來","信賢"]
    elif age in ("35-44","45-54") and sex == "女":
        pool = ["靜怡","雅雯","慧君","美珍","素芬","麗卿","淑貞","惠如",
                "美惠","麗華","惠雯","麗美","淑娟","雅芳","怡君","婉玲"]
    else:
        pool = ["秀蘭","美惠","素卿","麗華","春梅","美枝","淑華","明輝",
                "俊傑","阿坤","阿利","萬福","春生","正男","水木","阿雪"]
    random.shuffle(pool)
    return pool

NAME_POOLS = {}  # key = (age, sex, occ) -> deque of names
def get_name(age, sex, occ):
    key = (age, sex, occ)
    if key not in NAME_POOLS:
        NAME_POOLS[key] = deque(_build_name_pool(age, sex, occ))
    pool = NAME_POOLS[key]
    name = pool.popleft()   # take from front
    pool.append(name)        # recycle to back — ensures cycling diversity
    return name

# ═══ 4. GENERATE ═══

personas = []
pid = 0
coherence_fixes = {"fam_inc_5plus": 0, "fam_inc_4": 0, "fam_inc_student_5plus": 0, "marriage_minor": 0, "marriage_student_divorce": 0, "edu_professional_bump": 0, "marriage_young_widowed": 0}

# ── Background story inference engine (phrase-pool diversified) ──

# Household composition phrase pools
HH_SINGLE_UNMARRIED = ["自己一個人住", "一個人租套房", "享受單身生活"]
HH_SINGLE_MARRIED = [
    "配偶在外地工作，自己一個人住",
    "夫妻分居兩地，週末才見面",
    "配偶長期在國外，一人獨居",
    "新婚但暫時分居，等房子處理好",
]
HH_SINGLE_MARRIED_SENIOR = [
    "配偶在外地工作，自己一個人住",
    "夫妻分居兩地，週末才見面",
    "配偶長期在國外，一人獨居",
    "孩子在外地，夫妻兩人生活",
]
HH_SINGLE_DIVORCED = ["離婚後一個人住", "恢復單身，自己租房子"]
HH_SINGLE_WIDOWED = ["老伴走了，現在獨居", "一個人過日子", "子女都在外地，自己住"]
HH_SINGLE_PARENT = ["跟媽媽同住，是單親家庭", "由媽媽一手帶大，母子兩人", "跟爸爸同住"]
HH_WITH_PARENT_CHILD = ["輪流跟爸爸或媽媽住（爸媽離婚）"]
HH_CARING_ELDERLY = ["跟年邁的父母同住，單身照顧長輩", "為了照顧爸媽，選擇住家裡"]
HH_COUPLE_ONLY = ["夫妻兩人世界", "結婚後沒有生小孩的打算"]
HH_COUPLE_NEWLYWED = ["新婚不久，享受兩人生活", "結婚後沒有生小孩的打算", "夫妻兩人世界"]
HH_DIVORCED_WITH_CHILD_MALE = ["離婚後自己帶一個孩子", "單親爸爸，小孩還小"]
HH_DIVORCED_WITH_CHILD_FEMALE = ["離婚後自己帶一個孩子", "單親媽媽，小孩還小"]
HH_FAM3_MARRIED = ["小家庭，夫妻加一個孩子", "一家三口，日子簡單"]
HH_FAM3_UNMARRIED_MALE = ["跟父母同住，是家裡唯一的孩子", "獨生子，爸媽的寶"]
HH_FAM3_UNMARRIED_FEMALE = ["跟父母同住，是家裡唯一的孩子", "獨生女，爸媽的寶"]
HH_FAM3_ELDERLY_UNMARRIED = ["一個人在家，簡單過日子", "小孩都在外地，自己一個人住"]
HH_FAM4_MARRIED = ["典型小家庭，夫妻加兩個孩子", "兩個小孩正值最花錢的年紀"]
HH_FAM4_UNMARRIED = [
    "跟爸爸媽媽和一個弟弟住",
    "跟爸爸媽媽和一個妹妹住",
    "跟爸爸媽媽和一個哥哥住",
    "跟爸爸媽媽和一個姊姊住",
    "跟爸爸媽媽和阿公住",
    "跟爸爸媽媽和阿嬤住",
]
HH_FAM4_UNMARRIED_SENIOR = [
    "跟兄弟姊妹同住，互相照顧",
    "和家人一起住，互相照應",
    "跟親人同住，生活有個伴",
]
HH_FAM5_STUDENT = [
    "在家裡排行老大，底下有弟弟妹妹",
    "是家裡的老大，要幫忙照顧弟弟妹妹",
    "是家裡的老么，上面有哥哥",
    "是家裡的老么，上面有姊姊",
    "在家裡排行中間，上有兄姐下有弟妹",
]
HH_FAM5_UNMARRIED = ["與父母和多位兄弟姊妹同住", "家裡熱鬧，但房間不夠用"]
HH_FAM5_UNMARRIED_SENIOR = ["和兄弟姊妹同住，家裡熱鬧", "和家人同住，互相有個照應"]
HH_FAM5_MARRIED = ["大家庭，夫妻加三個以上的孩子", "兒女成群，家裡很熱鬧"]
HH_FAM5_WIDOWED_SENIOR = ["兒孫滿堂，與子女和孫輩同住", "三代同堂，家裡很熱鬧"]
HH_FAM5_WIDOWED_YOUNG = ["大家庭，與家人同住", "和父母及兄弟姊妹同住"]
HH_MISSING_FALLBACK = ["簡單過日子", "生活樸實", "過著平穩的日子"]

# Young divorced — not the same as elderly widowed
HH_YOUNG_DIVORCED_MALE = [
    "離婚後搬回老家住",
    "離婚後跟家人同住",
    "婚姻很短暫，現在恢復單身",
    "離婚後搬出去自己住",
]
HH_YOUNG_DIVORCED_FEMALE = [
    "離婚後搬回娘家住",
    "離婚後跟家人同住",
    "婚姻很短暫，現在恢復單身",
    "離婚後回學校繼續進修",
]

# Economic situation phrase pools
ECON_TIGHT_BIGFAM = [
    "經濟上要很精打細算",
    "每一塊錢都要算清楚",
    "月底常常手頭緊",
    "買東西都要先比價",
    "伙食費佔了開銷的大半",
    "能省則省，不太敢亂花錢",
    "小孩的開銷很大，存不了什麼錢",
    "最近物價漲得很有感，日子更緊了",
]
ECON_STRESSED = [
    "經濟壓力非常大",
    "常常入不敷出",
    "貸款和帳單壓得喘不過氣",
    "房租佔掉收入快一半",
]
ECON_COMFORTABLE = [
    "經濟上滿寬裕的",
    "有些積蓄，偶爾會出國玩",
    "手頭還算寬鬆，不用太省",
    "生活品質還不錯，該花的會花",
]
ECON_STUDENT_WORK = [
    "有時需要打工貼補家用",
    "課餘時間在超商打工",
    "靠助學貸款和打工撐生活費",
]

# Life stage phrase pools
LIFE_PRIMARY = ["還在唸小學", "每天放學就是寫作業和看卡通"]
LIFE_MIDDLE = ["正在唸中學", "每天補習到很晚"]
LIFE_UNI = ["正在讀大學", "大學生活就是上課和玩"]
LIFE_FRESH = ["剛出社會不久", "還在摸索職涯方向"]
LIFE_CAREER = [
    "正在事業打拚期",
    "每天加班到八九點是日常",
    "為了升遷，這幾年特別拚",
    "工作壓力大但成就感也大",
]
LIFE_MID30S = [
    "上有老下有小，是家庭支柱",
    "正是扛家計的年紀，不敢輕易換工作",
    "最近開始注重養生和體檢",
    "小孩的教育費是最大開銷",
    "工作和家庭兩頭燒",
    "開始考慮要不要買房",
]
LIFE_MID40S = [
    "工作量趨於穩定，開始思考退休規劃",
    "職場老鳥了，開始交棒給年輕人",
    "身體開始有些小毛病，開始注意健康",
    "小孩慢慢大了，稍微輕鬆一點",
    "開始想退休後要做什麼",
    "職位不上不下，有點尷尬但穩定",
]
LIFE_FRESH_RETIRED = [
    "剛退休，還在適應慢生活",
    "退休後每天早上都去公園",
    "退休後開始學一些以前沒時間做的事",
]
LIFE_PRE_RETIRE = [
    "快退休了，心態上開始調整",
    "剩沒幾年就退休，開始交接工作",
    "年紀到了，開始想退休後的生活",
]
LIFE_SENIOR_WIDOWED = [
    "現在一個人過日子",
    "老伴走了，孩子也都成年了",
]
LIFE_SENIOR_WIDOWED_FAMILY = [
    "老伴走了，現在跟孩子住",
    "老伴走了，跟家人一起住",
    "老伴不在了，有家人陪伴",
]
LIFE_SENIOR = [
    "退休生活，含飴弄孫",
    "退休後每天種花散步",
    "早上公園運動，下午找朋友聊天",
]

def infer_background(age, sex, marriage, occ, fam, fam_inc, region, inc, price_tier):
    parts = []
    # Household composition
    if fam == "1" and marriage == "未婚": parts.append(random.choice(HH_SINGLE_UNMARRIED))
    elif fam == "1" and marriage == "已婚":
        pool = HH_SINGLE_MARRIED_SENIOR if age in ("55-64","65+") else HH_SINGLE_MARRIED
        parts.append(random.choice(pool))
    elif fam == "1" and marriage == "離婚": parts.append(random.choice(HH_SINGLE_DIVORCED))
    elif fam == "1" and marriage == "鰥寡": parts.append(random.choice(HH_SINGLE_WIDOWED))
    elif fam == "2" and marriage == "未婚" and age in ("19-24","25-34"): parts.append(random.choice(HH_SINGLE_PARENT))
    elif fam == "2" and marriage == "未婚" and age in ("0-11","12-18"): parts.append(random.choice(HH_WITH_PARENT_CHILD))
    elif fam == "2" and marriage == "未婚" and age in ("35-44",): parts.append(random.choice(HH_CARING_ELDERLY))
    elif fam == "2" and marriage == "已婚" and age in ("19-24","25-34","35-44"): parts.append(random.choice(HH_COUPLE_NEWLYWED))
    elif fam == "2" and marriage == "已婚": parts.append(random.choice(HH_COUPLE_ONLY))
    elif fam == "2" and marriage == "離婚":
        pool = HH_DIVORCED_WITH_CHILD_MALE if sex == "男" else HH_DIVORCED_WITH_CHILD_FEMALE
        parts.append(random.choice(pool))
    elif fam == "3" and marriage == "已婚": parts.append(random.choice(HH_FAM3_MARRIED))
    elif fam == "3" and marriage == "未婚":
        pool = HH_FAM3_ELDERLY_UNMARRIED if age in ("55-64","65+") else (HH_FAM3_UNMARRIED_MALE if sex == "男" else HH_FAM3_UNMARRIED_FEMALE)
        parts.append(random.choice(pool))
    elif fam == "4" and marriage == "已婚": parts.append(random.choice(HH_FAM4_MARRIED))
    elif fam == "4" and marriage == "未婚":
        pool = HH_FAM4_UNMARRIED_SENIOR if age in ("45-54","55-64","65+") else HH_FAM4_UNMARRIED
        parts.append(random.choice(pool))
    elif fam == "5+" and marriage == "未婚" and occ == "學生": parts.append(random.choice(HH_FAM5_STUDENT))
    elif fam == "5+" and marriage == "未婚":
        pool = HH_FAM5_UNMARRIED_SENIOR if age in ("45-54","55-64","65+") else HH_FAM5_UNMARRIED
        parts.append(random.choice(pool))
    elif fam == "5+" and marriage == "已婚": parts.append(random.choice(HH_FAM5_MARRIED))
    elif age in ("19-24","25-34") and marriage == "離婚" and fam in ("3","4","5+"):
        pool = HH_YOUNG_DIVORCED_MALE if sex == "男" else HH_YOUNG_DIVORCED_FEMALE
        parts.append(random.choice(pool))
    elif fam == "5+" and marriage in ("離婚","鰥寡"):
        pool = HH_FAM5_WIDOWED_SENIOR if age in ("55-64","65+") else HH_FAM5_WIDOWED_YOUNG
        parts.append(random.choice(pool))
    # Fallback if no household branch matched
    if not parts:
        parts.append(random.choice(HH_MISSING_FALLBACK))
    # Economic situation (skip for children — a kid doesn't worry about household budget)
    def econ_by_tier(tight_pool, stressed_pool, comfy_pool, tier, inc_level="3-8萬"):
        """Select economic phrase weighted by local price level + income."""
        base_w = {
            "高":   {"tight": 0.70, "stressed": 0.25, "comfy": 0.05},
            "中高": {"tight": 0.55, "stressed": 0.20, "comfy": 0.25},
            "中":   {"tight": 0.40, "stressed": 0.15, "comfy": 0.45},
            "低":   {"tight": 0.25, "stressed": 0.10, "comfy": 0.65},
            "極低": {"tight": 0.15, "stressed": 0.05, "comfy": 0.80},
        }.get(tier, {"tight": 0.40, "stressed": 0.15, "comfy": 0.45})
        # Income bias: <3萬 → tighter, >8萬 → looser
        if inc_level == "<3萬":
            base_w["tight"] += 0.20
            base_w["comfy"] = max(0, base_w["comfy"] - 0.20)
        elif inc_level == ">8萬":
            base_w["comfy"] += 0.15
            base_w["tight"] = max(0, base_w["tight"] - 0.15)
        # Renormalize
        total = sum(base_w.values())
        w = {k: v/total for k, v in base_w.items()}
        pool_map = {"tight": tight_pool, "stressed": stressed_pool, "comfy": comfy_pool}
        choice = random.choices(list(w.keys()), weights=list(w.values()), k=1)[0]
        return random.choice(pool_map[choice])
    
    if age not in ("0-11","12-18"):
        if fam in ("4","5+") and fam_inc in ("1-3萬","3-7萬"):
            parts.append(econ_by_tier(ECON_TIGHT_BIGFAM, ECON_STRESSED, ECON_COMFORTABLE, price_tier, inc))
        elif fam in ("4","5+") and fam_inc == "<1萬":
            parts.append(econ_by_tier(ECON_STRESSED, ECON_TIGHT_BIGFAM, ECON_TIGHT_BIGFAM, price_tier, inc))
        elif fam in ("1","2") and fam_inc in ("7萬","百萬"):
            parts.append(econ_by_tier(ECON_COMFORTABLE, ECON_COMFORTABLE, ECON_COMFORTABLE, price_tier, inc))
        elif occ == "學生" and fam == "5+":
            parts.append(random.choice(ECON_STUDENT_WORK))
        else:
            # No specific branch matched — add generic economic phrase if adult
            parts.append(econ_by_tier(ECON_TIGHT_BIGFAM, ECON_STRESSED, ECON_COMFORTABLE, price_tier, inc))
    # Life stage
    if age == "0-11": parts.append(random.choice(LIFE_PRIMARY))
    elif age == "12-18": parts.append(random.choice(LIFE_MIDDLE))
    elif age == "19-24" and occ == "學生": parts.append(random.choice(LIFE_UNI))
    elif age == "19-24" and occ != "學生": parts.append(random.choice(LIFE_FRESH))
    elif age == "25-34" and occ not in ("退休","學生"): parts.append(random.choice(LIFE_CAREER))
    elif age == "35-44": parts.append(random.choice(LIFE_MID30S))
    elif age == "45-54": parts.append(random.choice(LIFE_MID40S))
    elif age == "55-64" and occ == "退休": parts.append(random.choice(LIFE_FRESH_RETIRED))
    elif age == "55-64": parts.append(random.choice(LIFE_PRE_RETIRE))
    elif age == "65+" and marriage == "鰥寡":
        pool = LIFE_SENIOR_WIDOWED_FAMILY if fam not in ("1",) else LIFE_SENIOR_WIDOWED
        parts.append(random.choice(pool))
    elif age == "65+": parts.append(random.choice(LIFE_SENIOR))
    # Region
    region_map = {
        "都會區(六都)": "住在都會區",
        "北部": "住在北部",
        "中部": "住在中部",
        "南部": "住在南部",
        "花東": "住在東部",
        "離島": "住在離島",
    }
    parts.append(region_map.get(region, "住在台灣"))
    return "。".join(parts) + "。"

for region, age, sex, weight, count in weighted:
    for _ in range(count):
        edu = wchoice(EDU_PROB.get(age, {"大學":1}))
        occ = wchoice(OCC_PROB.get((age, sex), {"其他":1}))
        # ── City-based occupation adjustment (竹科/金融/製造) ──
        OCC_CITY_BOOST = {
            "新竹縣": {"科技": 0.30}, "新竹市": {"科技": 0.30},
            "台北市": {"金融": 0.20},
            "桃園市": {"製造": 0.20},
            "台中市": {"製造": 0.15}, "台南市": {"製造": 0.15}, "高雄市": {"製造": 0.15},
        }
        if age not in ("0-11","12-18","65+") and occ not in ("學生","退休"):
            boosts = OCC_CITY_BOOST.get(residence, {})
            for target, prob in boosts.items():
                if occ != target and random.random() < prob:
                    occ = target
                    break
        inc = wchoice(INC_PROB.get(occ if occ in INC_PROB else "其他", {"<3萬":1}))
        pol = "無政治傾向" if age in ("0-11","12-18") else wchoice(POL_PROB.get(region, POL_PROB["都會區(六都)"]))
        med = wchoice(MEDIA_PROB.get(age, {"混合":1}))
        fam = wchoice(FAMILY_SIZE_PROB.get(age, {"3":1}))
        fam_inc = wchoice(FAMILY_INCOME_PROB.get((inc, occ) if (inc, occ) in FAMILY_INCOME_PROB else ("3-8萬", "服務"), {"3-7萬":1}))
        hobbies = pick_hobbies(age, sex, occ)
        marriage = wchoice(MARRIAGE_PROB_MALE.get(age, {"未婚":1})) if sex == "男" else wchoice(MARRIAGE_PROB_FEMALE.get(age, {"未婚":1}))
        # ── 戶籍地 (registered residence) within region ──
        residence = random.choice(REGION_TO_CITIES.get(region, ["其他"]))
        # ── 物價分級 based on residence ──
        price_tier = PRICE_TIER.get(residence, "中")
        # ── 家戶所得分級 based on residence ──
        hh_income_tier = HH_INCOME_TIER.get(residence, "中")
        
        # ── Coherence validation ──
        if fam == "5+" and fam_inc in ("<1萬", "1-3萬"):
            fam_inc = wchoice({"3-7萬":0.45, "7萬":0.35, "百萬":0.20})
            coherence_fixes["fam_inc_5plus"] += 1
        if fam == "4" and fam_inc == "<1萬":
            fam_inc = wchoice({"1-3萬":0.30, "3-7萬":0.40, "7萬":0.20, "百萬":0.10})
            coherence_fixes["fam_inc_4"] += 1
        if occ == "學生" and fam == "5+" and fam_inc in ("<1萬", "1-3萬"):
            fam_inc = wchoice({"3-7萬":0.40, "7萬":0.35, "百萬":0.25})
            coherence_fixes["fam_inc_student_5plus"] += 1
        if marriage == "已婚" and age in ("0-11","12-18"):
            marriage = "未婚"
            coherence_fixes["marriage_minor"] += 1
        if marriage == "已婚" and occ == "學生" and age in ("19-24",):
            marriage = "未婚"
            coherence_fixes["marriage_student_married"] = coherence_fixes.get("marriage_student_married", 0) + 1
        if marriage == "離婚" and occ == "學生" and age in ("19-24",):
            marriage = "未婚"
            coherence_fixes["marriage_student_divorce"] += 1
        if marriage == "鰥寡" and age in ("19-24","25-34"):
            marriage = "離婚" if random.random() < 0.7 else "未婚"
            coherence_fixes["marriage_young_widowed"] += 1
        if edu in ("國中以下","高中") and occ in ("科技","金融","醫療") and age in ("35-44","45-54","55-64"):
            edu = "大學"
            coherence_fixes["edu_professional_bump"] += 1
        # ── Adjust family_income by city household income level ──
        fam_inc = adjust_family_income_by_tier(fam_inc, hh_income_tier)
        
        name = get_name(age, sex, occ)
        
        # ── Political stance enrichment (occupation/income cross-referenced) ──
        pol_stance = ""
        pol_issues = []
        if pol in POLITICAL_STANCES and age not in ("0-11","12-18"):
            occ_group = OCC_GROUP_MAP.get(occ, "其他")
            cross_key = (pol, occ_group)
            if cross_key in POLITICAL_STANCES_CROSS:
                pol_stance = random.choice(POLITICAL_STANCES_CROSS[cross_key])
            else:
                pol_stance = random.choice(POLITICAL_STANCES[pol]["stances"])
            # 30% chance to enrich with income-aware stance
            if inc == ">8萬" and pol in HIGH_INCOME_STANCES and random.random() < 0.3:
                pol_stance = HIGH_INCOME_STANCES[pol]
            elif inc in ("<3萬","無收入") and pol in LOW_INCOME_STANCES and random.random() < 0.3:
                pol_stance = LOW_INCOME_STANCES[pol]
            pol_issues = random.sample(POLITICAL_STANCES[pol]["issues"], min(2, len(POLITICAL_STANCES[pol]["issues"])))
        
        # ── Background story inference ──
        story = infer_background(age, sex, marriage, occ, fam, fam_inc, region, inc, price_tier)
        # ── Story coherence: family>1 but "一個人過日子" ──
        single_phrases = ["現在一個人過日子", "一個人過日子"]
        if fam not in ("1",) and any(p in story for p in single_phrases):
            for p in single_phrases:
                if p in story:
                    story = story.replace(p, random.choice(["老伴走了，跟家人一起住", "老伴走了，有家人陪伴"]))
                    break
        
        # ── Story coherence: "含飴弄孫" conflicts with low income/高物價 ──
        if "含飴弄孫" in story and inc in ("<3萬",) and price_tier in ("高","中高","中"):
            story = story.replace("退休生活，含飴弄孫", "退休生活，簡單過日子")
            coherence_fixes["story_hantai_contra"] = coherence_fixes.get("story_hantai_contra", 0) + 1
        
        # ── Story coherence: no "小孩" in life stage when family_size = 1 ──
        if fam == "1" and "小孩" in story and "配偶" not in story and "夫妻" not in story:
            # Replace children-related life stage phrases
            replacements = {
                "小孩的開銷很大，存不了什麼錢": "一個人生活，開銷不大但存錢也不容易",
                "小孩的教育費是最大開銷": "生活開銷不算大，但存錢也不容易",
                "小孩慢慢大了，稍微輕鬆一點": "一個人生活，日子過得簡單",
            }
            for old_phrase, new_phrase in replacements.items():
                if old_phrase in story:
                    story = story.replace(old_phrase, new_phrase)
                    break
        if "沒有生小孩" in story and ("含飴弄孫" in story or "小孩" in story):
            # Regenerate with different life stage: pick a simpler one
            old_life = story.split("。")[-2] if "。" in story else story
            replacements = {
                "小孩的開銷很大，存不了什麼錢": "生活開銷不小，存不了什麼錢",
                "小孩的教育費是最大開銷": "生活費是最大開銷",
                "小孩慢慢大了，稍微輕鬆一點": "生活慢慢穩定下來，稍微輕鬆一點",
                "退休生活，含飴弄孫": "退休生活，兩人作伴",
            }
            for old_phrase, new_phrase in replacements.items():
                if old_phrase in story:
                    story = story.replace(old_phrase, new_phrase)
                    coherence_fixes["story_nochild_contra"] = coherence_fixes.get("story_nochild_contra", 0) + 1
                    break
        
        pid += 1
        hobby_text = "、".join(hobbies)
        stance_suffix = f"{pol_stance}。" if pol_stance else ""
        
        # ── Natural age descriptor for minors AND seniors ──
        def age_desc():
            if age == "0-11":
                return f"國小{'男' if sex=='男' else '女'}生"
            elif age == "12-18":
                return f"{random.choice(['國','高'])}中{'男' if sex=='男' else '女'}生"
            elif age == "65+":
                return f"{'阿伯' if sex=='男' else '阿姨'}"
            return None
        
        # ── Occupation-specific phrase for "做{occ}" templates ──
        def occ_phrase():
            mapping = {
                "退休": "已經退休了",
                "學生": "還在讀書",
                "家管": "在家照顧家庭",
                "公務": "當公務員",
                "自營": "自己做生意",
            }
            return mapping.get(occ, f"做{occ}")
        
        # ── Specific age from age bracket (e.g., "45-54" → 47) ──
        def specific_age():
            if age == "0-11": return str(random.randint(3, 11))
            elif age == "12-18": return str(random.randint(12, 18))
            elif age == "19-24": return str(random.randint(19, 24))
            elif age == "25-34": return str(random.randint(25, 34))
            elif age == "35-44": return str(random.randint(35, 44))
            elif age == "45-54": return str(random.randint(45, 54))
            elif age == "55-64": return str(random.randint(55, 64))
            else: return f"{random.randint(65, 78)}"  # 65+
        
        # ── Economic context sentence: income vs local cost of living ──
        def gen_econ_context():
            if age in ("0-11","12-18"):
                return ""
            # Effective income: personal first, family as proxy
            eff_inc = inc if inc not in (None, "無收入") else "無收入"
            # Low personal income but high family income -> family context
            if eff_inc in ("<3萬","無收入") and fam_inc in ("百萬","7萬"):
                if occ == "學生":
                    return f"家裏經濟不錯，但在{residence}開銷還是很大。" if price_tier in ("高","中高") else "家裏經濟還不錯，生活不用太擔心錢。"
                return f"家裏經濟還不錯，在{residence}生活還過得去。"
            if eff_inc == "無收入":
                if occ in ("學生","退休","家管"):
                    if fam_inc in ("7萬","百萬"): return "家裏經濟還不錯，不用擔心錢的問題。"
                    elif fam_inc in ("1-3萬","<1萬"): return "家裏經濟比較吃緊。"
                return ""
            if eff_inc == ">8萬":
                if price_tier in ("高","中高"): return f"在{residence}收入不錯，但物價高還是要算着花。"
                elif price_tier in ("低","極低"): return f"在{residence}收入算很高了，日子過得滿舒服的。"
                else: return f"在{residence}收入不錯，生活還算輕鬆。"
            if eff_inc == "3-8萬":
                if price_tier in ("高","中高"): return f"在{residence}這個收入不太夠用，物價太高了。"
                elif price_tier in ("低","極低"): return f"在{residence}這個收入還不錯，不用太省。"
                else: return f"在{residence}收入剛好夠生活。"
            # <3萬
            if price_tier in ("高","中高"): return f"在{residence}收入低，生活壓力很大。"
            return f"收入不高，在{residence}還是要省着點。"
        
        # ── 3 prompt_prefix template families        # ── 3 prompt_prefix template families (randomly assigned) ──
        # Strip trailing location from story to avoid redundancy with prefix
        def strip_trailing_location(s):
            # Remove "住在XX" or "住在XX生活圈" or "住在XX地區" from the end
            import re
            return re.sub(r"[。，]?住在[^.，]+$", "", s).rstrip("。")
        
        r = random.random()
        ad = age_desc()
        # Build a clean story without trailing location for use in prefix
        story_clean = strip_trailing_location(story)
        econ_ctx = gen_econ_context()
        
        if r < 0.40:
            # A: Third-person descriptive (40%)
            if ad and age == "65+":
                # Natural elderly intro: "這是碧嬸，72歲了，住花蓮縣。"
                age_sex_str = f"{name}，{specific_age()}歲了"
                prefix = (
                    f"這是{age_sex_str}，住{residence}。"
                    f"{story_clean}。"
                    f"平常喜歡{hobby_text}。"
                    f"{stance_suffix}"
                    f"{econ_ctx}"
                )
            else:
                age_sex_str = ad if ad else f"{specific_age()}歲的{sex}性"
                prefix = (
                    f"{name}是{age_sex_str}，住在{residence}。"
                    f"{story_clean}。"
                    f"平常喜歡{hobby_text}。"
                    f"{stance_suffix}"
                    f"{econ_ctx}"
                )
        elif r < 0.75:
            # B: First-person natural (35%)
            first_story = story_clean.split("。")[0] + "。" if "。" in story_clean else story_clean + "。"
            if ad and age == "65+":
                # Natural elderly first-person: "你們可以叫我碧嬸，72歲了，住花蓮縣。"
                prefix = (
                    f"你們可以叫我{name}，{specific_age()}歲了，住{residence}。"
                    f"{first_story}"
                    f"放假喜歡{hobby_text}。"
                    f"{stance_suffix}"
                    f"{econ_ctx}"
                )
            elif ad:
                prefix = (
                    f"我叫{name}，是{ad}，住{residence}。"
                    f"{first_story}"
                    f"放假喜歡{hobby_text}。"
                    f"{stance_suffix}"
                    f"{econ_ctx}"
                )
            else:
                prefix = (
                    f"我叫{name}，{specific_age()}歲，住{residence}，{occ_phrase()}。"
                    f"{first_story}"
                    f"放假喜歡{hobby_text}。"
                    f"{stance_suffix}"
                    f"{econ_ctx}"
                )
        else:
            # C: Concise natural (25%)
            first_story = story_clean.split("。")[0] if "。" in story_clean else story_clean
            if ad and age == "65+":
                prefix = (
                    f"我是{name}，{specific_age()}歲，住{residence}，{occ_phrase()}。"
                    f"{first_story}。"
                    f"興趣是{hobby_text}。{stance_suffix}"
                    f"{econ_ctx}"
                )
            else:
                prefix = (
                    f"我是{name}，{ad if ad else f'{specific_age()}歲'}，住在{residence}，{occ_phrase()}。"
                    f"{first_story}。"
                    f"興趣是{hobby_text}。{stance_suffix}"
                    f"{econ_ctx}"
                )
        
        ref = f"【{name}】{age}/{region}/{sex}/{marriage}/{occ}/{edu}/{fam}人/{fam_inc}/{','.join(hobbies)}"

        personas.append({
            "id": f"TW-P-{pid:04d}", "name": name,
            "type": "虛構人設",
            "note": "人口加權抽樣（14維度，含背景推論+政治補強）",
            "dimensions": {
                "age": age, "sex": sex, "region": region,
                "education": edu, "occupation": occ, "income": inc,
                "politics": pol, "media_diet": med,
                "family_size": fam, "family_income": fam_inc, "hobby": hobbies,
                "marriage": marriage, "political_stance": pol_stance,
                "political_issues": pol_issues, "background_story": story,
                "residence": residence,
                "price_tier": price_tier,
                "hh_income_tier": hh_income_tier
            },
            "reference_pre_prompt": ref,
            "prompt_prefix": prefix
        })

# ═══ 5. OUTPUT ═══

outpath = "/home/ubuntu/lab-riscv/hermesa3/persona/tw_persona_1069.json"
with open(outpath, "w") as f:
    json.dump(personas, f, ensure_ascii=False, indent=2)

ages = Counter(p["dimensions"]["age"] for p in personas)
regions = Counter(p["dimensions"]["region"] for p in personas)
sexes = Counter(p["dimensions"]["sex"] for p in personas)
residences = Counter(p["dimensions"]["residence"] for p in personas)

print(f"\n{'='*60}")
print(f"  1069 Personas — Complete Distribution")
print(f"{'='*60}")
print(f"\n  年齡分布:")
for k in ["0-11","12-18","19-24","25-34","35-44","45-54","55-64","65+"]:
    bar = "█" * max(1, ages[k]//5)
    print(f"    {k:<6s}: {ages[k]:>3d} {bar}")
print(f"\n  區域分布:")
for r in ["都會區(六都)","北部","中部","南部","花東","離島"]:
    bar = "█" * max(1, regions[r]//3)
    print(f"    {r:<10s}: {regions[r]:>3d} {bar}")
print(f"\n  性別: 男={sexes['男']}  女={sexes['女']}")
print(f"\n  戶籍地覆蓋: {len(residences)} 個縣市")
total_fixes = sum(coherence_fixes.values())
if total_fixes > 0:
    print(f"\n  🔧 連貫性修正: {total_fixes} 次")
    for k, v in coherence_fixes.items():
        if v > 0: print(f"      {k}: {v}")
names_used = Counter(p["name"] for p in personas)
print(f"\n  📛 名字唯一性: {len(names_used)} 個不重複名字 ({len(names_used)/len(personas)*100:.1f}%)")
top_names = [f"{n}({c})" for n, c in names_used.most_common(5)]
print(f"      最常用: {', '.join(top_names)}")
print(f"\n  💾 已存: hermesa3/persona/tw_persona_1069.json ({len(personas)} personas)")
print(f"{'='*60}")
