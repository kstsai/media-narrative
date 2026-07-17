# Persona Database — Transfer Delivery

> **版本**: v3.2 | **資料**: 1069 筆人設 | **種子**: 42
> **交付日期**: 2026-07-15
> **授權模式**: Transfer 方案 — 詳見 `TRANSFER-MODEL.md`

---

## 什麼是 Persona DB？

Persona DB 是台灣人口加權的**合成人設資料庫**，包含 1069 筆依真實人口統計分布生成的虛擬人物。每個人設涵蓋 18 個維度（年齡、性別、居住地、職業、收入、家庭、政治傾向、興趣等），並附有自然中文的 prompt_prefix（角色扮演用）和 structured reference_pre_prompt（篩選用）。

### 應用場景

- **市場研究** — 找出目標客群的合成樣本進行問卷模擬
- **店點選址** — 模擬不同區域 persona 對展店策略的反應
- **品牌能見度** — 測試 LLM 在不同 persona 查詢下會推薦哪些品牌
- **產品設計** — 驗證產品功能對 target persona 的吸引力
- **民意探索** — 了解不同人口群體對議題的可能看法

---

## 硬體需求

### KVM 主機最低需求

| 規格 | 建議值 | 備註 |
|:-----|:-------|:------|
| **CPU** | 4 cores, x86_64 | 支援 virtualization (vmx/svm) |
| **RAM** | 8 GB | 12+ GB 更佳 |
| **儲存** | 40 GB 可用空間 | SSD 佳，NVMe 尤佳 |
| **網路** | 對外連線 | 首次 setup 需下載套件 |
| **OS** | Ubuntu 22.04/24.04 LTS | 其他 Linux 發行版亦可 |

### 軟體需求

- Python 3.10+
- Git
- 可選：Hermes Agent（如要使用 skill-based 工作流）

---

## 安裝步驟

### 1. 下載 artifact

從 GitHub 下載：

```bash
git clone https://github.com/kstsai/persona-db.git
cd persona-db
```

或者直接下載 ZIP：

```bash
# 從 GitHub 下載
wget https://github.com/kstsai/persona-db/archive/refs/heads/main.zip
unzip main.zip
cd persona-db-main
```

### 2. 驗證完整性

```bash
# 檢查核心工具是否就位
ls -la \
  _generate_997.py \
  qa_validate.py \
  query_persona.py \
  tw_persona_1069.json

# 驗證資料完整性 (1069 筆)
python3 -c "import json; d=json.load(open('tw_persona_1069.json')); print(f'✅ {len(d)} personas, 22/{len(set(p[\"dimensions\"][\"residence\"] for p in d))} cities')"

# 執行 QA 驗證 (23 條規則全 PASS 才是正常)
python3 qa_validate.py
```

**預期輸出：**
```
✅ ALL CHECKS PASSED
```

### 3. 試跑查詢

```bash
# 列出所有可用的維度值
python3 query_persona.py --list-dimensions

# 查詢範例：台北市 35-44 歲科技業
python3 query_persona.py --residence 台北市 --age 35-44 --occ 科技 --top 3

# 查詢範例：新竹市 25-34 歲女性
python3 query_persona.py --residence 新竹市 --age 25-34 --sex 女 --top 5
```

### 4. 試跑 Generate（選擇性）

```bash
# 重新產生 1069 筆人設 (會覆蓋 tw_persona_1069.json)
python3 _generate_997.py

# 再次驗證
python3 qa_validate.py
```

### 5. (可選) 裝 Hermes Agent

如需使用 Skill-based 自動化工作流（委派 sub-agent 模擬、跨 session context 管理）：

請參考 [Hermes Agent 安裝說明](https://hermes-agent.nousresearch.com/docs)。

---

## 目錄結構

```
persona-db/
├── _generate_997.py           ← 人設生成引擎 (seed=42, TARGET=1069)
├── qa_validate.py             ← 23 條 QA 規則 (R1-R23)
├── query_persona.py           ← CLI 查詢工具
├── sample_stratified.py       ← 分層抽樣工具 (96 組合)
├── build_appliance.py         ← Appliance 打包腳本
├── export_qualified_memory.py ← 記憶匯出工具
├── occ_prob_real.py           ← DGBAS 真實職業機率表
├── marriage_prob_real.py      ← MOI 真實婚姻機率表
├── tw_persona_1069.json       ← 最終產出 (1.4MB, 1069 筆)
├── population_by_region_age_sex_2025.csv
├── tw-persona-db-rfc.md       ← RFC 規格文件
├── qualified-memory.md        ← 24 條 qualified knowledge
├── VERSION                    ← v3.2
├── LITE-MODEL.md              ← Lite 方案說明
├── TRANSFER-MODEL.md          ← Transfer 方案說明
├── UPGRADE-PRICING.md         ← 升級計費說明
├── README.md                  ← 本文件
├── scripts/                   ← 驗證腳本 (9 個)
│   ├── verify_chunk3.py       ←   單 chunk 10 項檢查
│   ├── verify_economic_tone.py←   經濟語氣一致性
│   ├── persona_review.py      ←   112 樣本審查 (5 類別)
│   ├── persona_review_deep.py ←   語意深層審查
│   ├── persona_contradiction_check.py
│   ├── gen_verification_report.py← 分布驗證報告
│   └── ...
├── references/                ← 參考文件 (34 份)
│   ├── residence-price-index.md
│   ├── household-income-by-city.md
│   ├── economic-context-sentences.md
│   ├── consolidated-pro-review-2026-07-13.md
│   ├── dgbas-manpower-survey-2024.md
│   ├── chunk2/3/4/5/6-contradiction-patterns.md
│   ├── hermes-session-context-management.md
│   ├── session-management-workflow.md
│   ├── persona-db-query-proposal.md
│   ├── skills/                ←   skill 參考
│   └── ...
├── worklogs/                  ← 工時記錄
│   ├── WORKLOG-2026-07-11-13.md
│   ├── WORKLOG-2026-07-14.md
│   ├── BANK-VISIBILITY-*.md
│   └── RAW-RESULTS-2026-07-14.md
├── concepts/                  ← 概念探索
│   └── persona-election-analysis.md
└── templates/
    └── auto-import-qualified.sh
```

---

## 常用指令

### 查詢 Persona

```bash
# 精確匹配
python3 query_persona.py --residence 新竹市 --occ 科技 --age 35-44

# 模糊匹配 (prefix ~)
python3 query_persona.py --occ ~工程

# 列出可用維度
python3 query_persona.py --list-dimensions

# 取前 N 筆
python3 query_persona.py --residence 台北市 --income ">8萬" --top 3
```

### 重新生成

```bash
python3 _generate_997.py
# → 覆蓋 tw_persona_1069.json
# → 需再跑 QA
python3 qa_validate.py
# → 產生分布報告
python3 scripts/gen_verification_report.py tw_persona_1069.json
```

### 品質管控

```bash
# QA 驗證 (23 條規則)
python3 qa_validate.py

# 分層抽樣 (96 組合)
python3 sample_stratified.py

# 抽樣審查
python3 scripts/persona_review.py tw_persona_112_stratified.json

# 分布驗證報告
python3 scripts/gen_verification_report.py tw_persona_1069.json
```

### 打包 Appliance

```bash
# Standard 版 (無 generate engine)
python3 build_appliance.py

# Pro 版 (含 generate + QA)
python3 build_appliance.py --pro
```

---

## 已知限制

| 限制 | 說明 |
|:-----|:------|
| **小城市覆蓋有限** | 新竹市 ~1.9%, 離島 ~1.1%。特定城市+年齡+職業組合可能回 0 |
| **查不到不代表不存在** | 只是該組合在 1069 筆中未抽到。放寬條件即可 |
| **Generate = 新一批人設** | 每次 regenerate 產生不同的名字和故事（seed=42 確保分布相同） |
| **She 卡不再找他** | `_generate_997.py` 已無 `/home/ubuntu/lab-riscv/` 硬編碼路徑，支援 `PERSONA_OUTPUT` env var |

---

## 授權條款摘要

本交付物採 **Transfer 方案**（詳見 `TRANSFER-MODEL.md`）：

| 可以做的事 | 不可以做的事 |
|:-----------|:-------------|
| ✅ 自行 iterate 改進 1069.json | ❌ 轉售 tool 本身 (_generate_997.py, qa_validate.py 等) |
| ✅ 販售您改進後的 1069.json | ❌ 將 tool 作為 SaaS 服務提供 |
| ✅ 內部產品開發使用 | ❌ 轉授權或再散布原始 tool |
| ✅ 要求 main branch 更新（另計費） | |

---

## 學習資源

| 文件 | 適合 |
|:-----|:------|
| `tw-persona-db-rfc.md` | 想了解架構設計 |
| `qualified-memory.md` | 24 條關鍵知識，快速上手 |
| `references/hermes-session-context-management.md` | 理解 Session 與 Context 管理 |
| `references/persona-db-query-proposal.md` | 如何用 GitHub Issues 查詢 Persona DB |
| `references/economic-context-sentences.md` | 經濟語氣邏輯 |
| `references/residence-price-index.md` | 各縣市物價分級 |
| `scripts/gen_verification_report.py` | 驗證產生品質 |
| `TRANSFER-MODEL.md` | 授權與商業條款 |
