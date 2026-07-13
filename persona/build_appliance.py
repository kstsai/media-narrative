#!/usr/bin/env python3
"""
build_appliance.py — 打包甲方可自部署的 persona DB appliance（分身）

用法:
    python3 build_appliance.py                          # 自動版號（從 VERSION）
    python3 build_appliance.py --version v3.2            # 指定版號
    python3 build_appliance.py --with-api                # 含簡易 API server
    python3 build_appliance.py --dry-run                 # 試跑，不產檔案

輸出: persona-appliance-v3.2.zip
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

HOME = Path.home()
PERSONA_DIR = Path("/home/ubuntu/lab-riscv/hermesa3/persona")
SKILL_DIR = HOME / ".hermes" / "skills" / "research" / "tw-persona-db"
OUTPUT_DIR = Path("/home/ubuntu/lab-riscv/hermesa3/releases")
VERSION_FILE = PERSONA_DIR / "VERSION"

# ─── ✅ 要放進分身的核心資料 ──────────────────────────────
CORE_DATA = [
    "tw_persona_1069.json",
    "population_by_region_age_sex_2025.csv",
    "tw-persona-db-rfc.md",
    "qualified-memory.md",
    "VERSION",
]

# ─── ✅ 要放進分身的工具腳本 ──────────────────────────────
TOOLS = [
    "query_persona.py",
    "sample_stratified.py",
]

# ─── ✅ Pro 版本多出來的檔案 ──────────────────────────────
PRO_EXTRA = [
    "_generate_997.py",
    "qa_validate.py",
    "occ_prob_real.py",
    "marriage_prob_real.py",
]

# ─── Pro 版多出來的 scripts ──────────────────────────────
PRO_EXTRA_SCRIPTS = [
    "persona_contradiction_check.py",
    "persona_review.py",
    "persona_review_deep.py",
    "verify_economic_tone.py",
]

# ─── ❌ 絕對不放的檔案（Standard）────────────────────────
# Pro 版會從這個清單移除 _generate_997.py 和 qa_validate.py
BASE_EXCLUDE = {
    "export_qualified_memory.py", # 你的 release 工具
    "BUSINESS-MODEL.md",          # 內部商業模式
    "MILESTONE-v3.0.md",          # 內部迭代記錄
    "MILESTONE_v0.1.md",          # 內部
    "analysis_report_112.md",     # 內部品質分析
    "stats_report.py",            # 內部
    "stats_report_20260710.md",   # 內部
    "persona_childcare_card.json", # 已交付 sample
    "_debug_api.py",              # debug 工具
    "_fetch_family_size.py",      # 內部
    "_find_top10.py",             # 內部
    "etlPopulation.py",           # 內部
    "ris-opendata-apidoc.json",   # API 文件
    "tw_persona_997.json",        # 舊版
    "tw_persona_112_stratified.json",  # 內部樣本
    "tw_persona_prototype_001_v3.json", # prototype
    "tw_persona_prototype_002_engineer.json",
    "tw_persona_top10.json",
    "appliance-checklist.md",     # 這是你的內部文件
    "appliance-pro-deliverable.md", # 內部比對文件
}

# ─── ✅ 要放進分身的 skill references ────────────────────
INCLUDE_REFS = [
    "dimension-definitions.md",
    "name-pool-architecture.md",
    "economic-context-sentences.md",
    "city-occupation-boost.md",
    "household-income-by-city.md",
    "residence-price-index.md",
    "language-standards.md",
    "price-consumption-data.md",
    "qualified-memory-convention.md",
    "96-sample-v3-review-2026-07-11.md",
]

INCLUDE_SCRIPTS = [
    "persona_review.py",
    "verify_economic_tone.py",
    "persona_contradiction_check.py",
]


def read_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "v3.0"


def write_readme(version: str) -> str:
    """產出 README.md 給甲方"""
    clean_v = version.lstrip("v")
    return f"""# TW Persona DB — Appliance {version}

> 1069 筆台灣人設資料庫查詢工具
> 產出日期: {datetime.now().strftime('%Y-%m-%d')}

## 這是什麼

一套 1069 筆人口加權台灣人設資料庫 + CLI 查詢工具。
18 維度結構化資料，涵蓋年齡/性別/區域/教育/職業/收入/政治/媒體/家庭/婚姻/興趣等。

## 系統需求

- Python 3.8+
- 無需網路連線（離線可查）
- 建議 4GB+ RAM（載入 1.4MB JSON 無壓力）

## 快速開始

```bash
# 1. 解壓縮
unzip persona-appliance-{version}.zip -d ~/persona-db/

# 2. 進入目錄
cd ~/persona-db

# 3. 開始查詢
python3 tools/query_persona.py --residence 台北市 --age 35-44 --occupation 科技
python3 tools/query_persona.py --list-dimensions
python3 tools/query_persona.py --residence 台中市 --politics 泛綠 --top 5
```

## 常用查詢範例

| 目標 | 指令 |
|:-----|:-----|
| 查選區分布 | `python3 tools/query_persona.py --residence 台中市 --age 30-44 --politics 泛綠` |
| 查展店客群 | `python3 tools/query_persona.py --residence 高雄市 --income >8萬 --family_size 3+` |
| 查金融商品 | `python3 tools/query_persona.py --age 25-40 --occupation 科技/金融 --marriage 未婚` |
| 列出所有維度 | `python3 tools/query_persona.py --list-dimensions` |
| 模糊搜尋職業 | `python3 tools/query_persona.py --occ ~工程` |
| 只看前 3 筆 | `上列指令加 --top 3` |

## 18 維度速查

| # | 維度 | 合法值 |
|---|------|--------|
| 1 | age | 0-11 / 12-18 / 19-24 / 25-34 / 35-44 / 45-54 / 55-64 / 65+ |
| 2 | sex | 男 / 女 |
| 3 | region | 都會區(六都) / 北部 / 中部 / 南部 / 花東 / 離島 |
| 4 | education | 國中以下 / 高中 / 大學 / 研究所以上 |
| 5 | occupation | 學生 / 科技 / 服務 / 製造 / 教育 / 醫療 / 公務 / 自營 / 家管 / 退休 / 其他 |
| 6 | personal_income | <3萬 / 3-8萬 / >8萬 / 無收入 |
| 7 | politics | 泛綠 / 泛藍 / 白/第三勢力 / 無政治傾向 |
| 8 | media_diet | 家長主導 / 兒童內容為主 / 傳統媒體為主 / 社群為主 / 混合 / 國際來源 |
| 9 | family_size | 1 / 2 / 3 / 4 / 5+ |
| 10 | family_income | <1萬 / 1-3萬 / 3-7萬 / 7萬 / 百萬 |
| 11 | hobby | 打電動 / 追劇 / 閱讀 / 登山 / 游泳 / 球類 / 逛街購物 / 烹飪 / 園藝 / 泡茶 / 下棋 / 打牌 / 繪畫 / 音樂 / 廣場舞 |
| 12 | marriage | 未婚 / 已婚 / 離婚 / 鰥寡 |
| 13 | residence | 台北市 ~ 連江縣（22 縣市） |
| 14-18 | 政治立場/議題/物價/所得級 | 見 RFC |

## 已知限制

1. **小縣市人少**：新竹市 ~1.9%、離島 ~1.1%、金門 ~0.3%。極端組合（新竹市+45-54+科技+4口）可能回 0。請放寬 region 條件。
2. **職業加成**：新竹縣/市 30%→科技、台北市 20%→金融、桃園市 20%→製造。這是基於實際產業分布。
3. **物價/所得分級**：依據 DGBAS 官方數據，參見 RFC 及 references。
4. **背景故事為模板生成**：可能出現經濟語氣不一致（如「手頭寬鬆」+「收入低」），屬已知 issue，本尊持續改善中。

## 更新方式

當有 major release 時（如 v3.2 → v4.0），會收到通知：

```bash
# 下載新版 ZIP
# 解壓縮覆蓋
unzip -o persona-appliance-v4.0.zip -d ~/persona-db/

# 或使用自動更新腳本
bash tools/auto-import-qualified.sh persona-appliance-v4.0.zip
```

## 聯絡與支援

- **日常操作問題**：先查 FAQ.md 和 qualified-memory.md
- **資料品質問題 / major upgrade 需求**：聯絡 Kuo-Shou（類心理師方案，NT$3,000/hr）
- bug fix（v{version} 範圍內含 3 個月修正支援）

---

_文件版本: v{version} | 產出時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}_
"""


def write_faq() -> str:
    """產出 FAQ.md 給甲方"""
    return """# TW Persona DB Appliance — 常見問題 (FAQ)

## Q: 查詢回 0 筆怎麼辦？

**最常見原因**：組合太細，人口權重不足。

解法：
```bash
# 原本（太細，可能回 0）
python3 query_persona.py --residence 新竹市 --age 45-54 --occupation 科技 --family_size 4

# 放寬 region（新竹市人口僅 ~1.9%）
python3 query_persona.py --residence 新竹縣 --age 45-54 --occupation 科技

# 或放寬年齡
python3 query_persona.py --residence 新竹市 --age 35-54 --occupation 科技
```

如果所有條件都放寬還是 0，那就是這個組合在真實人口中真的極少。

---

## Q: 為什麼台北市的 persona 這麼多？離島這麼少？

這是**人口加權抽樣**的結果。1069 筆的分配比例 = 真實台灣人口比例：
- 台北市 ~11% → ~118 筆
- 離島（澎湖/金門/連江）合計 ~1.5% → ~16 筆

不是遺漏，是人口比例如此。

---

## Q: 這份資料跟真實政府統計差多少？

| 項目 | 誤差 |
|:-----|:----:|
| 年齡分布 | ≤ 0.3% |
| 區域分布 | ≤ 0.4% |
| 性別比 | 49.7:50.3（實際 49.5:50.5） |
| 縣市覆蓋 | 22/22 |
| 資料源 | 7 個官方統計（ODRP014、DGBAS、主計總處、內政部） |

---

## Q: 我可以自己加資料或改資料嗎？

可以。`data/tw_persona_1069.json` 是標準 JSON 格式。
- 要新增維度：直接在 JSON 的 dimensions 加欄位
- 要修改 prompt：編輯對應欄位
- 建議保留原始備份

注意：自行修改後，本尊後續的 qualified memory 更新可能與你的修改衝突。

---

## Q: 我可以把資料嵌入我的網站或服務嗎？

可以。`tw_persona_1069.json` 是永久授權，可用於商業產品內部。
- 不可轉售原始資料
- 不可再授權給第三方
- 基於資料分析的衍生結果（報表、圖表）不受限制

---

## Q: 跟傳統外包建人設資料庫差在哪？

| 項目 | 這個 Appliance | 傳統外包 |
|:-----|:--------------|:---------|
| 價格 | NT$XX,000 一次 | NT$80K-150K |
| 筆數 | 1069 | 500-1000 |
| 維度 | 18 | 8-12 |
| 品質驗證 | 20 條 QA 規則 | 通常無系統驗證 |
| 查詢工具 | CLI 即時查詢 | 通常只給 Excel |
| 迭代能力 | 可自行擴充 | 全部重做 |

---

## Q: 什麼情況下該找 Kuo-Shou？

**建議找她：**
- major version upgrade（v3.x → v4.0）
- 需要疊加全新維度（如選舉投票紀錄、消費偏好）
- 發現資料有系統性錯誤
- 需要完全重建（如日本版、越南版）

**不用找她：**
- query 回 0 筆（先放寬條件）
- 想改 prompt 文案（自行編輯 JSON）
- 基本操作問題（先看 README 和 qualified-memory.md）

---

## Q: 更新會不會把我的修改蓋掉？

`auto-import-qualified.sh` 只會覆蓋：
- `data/tw_persona_1069.json`
- `skills/tw-persona-db/`
- `tools/*.py`

不會動到你自己新增或修改的檔案。如果不放心，更新前先備份 `data/` 目錄。

---

## Q: 我可以不用 Hermes Agent，直接用 query_persona.py 嗎？

**可以。** query_persona.py 是獨立 Python 腳本，不需要 Hermes Agent。
只需要 Python 3 標準函式庫（json、csv、argparse、collections）。

這也是為什麼把它包成 CLI 而不是 Hermes skill 的 main 介面——低依賴，高可攜。

---

## Q: prompt_prefix 和 reference_pre_prompt 有什麼差？

- **prompt_prefix**：角色扮演用。餵給 LLM 讓它扮演該 persona 回答問卷。
- **reference_pre_prompt**：結構化摘要。GEO 操作員（你）過濾查詢用。

兩個都是同一 persona 的不同呈現方式。

---

## Q: 為什麼有些背景故事看起來怪怪的？

背景故事是模板引擎生成的（3 組模板池隨機組合），已知可能出現：
- 經濟語氣不一致（bg 說寬鬆、pre 說緊）
- 65+ persona 用「小孩」而不是「子女」
- 喪偶+family>1 仍說「一個人過日子」

這些是本尊持續迭代改善中的項目。如果你看到讓你在意的新 pattern，可以回報給 Kuo-Shou。

---

_最後更新: {datetime.now().strftime('%Y-%m-%d')}_
"""


def write_api_server() -> str:
    """簡易 Flask API wrapper（可選）"""
    return r'''#!/usr/bin/env python3
# api_server.py - optional REST API wrapper for querying personas via HTTP

# Usage:
#     pip install flask
#     python3 api_server.py              # start at http://0.0.0.0:5050
#     python3 api_server.py --port 8080  # custom port

# API:
#     GET /api/persona?residence=Taipei&age=35-44&occupation=tech
#     GET /api/persona/:id               # lookup by ID
#     GET /api/dimensions                # list all valid dimensions
#     GET /api/stats                     # basic statistics

# Response format: JSON

import argparse
import json
import sys
from pathlib import Path

app = None
data = []
dimensions_index = {}


def load_data():
    global data, dimensions_index
    data_path = Path(__file__).parent.parent / "data" / "tw_persona_1069.json"
    if not data_path.exists():
        print(f"Cannot find data: {data_path}")
        sys.exit(1)
    with open(data_path) as f:
        data = json.load(f)
    dims = set()
    for p in data:
        for k in p["dimensions"]:
            dims.add(k)
    dimensions_index = sorted(dims)


def match_persona(params):
    """支援的 filter keys 等同 query_persona.py"""
    results = []
    for p in data:
        d = p["dimensions"]
        match = True
        for k, v in params.items():
            if k == "top":
                continue
            if k == "occ":
                # fuzzy match
                if v not in d.get("occupation", ""):
                    match = False
                    break
            elif k in d:
                if str(v) != str(d[k]):
                    match = False
                    break
            else:
                match = False
                break
        if match:
            results.append(p)
    top = int(params.get("top", 0))
    if top and top < len(results):
        results = results[:top]
    return results


def start_server(port=5050):
    try:
        from flask import Flask, jsonify, request
    except ImportError:
        print("❌ 需要 flask: pip install flask")
        sys.exit(1)

    global app
    app = Flask(__name__)
    load_data()

    @app.route("/api/persona", methods=["GET"])
    def query_personas():
        params = {k: v for k, v in request.args.items()}
        results = match_persona(params)
        return jsonify({"count": len(results), "results": results})

    @app.route("/api/dimensions", methods=["GET"])
    def list_dimensions():
        return jsonify({"dimensions": sorted(dimensions_index)})

    @app.route("/api/stats", methods=["GET"])
    def stats():
        return jsonify({
            "total": len(data),
            "version": "v3.2",
        })

    print(f"🚀 API server 啟動在 http://0.0.0.0:{port}")
    print(f"   範例: curl 'http://localhost:{port}/api/persona?residence=台北市&age=35-44'")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Persona DB API Server")
    parser.add_argument("--port", type=int, default=5050, help="Port (default: 5050)")
    args = parser.parse_args()
    start_server(port=args.port)
'''


def write_query_examples() -> str:
    """query 範例 shell script"""
    return r"""#!/bin/bash
# query-examples.sh — 常用查詢範例
# 用法: bash query-examples.sh

QUERY="python3 tools/query_persona.py"

echo "╔══════════════════════════════════════════════╗"
echo "║  TW Persona DB — 常用查詢範例               ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

echo "=== 1. 台北市 35-44 歲科技業 ==="
$QUERY --residence 台北市 --age 35-44 --occupation 科技 --top 3

echo ""
echo "=== 2. 台中市 30-44 歲泛綠選民 ==="
$QUERY --residence 台中市 --age 30-44 --politics 泛綠 --top 3

echo ""
echo "=== 3. 高雄市高收入有家庭 ==="
$QUERY --residence 高雄市 --income ">8萬" --family_size "3+" --top 3

echo ""
echo "=== 4. 全台 25-40 未婚科技/金融 ==="
$QUERY --age 25-34 --age 35-44 --marriage 未婚 --occ ~工程 --occ ~金融 --top 5

echo ""
echo "=== 5. 新竹市科技業（測試城市加成） ==="
$QUERY --residence 新竹市 --occupation 科技 --top 5

echo ""
echo "=== 6. 列出所有可用維度 ==="
$QUERY --list-dimensions
"""


def build_appliance(version: str, with_api: bool = False, dry_run: bool = False, pro: bool = False) -> Path | None:
    """打包 persona appliance zip"""
    label = "Pro" if pro else "Standard"
    if dry_run:
        suffix = "-pro" if pro else ""
        print(f"🧪 [DRY RUN] 將產出 persona-appliance{suffix}-{version}.zip ({label})")
        print(f"   核心資料: {len(CORE_DATA)} 檔")
        print(f"   工具: {len(TOOLS)} 檔")
        print(f"   Skill refs: {len(INCLUDE_REFS)} 檔")
        print(f"   Skill scripts: {len(PRO_EXTRA_SCRIPTS) if pro else len(INCLUDE_SCRIPTS)} 檔")
        print(f"   含 API server: {with_api}")
        if pro:
            print(f"   Pro extra: {len(PRO_EXTRA)} 檔 (含 generate engine)")
        return None

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "-pro" if pro else ""
    zip_path = OUTPUT_DIR / f"persona-appliance{suffix}-{version}.zip"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # — README.md —
        (tmp / "README.md").write_text(write_readme(version), encoding="utf-8")

        # — FAQ.md —
        (tmp / "FAQ.md").write_text(write_faq(), encoding="utf-8")

        # — VERSION —
        (tmp / "VERSION").write_text(version + "\n")

        # — data/ —
        data_dir = tmp / "data"
        data_dir.mkdir()
        for fname in CORE_DATA:
            src = PERSONA_DIR / fname
            if src.exists():
                shutil.copy2(src, data_dir / fname)
            else:
                print(f"  ⚠️ 找不到 {fname}，跳過")

        # — tools/ —
        tools_dir = tmp / "tools"
        tools_dir.mkdir()
        for fname in TOOLS:
            src = PERSONA_DIR / fname
            if src.exists():
                shutil.copy2(src, tools_dir / fname)
        # auto-import-qualified.sh
        import_src = PERSONA_DIR / "auto-import-qualified.sh"
        if import_src.exists():
            shutil.copy2(import_src, tools_dir / "auto-import-qualified.sh")
        # api_server.py (optional)
        if with_api:
            (tools_dir / "api_server.py").write_text(write_api_server(), encoding="utf-8")

        # — Pro 版額外檔案（generate engine + QA）—
        if pro:
            for fname in PRO_EXTRA:
                src = PERSONA_DIR / fname
                if src.exists():
                    # _generate_997.py → tools/ ; 資料檔 → data/
                    if fname.endswith(".py"):
                        shutil.copy2(src, tools_dir / fname)
                    else:
                        shutil.copy2(src, data_dir / fname)
                else:
                    print(f"  ⚠️ 找不到 {fname}，跳過")

        # — samples/query-examples.sh —
        samples_dir = tmp / "samples"
        samples_dir.mkdir()
        (samples_dir / "query-examples.sh").write_text(write_query_examples(), encoding="utf-8")
        # chmod via os
        os.chmod(samples_dir / "query-examples.sh", 0o755)

        # — skills/tw-persona-db/ —
        skill_target = tmp / "skills" / "tw-persona-db"

        # SKILL.md — Standard 用精簡版，Pro 用完整版
        if SKILL_DIR.exists():
            full_skill = SKILL_DIR / "SKILL.md"
            if full_skill.exists():
                skill_content = full_skill.read_text(encoding="utf-8")
                skill_target.mkdir(parents=True)
                if pro:
                    # Pro 版保留完整 SKILL（含 generation/QA methodology）
                    (skill_target / "SKILL.md").write_text(skill_content, encoding="utf-8")
                else:
                    # Standard 瘦身：移除內部迭代細節
                    simplified = _simplify_skill(skill_content)
                    (skill_target / "SKILL.md").write_text(simplified, encoding="utf-8")

            # references (精選)
            ref_src = SKILL_DIR / "references"
            if ref_src.exists():
                ref_target = skill_target / "references"
                ref_target.mkdir()
                for ref_name in INCLUDE_REFS:
                    ref_path = ref_src / ref_name
                    if ref_path.exists():
                        shutil.copy2(ref_path, ref_target / ref_name)

            # scripts（Pro版用完整清單，Standard用精選）
            scr_src = SKILL_DIR / "scripts"
            if scr_src.exists():
                scr_target = skill_target / "scripts"
                scr_target.mkdir()
                script_list = PRO_EXTRA_SCRIPTS if pro else INCLUDE_SCRIPTS
                for scr_name in script_list:
                    scr_path = scr_src / scr_name
                    if scr_path.exists():
                        shutil.copy2(scr_path, scr_target / scr_name)

        # — ZIP —
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in tmp.rglob("*"):
                if f.is_file():
                    arcname = f.relative_to(tmp)
                    zf.write(f, arcname)

    size_kb = zip_path.stat().st_size / 1024
    print(f"✅ persona-appliance-{version}.zip 已產出")
    print(f"   大小: {size_kb:.1f} KB")
    print(f"   路徑: {zip_path}")
    return zip_path


def _simplify_skill(content: str) -> str:
    """從 SKILL.md 中移除內部迭代細節，保留甲方需要的部分"""
    lines = content.split("\n")
    simplified = []
    keep = True
    for line in lines:
        # 跳過 pro review pipeline 的實作細節
        if "Sub-agent Finding Verification Pattern" in line:
            keep = False
        if "### Consistency Enforcement" in line:
            keep = False
        if "### Variable Scoping Trap" in line:
            keep = False
        if "### Chinese Semantic Tone Mismatches" in line:
            keep = False
        if "### Realism Enforcement" in line:
            keep = False
        if "## Deployed Configuration" in line:
            keep = False
        if "## Privacy Model" in line:
            keep = False
        if "## User's Quality Standards" in line:
            keep = False
        if "## Quick Start for Agent" in line:
            keep = False

        if keep:
            simplified.append(line)

        # 重新開啟 keep 的 section 結束標記
        if line.strip().startswith("## ") or line.strip().startswith("---"):
            keep = True

    # 保留核心 sections
    result = "\n".join(simplified)

    # 確保至少有核心內容
    if len(result) < 1000:
        # fallback: 回傳完整版
        return content

    return result


def main():
    parser = argparse.ArgumentParser(description="打包 persona DB appliance（分身）")
    parser.add_argument("--version", help="指定版號，預設從 VERSION 讀取")
    parser.add_argument("--with-api", action="store_true", help="含簡易 API server")
    parser.add_argument("--pro", action="store_true", help="Pro 版（含 generate engine + QA）")
    parser.add_argument("--dry-run", action="store_true", help="試跑，不產檔案")
    args = parser.parse_args()

    version = args.version or read_version()
    version = version.lstrip("v")  # remove leading v if present
    version = f"v{version}"  # ensure exactly one v
    label = "Pro" if args.pro else "Standard"
    print(f"🔧 打包分身 {version} ({label})")

    if args.dry_run:
        print(f"   含 API server: {args.with_api}")

    zip_path = build_appliance(version, with_api=args.with_api, dry_run=args.dry_run, pro=args.pro)

    if zip_path:
        print(f"\n🚀 交付步驟 ({label}):")
        print(f"   1. 交付 {zip_path} 給甲方")
        print(f"   2. 安排交接會議 (1-2hr)")
        print(f"   3. 展示 query CLI + 維度結構 + 已知限制")
        print(f"\n📋 檔案清單:")
        with zipfile.ZipFile(zip_path) as zf:
            for f in zf.namelist():
                info = zf.getinfo(f)
                print(f"   {f}  ({info.file_size:>8,} bytes)")


if __name__ == "__main__":
    main()
