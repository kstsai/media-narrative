# Milestone v3.0 — TW Persona Database

> 日期：2026-07-11
> 標籤：`persona-v3.0`
> Commit：`649ffc5`（最新）

---

## 摘要

從 v1.5 到 v3.0，歷經 4 輪 Pro review、15+ bug fixes、3 個新維度、QA 從 9 條擴充到 18 條。核心目標：**產出有品質的 persona db deliverable**，精進 iteration 方法與 review 驗證的可信度。

---

## 維度變更（v1.5 → v3.0）

| # | 維度 | v1.5 | v3.0 |
|:-|:----|:-----|:-----|
| 3 | 區域 | 北北基/桃竹苗/中彰投/雲嘉南/高屏/宜花東/離島（7區） | **都會區(六都)/北部/中部/南部/花東/離島（6區）** |
| 13 | **戶籍地** (NEW) | — | 台北市/新北市/…/連江縣（22縣市） |
| 14 | **物價分級** (NEW) | — | 高/中高/中/低/極低（基於主計總處消費支出） |
| 15 | **家戶所得分級** (NEW) | — | 極高/高/中/中低/低（基於主計總處家戶所得） |

## Prompt_prefix 演進

```
v1.5: 我叫柏伯，65+歲，住北北基，做退休。【柏伯】65+/北北基/退休。
v2.0: 我是福伯，阿伯，住在台北市，已經退休了。
v3.0: 我是福伯，阿伯，住在台北市，已經退休了。……
       在台北市收入不錯，但物價高還是要算著花。  ← 經濟脈絡句
```

## QA 演進

| 版本 | 規則數 | 範圍 |
|:----|:------:|:-----|
| v1.0 | 9 | 基本連貫性（未成年、婚姻、教育、分布） |
| v2.0 | 15 | 模板殘留（65+歳、做退休、【】、地點重複、獨生子…） |
| v3.0 | **18** | 年齡門檻（55+新婚、兒孫滿堂、未成年泡茶） |

## 基礎建設新增

- `sample_stratified.py` — 分層抽樣工具（96 combos，seed=42）
- `population_by_region_age_sex_2025.csv` — 6區×8年齡×2性別真實人口
- `qa_validate.py` — 18條自動化驗證規則
- DeepSeek V4 Pro delegation — 固定用於 sub-agent review
- `delegation.provider=custom:deepseek-pro` — config 層設定

---

## 迭代方法升級

### v1.5 流程
```
發現 bug → 修 → 隨機抽4樣本 → 你review → 又發現漏的
```

### v3.0 流程
```
發現 bug → 修 code + 加 QA rule → regenerate → qa_validate.py（18 rules, 0 violations）
→ sample_stratified.py（96 樣本）→ delegate_task(DeepSeek Pro) → 語意 review
→ 驗證新問題 → loop
```

### Pro review 實測成效
| 回合 | 模型 | 發現問題 | 獨家發現 |
|:----|:-----|:---------|:---------|
| 1 | Flash | ~9 類 | 表層 pattern（格式問題） |
| 2 | **Pro** | **~14 類** | 語意矛盾（娘家/兒孫滿堂/鰥寡） |

Pro 模型比 Flash 多發現 **5 類獨家問題**，token cost 3x 但有明確品質回報。

---

## 變更統計

| 指標 | 數值 |
|:----|:----:|
| 總 commit | 10（v3.0 相關） |
| 新增檔案 | 3（CSV, 抽樣工具, 抽樣樣本） |
| 修改檔案 | 2（generator, QA） |
| QA 規則 | 9 → **18** |
| 維度 | 14 → **16** |
| Stratified combos | 112（7區×8年齡×2性別）→ **96**（6區×8年齡×2性別） |
| 名字唯一性 | 172 名 / 17.3% |
| 連貫性修正 | 36-48 次/run |

---

## 後續規劃

- [ ] Domain stacking（選舉/金融/餐飲 overlay）
- [ ] Query CLI（`tw-persona query --region 南部 --age 35-44`）
- [ ] 物價/所得資料納入 reference_pre_prompt
- [ ] Spawn Pro review 作為 release gate
