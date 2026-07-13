# TW Persona DB — Transfer 方案

> **最終版** — 2026-07-13
> 取代舊版 `BUSINESS-MODEL.md`（方案 A/B/C/D 已整併）

---

## 一句話

> NT$60K-80K 賣斷，全部 tool 移交。甲方可自行 iterate 改進資料、可賣改進後的 1069.json。不可轉售 tool 本身。要我們 main branch 的新升級另計。

---

## 交付內容

```
Transfer 方案 v3.2（NT$60K-80K 賣斷）
├── data/
│   ├── tw_persona_1069.json      ← 1,069 筆，18 維度
│   ├── tw-persona-db-rfc.md      ← 規格文件
│   ├── qualified-memory.md       ← 24 條 domain knowledge
│   └── population_by_region_age_sex_2025.csv
├── tools/
│   ├── query_persona.py          ← 查詢 CLI
│   ├── _generate_997.py          ← 重新生成引擎 🔑
│   ├── qa_validate.py            ← 23 條 QA 規則 🔑
│   ├── occ_prob_real.py          ← DGBAS 真實職業機率
│   ├── marriage_prob_real.py     ← MOI 真實婚姻機率
│   ├── sample_stratified.py      ← 分層抽樣
│   └── auto-import-qualified.sh  ← 更新腳本
├── skills/tw-persona-db/
│   ├── SKILL.md                  ← 完整文件（含 methodology）
│   ├── references/               ← 維度/物價/所得/語言標準
│   └── scripts/                  ← 審查/驗證工具
├── samples/query-examples.sh     ← 常用查詢
├── README.md + FAQ.md            ← 快速入門
└── VERSION                       ← v3.2
```

---

## ⚠️ 品質免責聲明

**直接跑 `_generate_997.py` 不會產出 v3.2 品質。**

v3.2 的品質是透過 **900+ 則對話迭代** 打磨出來的：

```
v1.5  →  9 條 QA rules, 997 筆   ← 起點
         ↓
     900+ 則 #persona-db-dev 對話
         ↓ 每踩一個坑加一條 rule
         ↓ 每發現一個矛盾修一次模板
         ↓ 每輪 Pro review 驗收品質
         ↓
v3.2  →  23 條 QA rules, 1069 筆  ← 交付版本
```

_generate_997.py 本身沒有記錄這些 iteration——它們寫在 QA rules、模板池優化、經濟語氣對齊、連貫性修復裡。如果不跑 `qa_validate.py` 和 review scripts 就直接出貨，品質約等於 v1.5 水準。

**QA 工具和方法論交接的價值就在這裡**——你買的不只是 script，是知道「什麼時候該信 QA、什麼時候該人工看」的判斷力。

## 授權條款

| 項目 | 允許 | 不允許 |
|:-----|:----|:-------|
| 使用資料 | ✅ 可用於商業產品內部 | ❌ 不可轉售 tool 本身 |
| 改進資料 | ✅ 可自行 iterate、改進 1069.json | ❌ 不可轉售 `_generate_997.py` 等 |
| 販售成果 | ✅ **可賣改進後的 1069.json** | ❌ 不可作為獨立 tool 轉售 |
| 重新生成 | ✅ 可用 `_generate_997.py` 自行 regenerate | |
| 修改參數 | ✅ 可改 seed、TARGET 等參數 | |
| 子授權 | | ❌ 不可再授權予第三方 |

---

## 後續升級（另計）

甲方需要我們 main branch 的新版本時：

```
費率：NT$2,000/hr
計費：依 actual session log，透明可查
估算：一般 major upgrade 約 3 工作時 ≈ NT$6,000

實際範例（7/11-7/13）：
  7/11 六  5.7h  v3.0核心架構→v3.1擴充→65+自然化→2輪Pro review
  7/12 日  1.6h  真實OCC/MARRIAGE數據→QA R19-R20
  7/13 一  2.8h  v3.7全量驗證→6×Pro review→186次修正→QA R21-R23
  ────────────────────────────────────────
  合計     10.1h  v1.5→v3.7, 23 QA rules, 1069 personas
                        → NT$20,200（10.1h × NT$2,000/hr）
```

每次 upgrade 完會產出 `WORKLOG-YYYY-MM-DD.md`，內含：
- 每個時間段的具體工作內容
- 對應的 git commit
- 產出檔案一覽
- 工時與金額總結

---

## 與傳統方案對比

| | 傳統外包 | Transfer |
|:--|:---------|:---------|
| 價格 | NT$80K-150K | **NT$60K-80K** |
| 筆數 | 500-1,000 | **1,069** |
| 維度 | 8-12 | **18** |
| 品質驗證 | 通常無系統驗證 | **23 條 QA 規則自動化** |
| 是否可自行 iterate | ❌ 不行 | ✅ 完全可 |
| 是否可自行 regenerate | ❌ 不行 | ✅ 完全可 |
| 是否可賣改進後的資料 | ❌ 版權問題 | ✅ 允許 |
| 後續升級 | 全部重做 | NT$2,000/hr 按 session log |

---

## 關係

- 我們保留 main branch 持續迭代
- 甲方自行開發改進，與我們各自獨立
- 甲方需要我們的更新 → 類心理師方案 NT$2,000/hr
- 我們的 iteration 工作量依 actual session log 量化計費
- 乙方無 ongoing 維護義務

---

_文件版本: v1.0 | 最後更新: 2026-07-13_
