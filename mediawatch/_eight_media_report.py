#!/usr/bin/env python3
"""
Eight-media comparison report generator for a given date.
Usage: python3 _eight_media_report.py --date 2026-07-06
"""
import sys, json, re, os, time
from datetime import datetime, date
from collections import defaultdict, Counter
from urllib.parse import urljoin

TARGET_DATE = "2026-07-06"
if "--date" in sys.argv:
    idx = sys.argv.index("--date")
    if idx + 1 < len(sys.argv):
        TARGET_DATE = sys.argv[idx + 1]

OUTDIR = "/home/ubuntu/.hermes/cache/media_deep"
os.makedirs(OUTDIR, exist_ok=True)

# ─── 全文分析的人物字典 ───
PERSON_NAMES = [
    "賴清德", "蔣萬安", "沈伯洋", "韓國瑜", "蕭美琴",
    "林沛祥", "矢板明夫", "黃國昌", "王定宇", "盧秀燕",
    "陳以信", "吳子嘉", "李洋", "侯友宜", "楊珍妮",
    "柯文哲", "鄭麗文", "吳乃仁", "連勝文", "張善政",
    "柯志恩", "翁曉玲", "蘇巧慧", "何欣純", "賴瑞隆",
    "謝龍介", "江啟臣", "林姿妙", "陳其邁", "黃偉哲",
    "鄭朝方", "吳旭智", "邱臣遠", "李四川", "谷立言",
    "川普", "拜登", "馬英九", "顧立雄",
]

PARTY_KEYWORDS = {
    "民進黨": ["民進黨", "綠營", "綠委", "賴清德"],
    "國民黨": ["國民黨", "藍營", "藍委", "蔣萬安"],
    "民眾黨": ["民眾黨", "白營", "柯文哲", "黃國昌"],
    "中共": ["中共", "中國", "北京", "解放軍", "共軍"],
    "美國": ["美國", "美軍", "白宮", "川普", "拜登"],
}

def fetch(url, retries=3):
    import subprocess
    for a in range(retries):
        try:
            r = subprocess.run(["curl","-sL","--max-time","20", url], capture_output=True, text=True, timeout=25)
            if r.returncode == 0 and len(r.stdout) > 500:
                return r.stdout
        except: pass
        time.sleep(1)
    return ""

def body_text_from_html(html):
    """Extract clean body text from a news article HTML page."""
    # Remove script, style, nav
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL|re.IGNORECASE)
    # Strip all tags, get text
    text = re.sub(r'<[^>]+>', '\n', html)
    # Decode common entities
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    # Remove short lines (nav, menu items)
    lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
    # Remove lines that are purely navigation
    nav_keywords = ['cookie', 'close', 'menu', 'search', 'share', 'facebook', 'twitter',
                    'copyright', 'all rights', 'subscribe', 'newsletter', 'loading']
    lines = [l for l in lines if not any(kw in l.lower() for kw in nav_keywords)]
    # Remove lines with too many special chars (likely code/template)
    lines = [l for l in lines if sum(1 for c in l if c in '<>{}[]=+/') < len(l) * 0.2]
    return '\n'.join(lines)

def fetch_article_body(url, max_pages=30):
    """Fetch and extract clean body text from article URL."""
    html = fetch(url)
    if not html:
        return ""
    text = body_text_from_html(html)
    # Only keep first ~5000 chars of actual content (articles have header/footer nav)
    # Find the longest continuous text segment (the article body)
    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 30]
    if not paragraphs:
        return ""
    return '\n'.join(paragraphs[:max_pages])

def count_names(text, names):
    """Count occurrences of each name in text."""
    c = Counter()
    for name in names:
        count = text.count(name)
        if count > 0:
            c[name] = count
    return c

def count_terms(text, term_dict):
    """Count occurrences of each term group in text."""
    c = Counter()
    for group, keywords in term_dict.items():
        total = sum(text.count(kw) for kw in keywords)
        if total > 0:
            c[group] = total
    return c

# ─── 人設操作／風向判讀關鍵字庫 ───
PERSONA_BUILD = [
    "肯定", "讚", "力挺", "有功", "貢獻", "表率", "突破",
    "成功", "佳績", "進步", "創新高", "親民", "溫暖",
    "團結", "捍衛", "保護", "承諾", "落實",
]

PERSONA_DESTROY = [
    "雙標", "打臉", "造假", "翻車", "裝瞎", "裝天真",
    "大雷包", "何不食肉糜", "護航", "邪惡", "可恥",
    "騙", "謊", "黑心", "包庇", "蓋牌", "無能",
    "甩鍋", "卸責", "傲慢", "酬庸", "派系", "門神",
]

PERSONA_QUESTION = [
    "質疑", "呼籲", "要求", "批", "轟", "酸", "怒",
    "應說明", "待釐清", "引發討論", "爭議",
]

def label_persona(text, person_name, title=""):
    """Label persona engineering direction for a person in given text."""
    context = (title + " " + text).lower()
    destroy_score = sum(1 for kw in PERSONA_DESTROY if kw in context)
    build_score = sum(1 for kw in PERSONA_BUILD if kw in context)
    question_score = sum(1 for kw in PERSONA_QUESTION if kw in context)
    
    if destroy_score > build_score and destroy_score > 0:
        return "🗑️"
    if build_score > destroy_score and build_score > 0:
        return "😇"
    if question_score > 0:
        return "⚠️"
    return "😐"

def label_narrative(text, title=""):
    """Label narrative steering direction for an event/topic."""
    context = (title + " " + text).lower()
    blame_count = sum(1 for kw in ["應負責","咎責","究責","懲處","下台","道歉","打臉","說謊","隱瞞"] if kw in context)
    factual_count = sum(1 for kw in ["公布","宣布","指出","說明","表示","確認","報告","數據","統計","調查"] if kw in context)
    if blame_count > factual_count and blame_count > 0:
        return "🔴"
    if factual_count > 0:
        return "🟢"
    return "🟡"

def extract_titles(html, url_pattern, source_name):
    """Extract article titles and URLs from HTML."""
    articles = []
    seen = set()
    def add(t, u):
        t = t.strip()
        u = u.split("?")[0]
        if t and len(t) > 6 and "cookie" not in t.lower() and t not in seen:
            seen.add(t)
            articles.append((t, u))
    # Pattern 1: <a href="URL" title="TITLE">
    p1 = re.findall(r'<a[^>]*href="([^"]*'+url_pattern+'[^"]*)"[^>]*title="([^"]*)"', html)
    for url, title in p1:
        add(title, url)
    # Pattern 2: <a href="URL">TEXT</a> with TEXT > 10 chars
    p2 = re.findall(r'<a[^>]*href="([^"]*'+url_pattern+'[^"]*)"[^>]*>([^<]{10,})</a>', html)
    for url, title in p2:
        t = re.sub(r'<[^>]+>', '', title).strip()
        add(t, url)
    return articles

def extract_rss_titles(xml_text, source_name):
    """Extract article titles and URLs from RSS XML."""
    import xml.etree.ElementTree as ET
    articles = []
    try:
        root = ET.fromstring(xml_text)
        # RSS 2.0: channel > item > title, link
        ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            if title_el is not None and link_el is not None:
                t = title_el.text.strip() if title_el.text else ""
                if t and len(t) > 6:
                    articles.append((t[:65], link_el.text.strip() if link_el.text else ""))
    except ET.ParseError as e:
        print(f"  ⚠️ RSS parse error: {e}")
    return articles

def save_raw(name, data):
    path = os.path.join(OUTDIR, f"{name}_raw_{TARGET_DATE}.json")
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False)
    return path

# ═══ SCRAPE ═══

results = {}

# 1. CNA International (baseline)
print("📡 CNA 國際...", end=" ", flush=True)
html = fetch("https://www.cna.com.tw/list/aopl.aspx")
titles = extract_titles(html, "aopl", "cna")
results["中央社國際"] = [{"title":t, "url":urljoin("https://www.cna.com.tw",u)} for t,u in titles[:20]]
print(f"{len(results['中央社國際'])} 篇")

# 2. CNA Politics
print("📡 CNA 政治...", end=" ", flush=True)
html = fetch("https://www.cna.com.tw/list/aipl.aspx")
titles = extract_titles(html, "aipl", "cna")
results["中央社政治"] = [{"title":t, "url":urljoin("https://www.cna.com.tw",u)} for t,u in titles[:20]]
print(f"{len(results['中央社政治'])} 篇")

# 3. 自由時報
print("📡 自由時報...", end=" ", flush=True)
html = fetch("https://news.ltn.com.tw/list/breakingnews/politics")
titles = extract_titles(html, r"news\.ltn\.com\.tw/news/politics", "ltn")
results["自由時報"] = [{"title":t, "url":u} for t,u in titles[:30]]
print(f"{len(results['自由時報'])} 篇")

# 4. 聯合報
print("📡 聯合報...", end=" ", flush=True)
html = fetch("https://udn.com/news/breaknews/1")
titles = extract_titles(html, r"udn\.com/news/story", "udn")
results["聯合報"] = [{"title":t, "url":u} for t,u in titles[:30]]
print(f"{len(results['聯合報'])} 篇")

# 5. TVBS (via RSS feed — SPA site)
print("📡 TVBS...", end=" ", flush=True)
html = fetch("https://news.tvbs.com.tw/web_api/play_feed_new/politics")
titles = extract_rss_titles(html, "tvbs")
results["TVBS"] = [{"title":t, "url":u} for t,u in titles[:30]]
print(f"{len(results['TVBS'])} 篇")

# 6. ETtoday
print("📡 ETtoday...", end=" ", flush=True)
html = fetch("https://www.ettoday.net/news/politics")
titles = extract_titles(html, r"ettoday\.net", "ettoday")
results["ETtoday"] = [{"title":t, "url":u} for t,u in titles[:30]]
print(f"{len(results['ETtoday'])} 篇")

# 7. 三立
print("📡 三立...", end=" ", flush=True)
html = fetch("https://www.setn.com/ViewAll.aspx?PageGroupID=6")
titles = extract_titles(html, r"setn\.com", "setn")
results["三立"] = [{"title":t, "url":u} for t,u in titles[:20]]
print(f"{len(results['三立'])} 篇")

# 8. 中天 (via RSS feed — SPA site)
print("📡 中天...", end=" ", flush=True)
html = fetch("https://www.ctitv.com.tw/feed/")
titles = extract_rss_titles(html, "cti")
results["中天"] = [{"title":t, "url":u} for t,u in titles[:20]]
print(f"{len(results['中天'])} 篇")

# 9. 風傳媒 (Nuxt SPA — scrape homepage <a><h3> pattern)
print("📡 風傳媒...", end=" ", flush=True)
html = fetch("https://www.storm.mg")
titles = []
for m in re.finditer(r'<a[^>]*href="(/article/\d+)"[^>]*>.*?<h3[^>]*>(.*?)</h3>', html, re.DOTALL):
    t = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    u = "https://www.storm.mg" + m.group(1)
    if t and len(t) > 6:
        titles.append((t, u))
results["風傳媒"] = [{"title":t, "url":u} for t,u in titles[:20]]
print(f"{len(results['風傳媒'])} 篇")

# ═══ NEW SOURCES ═══

# 10. Yahoo News 政治 (via RSS)
print("📡 Yahoo 新聞...", end=" ", flush=True)
html = fetch("https://tw.news.yahoo.com/rss/politics")
titles = extract_rss_titles(html, "yahoo")
results["Yahoo新聞"] = [{"title":t, "url":u} for t,u in titles[:30]]
print(f"{len(results['Yahoo新聞'])} 篇")

# 11. LINE NEWS Today 政治 (SSR — extract h3 from HTML)
print("📡 LINE NEWS...", end=" ", flush=True)
html = fetch("https://today.line.me/tw/v2/tab/politics")
titles = []
for m in re.finditer(r'<h3[^>]*class="[^"]*header[^"]*"[^>]*>([^<]{10,})</h3>', html):
    t = m.group(1).strip()
    if t and len(t) > 6:
        titles.append((t, ""))
results["LINE NEWS"] = [{"title":t, "url":""} for t,u in titles[:20]]
print(f"{len(results['LINE NEWS'])} 篇")

save_raw("all_media", results)
print("✅ Raw data saved\n")

# ═══ FULL-TEXT ANALYSIS ═══
print("📖 全文爬取與分析中...")
print(f"{'─'*50}")

outlet_fulltext = {}
total_articles = sum(len(v) for k,v in results.items() if k != "中央社國際")
fetched = 0
for outlet, articles in results.items():
    if outlet == "中央社國際":
        continue
    all_text = ""
    outlet_names = Counter()
    outlet_terms = Counter()
    outlet_persona = {}  # person → label
    outlet_articles_text = []  # list of (title, body) for persona labeling
    for a in articles[:15]:  # Top 15 per outlet
        url = a["url"]
        if not url:
            continue
        body = fetch_article_body(url, max_pages=20)
        if body:
            all_text += body + "\n"
            outlet_names += count_names(body, PERSON_NAMES)
            outlet_terms += count_terms(body, PARTY_KEYWORDS)
            outlet_articles_text.append((a["title"], body))
        fetched += 1
        if fetched % 10 == 0:
            print(f"  📄 {fetched}/{total_articles} 篇已處理")
    # Compute persona labels for top names in this outlet
    for name, count in outlet_names.most_common(15):
        combined = " ".join(t + " " + b for t, b in outlet_articles_text)
        outlet_persona[name] = label_persona(combined, name)
    outlet_fulltext[outlet] = {
        "text": all_text,
        "names": dict(outlet_names.most_common(30)),
        "terms": dict(outlet_terms),
        "persona": outlet_persona,
    }

# Save fulltext analysis
with open(os.path.join(OUTDIR, f"fulltext_analysis_{TARGET_DATE}.json"), "w") as f:
    json.dump({k: {"names": v["names"], "terms": v["terms"], "persona": v["persona"]} for k, v in outlet_fulltext.items()}, f, ensure_ascii=False, indent=2)
print(f"  ✅ 全文分析完成（{fetched} 篇）")
print()

# ═══ SILENT ISSUE DETECTION ═══

# CNA international headlines = baseline
cna_world_titles = [a["title"] for a in results.get("中央社國際", [])]

# Extract key topics from CNA world
KEYWORDS = {
    "以哈衝突": ["以色列","哈瑪斯","加薩"],
    "俄烏戰爭": ["俄羅斯","烏克蘭","基輔"],
    "美中關係": ["美中","中國","拜登","川普"],
    "台海情勢": ["台海","共軍","遼寧號"],
    "全球經濟": ["美股","通膨","Fed","利率"],
    "中東局勢": ["伊朗","沙烏地","中東"],
}

def topic_in_titles(titles_src, keywords):
    text = " ".join(titles_src)
    for kw in keywords:
        if kw in text:
            return True
    return False

# Check which major news topics CNA itself covered
cna_text = " ".join(cna_world_titles)
print(f"\nCNA 國際頭條 topics:")
cna_topics = []
for topic, kws in KEYWORDS.items():
    if any(kw in cna_text for kw in kws):
        cna_topics.append(topic)
        print(f"  ✅ {topic}")
if not cna_topics:
    cna_topics = list(KEYWORDS.keys())[:4]  # fallback

# Build silence matrix
media_names = ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒"]
print(f"\n{'='*70}")
print(f"  八家媒體 7/6 比對報告 — 處理中")
print(f"{'='*70}")

total_all = sum(len(v) for k,v in results.items() if k != "中央社國際")
print(f"\n  總文章數（不含 CNA 國際）: {total_all}")

# Article count per source
print(f"\n📊 一、資料量總覽")
print(f"{'─'*50}")
for src in ["中央社政治","自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒","Yahoo新聞","LINE NEWS"]:
    count = len(results.get(src, []))
    bar = "█" * min(count//2, 20)
    print(f"  {src+':':<12s} {count:>3d}篇 {bar}")

# Silence matrix using CNA international topics
cna_headlines = [a["title"] for a in results.get("中央社國際", [])[:10]]
print(f"\n🔇 二、沉默議題矩陣（7/6 CNA 國際頭條）")
print(f"{'─'*50}")
print(f"  CNA 有報的國際新聞（前10）:")
for i, h in enumerate(cna_headlines, 1):
    print(f"    {i:02d}. {h[:60]}...")

print(f"\n{'='*70}")
print(f"📄 完整報告另存")
print(f"{'='*70}")

# Generate markdown report (07-07 style)
report = f"""# 十家媒體敘事比對 + CNA Baseline 沉默議題 — {TARGET_DATE}

## 分析範圍：自由時報 · 聯合報 · TVBS · ETtoday · 三立 · 中天 · 風傳媒 · Yahoo新聞 · LINE NEWS · CNA

---

## 一、資料量與爬取方式

| 媒體 | 篇數 | 光譜定位 | 爬取方式 | 全文 |
|:----:|:----:|:--------:|:--------|:----:|
"""
MEDIA_LABELS = {"中央社政治":"官方通訊社","自由時報":"偏綠","聯合報":"平衡","TVBS":"中性偏綠","ETtoday":"中性","三立":"偏綠","中天":"偏藍","風傳媒":"偏藍/評論","Yahoo新聞":"聚合/綜合","LINE NEWS":"聚合/綜合"}
MEDIA_CRAWL = {"中央社政治":"列表頁","自由時報":"curl 列表頁","聯合報":"curl 列表頁","TVBS":"RSS feed","ETtoday":"curl 列表頁","三立":"curl 列表頁","中天":"RSS feed","風傳媒":"首頁 <h3>","Yahoo新聞":"RSS feed 30篇","LINE NEWS":"SSR h3 提取 12篇"}
MEDIA_NOTE = {"中天":"RSS 僅輸出業配/活動稿，非全站","Yahoo新聞":"聚合平台，含多家媒體來源","LINE NEWS":"聚合平台，無獨立報導","聯合報":"當日量偏少"}

for src in ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒","Yahoo新聞","LINE NEWS"]:
    c = len(results.get(src, []))
    label = MEDIA_LABELS.get(src, "")
    crawl = MEDIA_CRAWL.get(src, "")
    ft_ok = "✅" if src in outlet_fulltext and outlet_fulltext[src]["names"] else "❌"
    note = MEDIA_NOTE.get(src, "")
    report += f"| **{src}** | {c} | {label} | {crawl} | {ft_ok} |\n"
    if note:
        report += f"| ⚠️ | | | {note} | |\n"

report += f"\n| **總計** | **{total_all}** | — | — | — |\n\n"
report += "> **資料完整性說明**：各媒體爬取方式如上。TVBS/中天 改用 RSS feed 後可靠性提升但篇數下降。Yahoo 為聚合平台，內含多家媒體文章。LINE NEWS 僅能取得標題，無全文分析。\n\n---\n\n"

# §2 — Person frequency (collapsible, skip-friendly)
report += "<details>\n<summary>📊 人物提及頻率（全內文 Top 15，可跳過）</summary>\n\n"
report += "| 人物 |"
for src in ["自由","聯合","TVBS","ETto","三立","中天","風媒"]:
    report += f" {src} |"
report += " 合計 |\n|" + "|".join(":---:" for _ in range(9)) + "|\n"
all_ft_names = Counter()
for src in ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒"]:
    if src in outlet_fulltext:
        all_ft_names += Counter(outlet_fulltext[src].get("names", {}))
for name, _ in all_ft_names.most_common(15):
    row = [name]
    total = 0
    for src in ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒"]:
        c = outlet_fulltext.get(src, {}).get("names", {}).get(name, 0)
        row.append(str(c))
        total += c
    row.append(str(total))
    report += "| " + " | ".join(row) + " |\n"
report += "\n</details>\n\n---\n\n"

# §3 — Media narrative characteristics (auto-generated from data)
report += "## 三、各媒體敘事特徵\n\n"
for src in ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒","Yahoo新聞","LINE NEWS"]:
    c = len(results.get(src, []))
    label = MEDIA_LABELS.get(src, "")
    ft = outlet_fulltext.get(src, {})
    names = ft.get("names", {})
    terms = ft.get("terms", {})
    
    # Auto-generate top keywords (top 3 persons + top 2 terms)
    top_persons = [n for n, _ in Counter(names).most_common(3)]
    top_terms = [t for t, _ in Counter(terms).most_common(3)]
    keywords = top_persons + top_terms
    kw_str = "、".join(keywords[:5]) if keywords else "—"
    
    # Simple characterization based on data
    if src == "Yahoo新聞":
        desc = "聚合平台，涵蓋最多來源"
    elif src == "LINE NEWS":
        desc = "聚合平台，以民生/颱風/社會為主"
    elif c >= 20:
        desc = f"大量，{label}"
    elif c >= 10:
        desc = f"中等，{label}"
    else:
        desc = f"少量，{label}"
    
    report += f"### {src}（{c}篇）— {desc}\n"
    report += f"- **關鍵詞**：{kw_str}\n"
    
    # If full-text available, add term dominance note
    if terms:
        dominant = max(terms, key=terms.get) if terms else ""
        if dominant:
            report += f"- **最突出詞彙**：{dominant}（{terms[dominant]}次）\n"
    
    # Add source-specific notes
    note = MEDIA_NOTE.get(src, "")
    if note:
        report += f"- ⚠️ {note}\n"
    report += "\n"

# §4 — Shared topic framing (auto-detect from headlines)
report += "## 四、共同議題框架比對\n\n"
# Simple approach: find keywords that appear in 3+ outlets
from collections import defaultdict
topic_keywords = defaultdict(list)
for src in ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒","Yahoo新聞"]:
    for a in results.get(src, []):
        title = a["title"]
        # Detect major topics from title keywords
        for topic, kws in [("矢板明夫/跨境鎮壓",["矢板","明夫","跨境","鎮壓"]),
                           ("毒油/致癌油",["毒油","致癌","中聯","苯駢芘"]),
                           ("巴威颱風",["巴威","颱風"]),
                           ("巨浪三/中共飛彈",["巨浪","飛彈","中共"]),
                           ("美軍/伊朗",["美軍","伊朗","空襲","荷莫茲"]),
                           ("憲兵/刺針",["憲兵","刺針"]),
                           ("黃國昌/光電",["黃國昌","光電","門神","賴勁麟"])]:
            if any(kw in title for kw in kws):
                topic_keywords[topic].append((src, title[:50]))

for topic, matches in topic_keywords.items():
    # Only show topics covered by 2+ outlets
    sources_covered = set(m[0] for m in matches)
    if len(sources_covered) < 2:
        continue
    
    report += f"### 議題：{topic}\n\n"
    report += "| 媒體 | 篇數標題 | 前期框架 |\n"
    report += "|:----:|:---------|:--------|\n"
    for src in ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒","Yahoo新聞"]:
        src_matches = [m for m in matches if m[0] == src]
        if src_matches:
            for t, title in src_matches[:2]:
                report += f"| **{src}** | {title}… | 🟡 待判讀 |\n"
        else:
            report += f"| **{src}** | ❌ 沉默 | ⚪ 沉默 |\n"
    report += "\n"

report += "---\n\n"

# §5 — Silence matrix
report += "## 五、沉默議題矩陣\n\n"
report += "| CNA國際頭條 | 自由 | 聯合 | TVBS | ETtoday | 三立 | 中天 | 風媒 | Yahoo |\n"
report += "|:-----------|:----:|:----:|:----:|:-------:|:----:|:----:|:----:|:-----:|\n"
for h in cna_headlines[:10]:
    row = [h[:25] + "…"]
    for src in ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒","Yahoo新聞"]:
        covered = False
        for a in results.get(src, []):
            title_words = set(a["title"])
            if len(set(h) & set(a["title"])) > 5:  # simple overlap check
                covered = True
                break
        row.append("✅" if covered else "❌")
    report += "| " + " | ".join(row) + " |\n"

report += "\n---\n\n"

# §6 — Key insights (auto-generated)
report += "## 六、關鍵洞察\n\n"
# Count how many CNA headlines were covered by any domestic outlet
silence_count = 0
for h in cna_headlines[:10]:
    any_covered = False
    for src in ["自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒","Yahoo新聞"]:
        for a in results.get(src, []):
            if len(set(h) & set(a["title"])) > 5:
                any_covered = True
                break
    if not any_covered:
        silence_count += 1

insights = []
insights.append(f"**國際沉默**：CNA 國際頭條 {len(cna_headlines)} 篇中，{silence_count} 篇國內媒體完全未報導。")
max_src = max([(s, len(results.get(s,[]))) for s in ["ETtoday","三立","風傳媒","Yahoo新聞"]], key=lambda x: x[1])
insights.append(f"**當日最大量**：{max_src[0]}（{max_src[1]}篇），提供最大資訊覆蓋。")

# Find extremes
for src, label in [("自由時報","偏綠"),("三立","偏綠"),("中天","偏藍"),("風傳媒","偏藍/評論")]:
    c = len(results.get(src, []))
    if c > 0:
        insights.append(f"**{src}（{label}）**：{c}篇，光譜定位 {label}。")

for i, insight in enumerate(insights, 1):
    report += f"{i}. {insight}\n"

report += "\n---\n\n## 七、原始資料\n\n"
for src in ["中央社國際","自由時報","聯合報","TVBS","ETtoday","三立","中天","風傳媒","Yahoo新聞","LINE NEWS"]:
    arts = results.get(src, [])
    report += f"\n### {src}（{len(arts)} 篇）\n\n"
    for a in arts[:10]:
        report += f"- {a['title'][:65]}\n"

report += f"\n---\n\n*報告產生：{datetime.now().strftime('%Y-%m-%d %H:%M')} · 爬蟲：`_eight_media_report.py`（10媒體 + 全文分析 + 人設標籤 v1）*\n"

report_path = f"/home/ubuntu/lab-riscv/hermesa3/mediawatch/eight-media-comparison-{TARGET_DATE}.md"
with open(report_path, "w") as f:
    f.write(report)
print(f"  💾 報告: {report_path}")
