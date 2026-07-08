#!/usr/bin/env python3
"""
Generate 997 personas from weighted Taiwan population data.
Uses real API data where available + known population ratios for complete coverage.
"""
import requests, json, sys, re, random
from collections import defaultdict, Counter

random.seed(42)

# ═══ 1. POPULATION DATA (REAL + ESTIMATED) ═══

# Known Taiwan population distribution (2025 estimates)
REGION_POP = {
    "北北基": 0.30, "桃竹苗": 0.17, "中彰投": 0.19,
    "雲嘉南": 0.14, "高屏": 0.15, "宜花東": 0.04, "離島": 0.01
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
TARGET = 997
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
    "0-11":{"高中以下":1},"12-18":{"高中以下":0.95,"大學":0.05},
    "19-24":{"高中以下":0.3,"大學":0.6,"研究所以上":0.1},
    "25-34":{"高中以下":0.15,"大學":0.55,"研究所以上":0.3},
    "35-44":{"高中以下":0.25,"大學":0.5,"研究所以上":0.25},
    "45-54":{"高中以下":0.35,"大學":0.45,"研究所以上":0.2},
    "55-64":{"高中以下":0.5,"大學":0.35,"研究所以上":0.15},
    "65+":{"高中以下":0.6,"大學":0.3,"研究所以上":0.1},
}

OCC_PROB = {
    ("0-11","男"):{"學生":1},("0-11","女"):{"學生":1},
    ("12-18","男"):{"學生":0.95,"服務":0.05},("12-18","女"):{"學生":0.95,"服務":0.05},
    ("19-24","男"):{"學生":0.5,"科技":0.15,"服務":0.2,"製造":0.15},
    ("19-24","女"):{"學生":0.5,"服務":0.3,"科技":0.1,"教育":0.1},
    ("25-34","男"):{"科技":0.3,"製造":0.2,"服務":0.2,"教育":0.1,"醫療":0.05,"金融":0.05,"公務":0.1},
    ("25-34","女"):{"服務":0.25,"教育":0.2,"醫療":0.15,"科技":0.15,"公務":0.15,"金融":0.1},
    ("35-44","男"):{"科技":0.25,"製造":0.2,"服務":0.15,"自營":0.15,"公務":0.1,"教育":0.1,"醫療":0.05},
    ("35-44","女"):{"服務":0.2,"教育":0.2,"醫療":0.15,"公務":0.15,"科技":0.1,"自營":0.1,"製造":0.1},
    ("45-54","男"):{"製造":0.25,"自營":0.2,"服務":0.15,"公務":0.15,"教育":0.1,"科技":0.1,"醫療":0.05},
    ("45-54","女"):{"服務":0.2,"教育":0.2,"公務":0.15,"自營":0.15,"醫療":0.1,"製造":0.1,"家管":0.1},
    ("55-64","男"):{"退休":0.3,"製造":0.2,"自營":0.2,"服務":0.15,"公務":0.1,"教育":0.05},
    ("55-64","女"):{"退休":0.3,"家管":0.2,"服務":0.2,"自營":0.15,"教育":0.1,"公務":0.05},
    ("65+","男"):{"退休":0.85,"自營":0.1,"服務":0.05},
    ("65+","女"):{"退休":0.85,"家管":0.1,"服務":0.05},
}

INC_PROB = {
    "學生":{"無收入":0.9,"<3萬":0.1},"退休":{"<3萬":0.5,"3-8萬":0.4,">8萬":0.1},
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
    "0-11":  {"4":0.25,"5+":0.25,"3":0.22,"2":0.15,"1":0.13},
    "12-18": {"4":0.25,"5+":0.25,"3":0.22,"2":0.15,"1":0.13},
    "19-24": {"3":0.25,"4":0.22,"2":0.20,"1":0.18,"5+":0.15},
    "25-34": {"2":0.28,"3":0.25,"1":0.22,"4":0.15,"5+":0.10},
    "35-44": {"3":0.25,"2":0.22,"4":0.20,"1":0.18,"5+":0.15},
    "45-54": {"2":0.25,"3":0.22,"4":0.20,"1":0.18,"5+":0.15},
    "55-64": {"1":0.30,"2":0.28,"3":0.18,"4":0.14,"5+":0.10},
    "65+":   {"1":0.45,"2":0.25,"3":0.15,"4":0.10,"5+":0.05},
}

FAMILY_INCOME_PROB = {
    ("<3萬","學生"):{"<1萬":0.1,"1-3萬":0.6,"3-7萬":0.25,"7萬+":0.05},
    ("<3萬","退休"):{"<1萬":0.2,"1-3萬":0.5,"3-7萬":0.2,"7萬+":0.1},
    ("<3萬","服務"):{"<1萬":0.1,"1-3萬":0.5,"3-7萬":0.3,"7萬+":0.1},
    ("<3萬","製造"):{"<1萬":0.05,"1-3萬":0.4,"3-7萬":0.4,"7萬+":0.15},
    ("3-8萬","科技"):{"1-3萬":0.1,"3-7萬":0.4,"7萬+":0.4,"<1萬":0.1},
    ("3-8萬","金融"):{"1-3萬":0.1,"3-7萬":0.4,"7萬+":0.4,"<1萬":0.1},
    ("3-8萬","公務"):{"1-3萬":0.15,"3-7萬":0.5,"7萬+":0.3,"<1萬":0.05},
    ("3-8萬","教育"):{"1-3萬":0.15,"3-7萬":0.55,"7萬+":0.25,"<1萬":0.05},
    ("3-8萬","醫療"):{"1-3萬":0.1,"3-7萬":0.5,"7萬+":0.35,"<1萬":0.05},
    (">8萬","科技"):{"7萬+":0.6,"3-7萬":0.3,"1-3萬":0.1,"<1萬":0},
    (">8萬","金融"):{"7萬+":0.6,"3-7萬":0.3,"1-3萬":0.1,"<1萬":0},
    (">8萬","醫療"):{"7萬+":0.5,"3-7萬":0.4,"1-3萬":0.1,"<1萬":0},
    (">8萬","自營"):{"7萬+":0.5,"3-7萬":0.35,"1-3萬":0.1,"<1萬":0.05},
}

HOBBY_POOL = {
    "young":   {"打電動":0.20,"追劇":0.18,"球類":0.15,"閱讀":0.10,"登山":0.08,"逛街購物":0.08,"烹飪":0.05,"游泳":0.05,"音樂":0.05,"園藝":0.03,"泡茶":0.02,"打牌":0.01},
    "adult":   {"追劇":0.18,"登山":0.15,"閱讀":0.14,"球類":0.12,"逛街購物":0.10,"打電動":0.08,"園藝":0.07,"烹飪":0.06,"游泳":0.05,"泡茶":0.03,"打牌":0.01,"下棋":0.01},
    "senior_m":{"閱讀":0.18,"登山":0.15,"泡茶":0.14,"追劇":0.10,"園藝":0.09,"下棋":0.08,"球類":0.07,"打牌":0.06,"逛街購物":0.04,"烹飪":0.03,"打電動":0.03,"游泳":0.03},
    "senior_f":{"追劇":0.18,"閱讀":0.14,"園藝":0.12,"逛街購物":0.12,"登山":0.10,"泡茶":0.08,"烹飪":0.08,"打牌":0.06,"廣場舞":0.05,"球類":0.03,"下棋":0.02,"打電動":0.02},
    "kid":     {"打電動":0.25,"球類":0.20,"閱讀":0.12,"追劇":0.12,"繪畫":0.10,"登山":0.06,"逛街購物":0.05,"游泳":0.04,"烹飪":0.03,"園藝":0.02,"泡茶":0.01,"音樂":0.00},
}

# Marriage status by age
MARRIAGE_PROB = {
    "0-11":  {"未婚":1.00,"已婚":0,"離婚":0,"鰥寡":0},
    "12-18": {"未婚":1.00,"已婚":0,"離婚":0,"鰥寡":0},
    "19-24": {"未婚":0.85,"已婚":0.12,"離婚":0.02,"鰥寡":0.01},
    "25-34": {"未婚":0.40,"已婚":0.50,"離婚":0.08,"鰥寡":0.02},
    "35-44": {"未婚":0.15,"已婚":0.65,"離婚":0.15,"鰥寡":0.05},
    "45-54": {"未婚":0.08,"已婚":0.65,"離婚":0.18,"鰥寡":0.09},
    "55-64": {"未婚":0.05,"已婚":0.60,"離婚":0.15,"鰥寡":0.20},
    "65+":   {"未婚":0.03,"已婚":0.45,"離婚":0.07,"鰥寡":0.45},
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
    "北北基":{"泛藍":0.30,"泛綠":0.30,"無政治傾向":0.25,"白/第三勢力":0.15},
    "桃竹苗":{"泛藍":0.35,"無政治傾向":0.30,"泛綠":0.20,"白/第三勢力":0.15},
    "中彰投":{"泛藍":0.30,"泛綠":0.30,"無政治傾向":0.25,"白/第三勢力":0.15},
    "雲嘉南":{"泛綠":0.40,"泛藍":0.20,"無政治傾向":0.30,"白/第三勢力":0.10},
    "高屏"   :{"泛綠":0.45,"泛藍":0.20,"無政治傾向":0.25,"白/第三勢力":0.10},
    "宜花東":{"泛藍":0.35,"無政治傾向":0.35,"泛綠":0.20,"白/第三勢力":0.10},
    "離島"   :{"泛藍":0.40,"無政治傾向":0.35,"泛綠":0.15,"白/第三勢力":0.10},
}

MEDIA_PROB = {
    "0-11":{"社群為主":0.6,"混合":0.3,"傳統媒體為主":0.1},
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

def wchoice(opts):
    ks, vs = zip(*opts.items())
    return random.choices(ks, weights=vs, k=1)[0]

# ═══ 3. NAME GENERATORS ═══

NAME_CACHE = {}
def get_name(age, sex, occ):
    key = (age, sex, occ)
    if key in NAME_CACHE: return NAME_CACHE[key]
    if age == "0-11":
        pool = ["糖糖","果果","樂樂","星星","蜜蜜","嘟嘟","妮妮","寶寶","可可","芽芽","米米","豆豆"]
    elif age == "12-18":
        pool = ["小莓","星醬","芽泉","糖球","小雲","夢醬","莓果","星月","小桃","蜜糖","泡泡","小葵"]
    elif age == "65+":
        pool = (["春伯","福伯","金伯","天伯","榮伯","有伯","萬伯","土伯","坤伯"] if sex=="男"
                else ["春姨","麗媽","秀姨","阿好嬸","金花嬸","素蘭嬸","阿桃","阿滿","阿鳳"])
    elif (age == "19-24" and sex == "男") or (age == "25-34" and sex == "男"):
        if occ in ("科技","金融"):
            pool = ["阿睿","阿凱","馬克","大衛","文森","阿誠","小光","傑森"]
        else:
            pool = ["小宇","小安","阿杰","阿豪","阿翔","小陳","阿元","阿明"]
    elif (age == "19-24" and sex == "女") or (age == "25-34" and sex == "女"):
        pool = ["小艾","艾倫","莉亞","若希","安妮","凱琳","可恩","小曦","愛莎","小莉","小薇","小彤"]
    elif age in ("35-44","45-54") and sex == "男":
        pool = ["志豪","大仁","建宏","強哥","文彬","明義","世昌","志強","永信","俊傑"]
    elif age in ("35-44","45-54") and sex == "女":
        pool = ["靜怡","雅雯","慧君","美珍","素芬","麗卿","淑貞","惠如","美惠","麗華"]
    else:
        pool = ["秀蘭","美惠","素卿","麗華","春梅","美枝","淑華","明輝","俊傑"]
    random.shuffle(pool)
    NAME_CACHE[key] = pool[0]
    return NAME_CACHE[key]

# ═══ 4. GENERATE ═══

personas = []
pid = 0
coherence_fixes = {"fam_inc_5plus": 0, "fam_inc_4": 0, "fam_inc_student_5plus": 0, "marriage_minor": 0}

# ── Background story inference engine ──
def infer_background(age, sex, marriage, occ, fam, fam_inc, region, inc):
    parts = []
    # Household composition
    if fam == "1" and marriage == "未婚": parts.append("自己一個人住")
    elif fam == "1" and marriage == "鰥寡": parts.append("老伴走了，現在獨居")
    elif fam == "2" and marriage == "未婚" and age in ("19-24","25-34"): parts.append("跟媽媽同住，是單親家庭")
    elif fam == "2" and marriage == "未婚" and age in ("0-11","12-18"): parts.append("跟其中一位家長同住")
    elif fam == "2" and marriage == "未婚" and age in ("35-44",): parts.append("跟年邁的父母同住，單身照顧長輩")
    elif fam == "2" and marriage == "已婚": parts.append("夫妻兩人世界")
    elif fam == "2" and marriage == "離婚": parts.append("離婚後自己帶一個孩子")
    elif fam == "3" and marriage == "已婚": parts.append("小家庭，夫妻加一個孩子")
    elif fam == "3" and marriage == "未婚": parts.append("跟父母同住，是家裡唯一的孩子")
    elif fam == "4" and marriage == "已婚": parts.append("典型小家庭，夫妻加兩個孩子")
    elif fam == "4" and marriage == "未婚": parts.append("跟父母和一個兄弟姊妹同住")
    elif fam == "5+" and marriage == "未婚" and occ == "學生": parts.append("家裡排行老大，底下還有弟妹")
    elif fam == "5+" and marriage == "未婚": parts.append("與父母和多位兄弟姊妹同住")
    elif fam == "5+" and marriage == "已婚": parts.append("大家庭，夫妻加三個以上的孩子")
    elif fam == "5+" and marriage in ("離婚","鰥寡"): parts.append("兒孫滿堂，與子女和孫輩同住")
    # Economic situation
    if fam in ("4","5+") and fam_inc in ("1-3萬","3-7萬"): parts.append("經濟上要很精打細算")
    elif fam in ("4","5+") and fam_inc == "<1萬": parts.append("經濟壓力非常大")
    elif fam in ("1","2") and fam_inc == "7萬+": parts.append("經濟上滿寬裕的")
    elif occ == "學生" and fam == "5+": parts.append("有時需要打工貼補家用")
    # Life stage
    if age == "0-11": parts.append("還在唸小學")
    elif age == "12-18": parts.append("正在唸中學")
    elif age == "19-24" and occ == "學生": parts.append("正在讀大學")
    elif age == "19-24" and occ != "學生": parts.append("剛出社會不久")
    elif age == "25-34" and occ not in ("退休","學生"): parts.append("正在事業打拚期")
    elif age == "35-44": parts.append("上有老下有小，是家庭支柱")
    elif age == "45-54": parts.append("工作量趨於穩定，開始思考退休規劃")
    elif age == "55-64" and occ == "退休": parts.append("剛退休，還在適應慢生活")
    elif age == "55-64": parts.append("快退休了，心態上開始調整")
    elif age == "65+" and marriage == "鰥寡": parts.append("現在一個人過日子")
    elif age == "65+": parts.append("退休生活，含飴弄孫")
    # Region
    region_map = {"北北基":"住在北北基生活圈","桃竹苗":"住在桃竹苗地區","中彰投":"住在中彰投地區","雲嘉南":"住在雲嘉南","高屏":"住在高屏地區","宜花東":"住在東部","離島":"住在離島，生活步調比較慢"}
    parts.append(region_map.get(region, "住在台灣"))
    return "。".join(parts) + "。"

for region, age, sex, weight, count in weighted:
    for _ in range(count):
        edu = wchoice(EDU_PROB.get(age, {"大學":1}))
        occ = wchoice(OCC_PROB.get((age, sex), {"其他":1}))
        inc = wchoice(INC_PROB.get(occ if occ in INC_PROB else "其他", {"<3萬":1}))
        pol = "無政治傾向" if age in ("0-11","12-18") else wchoice(POL_PROB.get(region, POL_PROB["北北基"]))
        med = wchoice(MEDIA_PROB.get(age, {"混合":1}))
        fam = wchoice(FAMILY_SIZE_PROB.get(age, {"3":1}))
        fam_inc = wchoice(FAMILY_INCOME_PROB.get((inc, occ) if (inc, occ) in FAMILY_INCOME_PROB else ("3-8萬", "服務"), {"3-7萬":1}))
        hobbies = pick_hobbies(age, sex, occ)
        marriage = wchoice(MARRIAGE_PROB.get(age, {"未婚":1}))
        
        # ── Coherence validation ──
        if fam == "5+" and fam_inc in ("<1萬", "1-3萬"):
            fam_inc = wchoice({"3-7萬":0.55, "7萬+":0.45})
            coherence_fixes["fam_inc_5plus"] += 1
        if fam == "4" and fam_inc == "<1萬":
            fam_inc = wchoice({"1-3萬":0.5, "3-7萬":0.5})
            coherence_fixes["fam_inc_4"] += 1
        if occ == "學生" and fam == "5+" and fam_inc in ("<1萬", "1-3萬"):
            fam_inc = wchoice({"3-7萬":0.5, "7萬+":0.5})
            coherence_fixes["fam_inc_student_5plus"] += 1
        if marriage == "已婚" and age in ("0-11","12-18"):
            marriage = "未婚"
            coherence_fixes["marriage_minor"] += 1
        
        name = get_name(age, sex, occ)
        
        # ── Political stance enrichment ──
        pol_stance = ""
        pol_issues = []
        if pol in POLITICAL_STANCES and age not in ("0-11","12-18"):
            ps = POLITICAL_STANCES[pol]
            pol_stance = random.choice(ps["stances"])
            pol_issues = random.sample(ps["issues"], min(2, len(ps["issues"])))
        
        # ── Background story inference ──
        story = infer_background(age, sex, marriage, occ, fam, fam_inc, region, inc)
        
        pid += 1
        base = f"{age}的{region}{sex}性，{marriage}，{occ}，{edu}，家庭{fam}人"
        ref = f"【{name}】{age}/{region}/{sex}/{marriage}/{occ}/{edu}/{fam}人/{fam_inc}/{','.join(hobbies)}"
        prefix = f"你是{name}，{base}。{story}興趣是{'、'.join(hobbies)}。{pol_stance}{'。' if pol_stance else ''}請以這個人設的視角回應。"

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
                "political_issues": pol_issues, "background_story": story
            },
            "reference_pre_prompt": ref,
            "prompt_prefix": prefix
        })

# ═══ 5. OUTPUT ═══

outpath = "/home/ubuntu/lab-riscv/hermesa3/persona/tw_persona_997.json"
with open(outpath, "w") as f:
    json.dump(personas, f, ensure_ascii=False, indent=2)

ages = Counter(p["dimensions"]["age"] for p in personas)
regions = Counter(p["dimensions"]["region"] for p in personas)
sexes = Counter(p["dimensions"]["sex"] for p in personas)

print(f"\n{'='*60}")
print(f"  997 Personas — Complete Distribution")
print(f"{'='*60}")
print(f"\n  年齡分布:")
for k in ["0-11","12-18","19-24","25-34","35-44","45-54","55-64","65+"]:
    bar = "█" * max(1, ages[k]//5)
    print(f"    {k:<6s}: {ages[k]:>3d} {bar}")
print(f"\n  區域分布:")
for r in ["北北基","桃竹苗","中彰投","雲嘉南","高屏","宜花東","離島"]:
    bar = "█" * max(1, regions[r]//3)
    print(f"    {r:<6s}: {regions[r]:>3d} {bar}")
print(f"\n  性別: 男={sexes['男']}  女={sexes['女']}")
total_fixes = sum(coherence_fixes.values())
if total_fixes > 0:
    print(f"\n  🔧 連貫性修正: {total_fixes} 次")
    for k, v in coherence_fixes.items():
        if v > 0: print(f"      {k}: {v}")
print(f"\n  💾 已存: hermesa3/persona/tw_persona_997.json ({len(personas)} personas)")
print(f"{'='*60}")
