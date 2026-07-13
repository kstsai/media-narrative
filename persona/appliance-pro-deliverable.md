# TW Persona DB — Standard vs Pro 交付對照
# 讓甲方選擇，附完整警告

---

## 🆚 方案對照表

| 項目 | Standard | Pro |
|:-----|:--------:|:---:|
| **價格** | **NT$60K-80K** | **NT$120K-150K** |
| `tw_persona_1069.json`（最新資料） | ✅ | ✅ |
| `query_persona.py`（唯讀查詢 CLI） | ✅ | ✅ |
| `sample_stratified.py`（抽樣檢視） | ✅ | ✅ |
| `tw-persona-db-rfc.md`（規格文件） | ✅ | ✅ |
| `qualified-memory.md`（24 條知識） | ✅ | ✅ |
| `FAQ.md` + `README.md` | ✅ | ✅ |
| `skills/tw-persona-db/`（精選 refs） | ✅ | ✅ |
| `_generate_997.py`（**重新生成引擎**） | ❌ | ✅ |
| `qa_validate.py`（20 條 QA 規則） | ❌ | ✅ |
| 完整 script 目錄（review/contradiction/etc） | ❌ | ✅ |
| 交接會議 | 1 次（1hr） | **2 次（共 3hr）** |
| 版本更新（major upgrade） | 類心理師 NT$3K/hr | 類心理師 NT$3K/hr |
| **使用限制** | 不可 self-generate | 可 self-generate |

---

## 📦 Pro 版多出來的檔案

### 放進 Pro 的額外檔案

| 檔案 | 大小 | 用途 | 風險等級 |
|:-----|:----:|:-----|:--------:|
| `_generate_997.py` | 55 KB | **重新生成 1069 筆 persona 的引擎** | 🔴 核心 IP |
| `qa_validate.py` | 11 KB | 20 條自動化品質驗證 | 🟢 必要配套 |
| `scripts/persona_contradiction_check.py` | 8.4 KB | 10-check 矛盾檢測 | 🟢 |
| `scripts/persona_review.py` | 9.5 KB | 自動化審查 | 🟢 |
| `scripts/persona_review_deep.py` | 4.4 KB | 深層審查 | 🟢 |
| `scripts/verify_economic_tone.py` | 4.6 KB | 經濟語氣驗證 | 🟢 |
| `occ_prob_real.py` | 2.9 KB | DGBAS 真實職業機率表 | 🟡 原始數據 |
| `marriage_prob_real.py` | 2.9 KB | 婚姻狀態機率表 | 🟡 原始數據 |
| `population_by_region_age_sex_2025.csv` | 7.2 KB | 人口權重（已含在 Standard） | 🟢 |

### 仍不放的檔案（你的核心護城河）

| 檔案 | 原因 |
|:-----|:------|
| `export_qualified_memory.py` | 你的 release 系統，不是她的工具 |
| `build_appliance.py` | 你的打包腳本 |
| `appliance-checklist.md` | 你的內部文件 |
| `BUSINESS-MODEL.md` | 商業模式內部討論 |
| `MILESTONE-*.md` | 迭代記錄 |
| `analysis_report_*.md` | 內部品質報告 |
| `stats_report.py` | 內部統計 |

---

## ⚠️ 必須對甲方說明的 7 項警告

以下是你在交接會議上必須講清楚的內容。建議逐條說明。

---

### ⚠️ 警告 1：重新生成 ≠ 品質保證

```
你以為：按 enter → 新的 1069 筆產出 → 品質跟 v3.1 一樣好
事實：按 enter → 新的 1069 筆產出 → 品質跟 v1.5 一樣爛
```

每一個 bug fix 都沒有寫在 generate script 的程式邏輯裡——它們寫在 **QA 規則** 和 **你的 iteration 經驗** 裡。

舉例：你花了 3 輪 iteration 才發現「含飴弄孫 + 低收入」有中文語感矛盾。這不是 code bug，是 domain knowledge bug。她重新 generate 後，這個問題會立刻回來。

**對策：每次 regenerate 後，必須執行完整 QA pipeline。**

```bash
python3 qa_validate.py          # 20 rules, exit code 0 才算 pass
python3 scripts/verify_economic_tone.py  # 經濟語氣比對
python3 sample_stratified.py    # 抽樣檢視
python3 scripts/persona_review_deep.py   # 深層審查
```

---

### ⚠️ 警告 2：QA 20 條只擋已知的坑

QA 規則的設計原則是：**每踩一個坑，就加一條 rule。**

所以 QA 20 條 = 我們踩過的 20 個坑。**她可能會踩到第 21 個、第 22 個。**

如果她發現 QA 全部通過，但 reviewer 覺得某個人設怪怪的——那是她發現了新的 pattern，應該要：
1. 回報給你
2. 你決定要不要加 R21
3. 更新到下一版 release

---

### ⚠️ 警告 3：不建議修改 `_generate_997.py` 的核心邏輯

script 裡有：
- 機率表（occupation、income、marriage）
- 城市職業加成（OCC_CITY_BOOST）
- 模板池（命名、背景故事）
- coherence 邏輯

**動任何一個，都可能產生蝴蝶效應。**

如果她想加新維度、改機率、調模板——那是 L2/L3 服務等級，建議走類心理師方案，由你來改。

| 她想做的事 | 建議作法 |
|:----------|:---------|
| 改機率表（如提高某個職業比例） | 走類心理師，你改 |
| 加新維度（如選舉投票紀錄） | 走類心理師，你疊加 |
| 微調 prompt 文案 | 她可以直接 edit JSON |
| 重新 generate（相同參數） | 她自己跑 |
| 加入新的職業類別 | 走類心理師，你擴充 |
| 修改命名池 | 走類心理師，你改 |
| 只改 seed 重跑看看差異 | 她自己跑，但要跑 QA |

---

### ⚠️ 警告 4：每次 regenerate 都是不同結果

seed=42 是固定的，但如果她改 seed 或改 TARGET，產出的 1069 筆人設會完全不同。

這不是 bug，是隨機抽樣的特性。**同一組參數跑兩次，名字和背景故事會不一樣，但分布統計會一致。**

如果她需要 reproducible 的結果，保持 seed=42。

---

### ⚠️ 警告 5：自行修改後的版本，無法直接 merge 官方 release

```
v3.1（官方）      → 她改了一部分    → 她手上是 v3.1-modified
v3.2（官方 release） → 她想 merge → 衝突！她改過的跟自己 overwrite 打架
```

**解法：**
- 她自訂的版本保留一份備份（如 `tw_persona_1069_custom.json`）
- 官方 release 覆蓋 `tw_persona_1069.json`
- 她需要的客製化改動，手動 merge 到新版
- 或者，走類心理師方案請你幫她做 diff + merge

---

### ⚠️ 警告 6：generate script 不可轉售

合約裡要寫明：

> `_generate_997.py` 及其所含的機率表、模板池、coherence 邏輯，為 Kuo-Shou Tsai 的智慧財產。甲方可用於內部產品開發，不可轉售、再授權、或作為獨立產品販售給第三方。

這跟資料授權（可用於商業內部、不可轉售）一致。

---

### ⚠️ 警告 7：Pro 不是買斷服務，是買斷工具

Pro 版 NT$120K-150K 包含：
- 2 次交接會議（總計 3hr）
- 首年 minor bug fix（合理的 bug，非新功能）
- 完整的生產工具

**不包含：**
- 疊加新維度（如選舉投票紀錄）
- 重大架構改動（如新增國家版本）
- 客製化 domain 擴充
- 無限次數的諮詢

以上走類心理師方案 NT$3,000/hr。

---

## 📋 Pro 版建議議約條款

```
TW Persona DB Appliance Pro — 授權契約大綱

1. 授權標的
   1.1 1069 筆台灣人設資料庫（tw_persona_1069.json）
   1.2 查詢工具（query_persona.py）
   1.3 生成引擎（_generate_997.py）及相關腳本
   1.4 品質驗證工具（qa_validate.py）
   1.5 文件（RFC、qualified-memory、FAQ、README）
   1.6 skill（tw-persona-db）

2. 授權範圍
   2.1 甲方可用於內部產品開發及商業用途
   2.2 甲方可自行 regenerate persona 資料
   2.3 甲方可修改生成參數（seed、TARGET 等）供內部使用
   2.4 甲方不可將生成引擎及其組成部分轉售或再授權予第三方

3. 品質責任
   3.1 甲方自行 regenerated 的資料，其品質由甲方自行驗證
   3.2 乙方（Kuo-Shou）提供 qa_validate.py 作為驗證工具，但不擔保自行生成結果的品質
   3.3 乙方持續迭代官方版本，甲方可另行選購升級

4. 後續服務
   4.1 首年 minor bug fix 含在價內（合理的 script 錯誤修復）
   4.2 新功能開發、domain 疊加、major upgrade → 類心理師方案 NT$3,000/hr
   4.3 諮詢超過 2hr/月 後按類心理師計費

5. 價格
   NT$120,000-150,000 一次付清

6. 交付物
   同本文件第 3 節所列全部檔案 + 2 次交接會議
```

---

## 🎯 給你的話術（跟她說明時用）

**開場：**

> 「Standard 版給你查詢工具，Pro 版給你生產工具。差異是我的生成引擎——你可以在自己的環境重新跑 1069 筆人設，不用每次都等我。」

**講警告時（不要嚇到她，要讓她覺得被保護）：**

> 「但我要老實跟你說：重新 generate 跟打開查詢工具不一樣。品質不是按 enter 就保證的。我花了一個月 iteration 才從 v1.5 到 v3.1——你第一次 regenerate，品質大概會回到 v1.5。我把 QA 工具和 iteration 方法都教給你，你可以在自己的節奏上慢慢 refine。」

**結尾：**

> 「Standard 版適合『我要用這個資料』。Pro 版適合『我要自己長出資料的能力』。看你現在的階段適合哪個。」

---

## 📦 Pro 版打包

執行以下指令產出 Pro 版 appliance：

```bash
cd ~/lab-riscv/hermesa3/persona
python3 build_appliance.py --pro --version v3.2
```

（`build_appliance.py` 新增 `--pro` flag 後會自動加入 generate script、QA script、完整 scripts 目錄、交接文件）
