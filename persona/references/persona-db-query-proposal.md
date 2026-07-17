# Persona DB — 甲方查詢介面提案

> 以 GitHub Issues 作為查詢入口，cron job 自動處理，結果回寫 issue
> 提案版本 v0.1 — 供與甲方討論用

---

## 核心概念

甲方不需要 Hermes Agent、不需要 CLI、不需要懂 Python。
他們只需要會開 **GitHub Issue**。

```
開 issue (查詢條件 + 模擬問題)
  → 自動處理 (query_persona + sub-agent 模擬)
  → 結果寫回 issue comment
  → 甲方可在同個 issue 追問
```

---

## 方案 A：獨立公開查詢 repo

### Repo 架構

```
github.com/kstsai/persona-db-query (public)
├── .github/ISSUE_TEMPLATE/
│   └── persona-db-query.md       ← 查詢表單範本
├── worklogs/                      ← 歷史分析報告 (唯讀)
│   ├── BANK-VISIBILITY-*.md
│   └── RAW-RESULTS-*.md
├── FAQ.md                         ← 常見問題
├── query-examples.md              ← 甲方可參考的範例查詢
└── CHANGELOG.md                   ← 資料更新記錄
```

### 甲方看到的權限

| 功能 | 權限 | 說明 |
|:-----|:----:|:------|
| 開 Issue | ✅ 可寫 | 提出查詢需求 |
| 看 Issue 結果 | ✅ 可讀 | 看到 query + 模擬回應 |
| 在 Issue 追問 | ✅ 可寫 | 同 thread 繼續討論 |
| 瀏覽 worklogs/ | ✅ 可讀 | 歷史分析報告 (rendered markdown) |
| 看到 code | ❌ 唯讀 | 只能看到這個 repo 的內容 |
| 看到 _generate_997.py | ❌ 看不到 | 在 private repo |

### 查詢流程圖

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  甲方開 Issue │ ──> │  Cron Job    │ ──> │  寫回 Comment │
│  (填表單)     │     │  (每N分鐘)   │     │  (含結果)     │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────┴──────┐
                     │  內部處理    │
                     │             │
                     │ 1. parse    │
                     │ 2. query    │
                     │ 3. simulate │
                     │ 4. format   │
                     └─────────────┘
```

---

## 方案 B：合併到現有 public repo

如果不想開新 repo，可以加在 `kstsai/media-narrative`（已是 public）：

```
github.com/kstsai/media-narrative (public)
├── persona/query/                  ← 新增
│   ├── .github/ISSUE_TEMPLATE/
│   ├── FAQ.md
│   └── query-examples.md
└── persona/worklogs/               ← 已有
```

| 優點 | 缺點 |
|:-----|:------|
| 不用額外管理一個 repo | repo 名稱跟內容不對應 |
| 現有的 GitHub Pages 可直接用 | 甲方可能困惑「這不是媒體分析嗎？」 |

---

## Issue 範本設計

### 標準查詢 — `persona-db-query`

```markdown
---
title: "persona-db-query: [簡短描述查詢目標]"
---

## 目標人設條件

可填的維度（愈多條件愈精準，但不一定要全填）：

- [ ] 年齡: ________ (ex: 25-34 / 35-44 / 不拘)
- [ ] 性別: ________ (ex: 男 / 女 / 不拘)
- [ ] 居住地: ________ (ex: 台北市 / 六都 / 不拘)
- [ ] 職業: ________ (ex: 科技 / 服務 / 家管 / 不拘)
- [ ] 收入: ________ (ex: >8萬 / 3-8萬 / 不拘)
- [ ] 家庭狀況: ________ (ex: 已婚有小孩 / 未婚 / 不拘)
- [ ] 政治傾向: ________ (ex: 泛綠 / 泛藍 / 不拘)
- [ ] 其他條件: ________

## 模擬問題

請寫出你想要這個 persona 回答的問題（1-3 題）：

> Q1: ________________________________
> Q2: ________________________________
> Q3: ________________________________

## 期望產出

- [ ] 符合條件的 persona 列表
- [ ] 每個 persona 對問題的角色扮演回答
- [ ] 跨 persona 的綜合分析
```

### 快速查詢 — `persona-db-quick`

簡化版，只查 persona 不模擬：

```markdown
---
title: "persona-db-quick: 新竹35-44科技業男性"
---

快速查詢：新竹市 + 35-44 + 科技業 + 男
只要列表，不用模擬回答。
```

### 樣本查看 — `persona-db-sample`

看特定地區/族群的分布狀況：

```markdown
---
title: "persona-db-sample: 離島地區有哪些人設"
---

想看離島（澎湖/金門/連江）的所有 persona 列表。
```

---

## 自動處理 pipeline

### 排程

```
每 10 分鐘掃一次 repo 的 open issues
  → 過濾 title 以 persona-db-query / quick / sample 開頭的
  → 跳過已處理的（檢查 label: processed）
  → 開始處理
```

### 處理步驟

```
Step 1: Parse issue body
  → 抽出年齡、性別、居住地、職業等條件
  → 抽出模擬問題（如果有的話）
  → 判斷查詢類型 (query / quick / sample)

Step 2: Run query_persona.py
  → 用條件過濾 1069 筆資料
  → 回傳符合條件的 persona list
  → 如果結果太多（>10），提示甲方縮小範圍
  → 如果結果太少（0），提示甲方放寬條件

Step 3: 如果是 standard query
  → 選 top 3 persona
  → 對每個 persona 丟 sub-agent 模擬
  → 收集回應

Step 4: Write back to issue
  → 加 label: processed
  → 加 comment 附結果
  → 如果出錯，加 label: query-error + 錯誤說明
```

### 結果回寫格式

```markdown
## 查詢結果

🔍 條件：新竹市 + 35-44 + 科技 + 男
📊 符合：3 筆

---

### 1️⃣ 協明 (TW-P-0301)
**35-44歲 | 台北市 | 科技業 | >8萬 | 已婚3口**

背景：一家三口，日子簡單。生活品質還不錯，該花的會花。
脈絡：在台北市收入不錯，但物價高還是要算着花。

> Q: 你覺得你居住的區域，還需要再多一家康是美嗎？
> A: 需要的話開在捷運站附近最好⋯⋯

---

> ⚡ 本次查詢由 persona-db v3.7 提供 • 若需更深入的模擬請開新 issue 描述更多細節
```

---

## 技術實作

### 需要的元件

| 元件 | 說明 |
|:-----|:------|
| **GitHub PAT** | 讀/寫 issue（scope: `repo` or `public_repo` + `issues`） |
| **Cron job** | `process-persona-queries.py`，每 10min 執行 |
| **query_persona.py** | 現有工具，直接調用 |
| **sub-agent delegator** | 現有 delegate_task，對每個 persona 派 sub-agent |
| **Issue template** | `.github/ISSUE_TEMPLATE/persona-db-query.md` |

### Cron job 腳本結構

```python
# process-persona-queries.py

def main():
    issues = fetch_open_issues(repo="kstsai/persona-db-worklogs")
    
    for issue in issues:
        if not is_query_issue(issue.title):
            continue
        if has_label(issue, "processed"):
            continue
        
        conditions = parse_issue_body(issue.body)
        personas = query_persona_db(conditions)
        
        if conditions.get("simulate"):
            responses = spawn_sub_agents(personas, conditions["questions"])
            write_back(issue, format_response(personas, responses))
        else:
            write_back(issue, format_persona_list(personas))
        
        add_label(issue, "processed")
```

### 錯誤處理

| 狀況 | 行為 |
|:-----|:------|
| Issue 格式不對 | 回 comment 請甲方補齊資訊 + `label: query-needs-info` |
| 查無符合條件 | 回 comment 建議放寬哪些維度 |
| 結果太多 (>10) | 提示甲方增加條件縮小範圍 |
| Sub-agent 失敗 | 回 partial result + 標註哪些模擬失敗 |
| Repo 或 API 斷線 | 跳過該輪，下次 cron 會重試 |

---

## 商業模式關聯

### 這屬於哪個方案？

| 方案 | 涵蓋 Query Service？ |
|:-----|:-------------------|
| **Lite (NT$25K)** | ❌ 不包含 — Lite 只給 data + gen engine，無服務 |
| **Transfer (NT$60-80K)** | ❌ 不包含 — Transfer 是工具移交，不含 ongoing service |
| **Session-Log Upgrade (NT$2,000/hr)** | ✅ 這屬於升級服務 — 建置 + 維護按工時計費 |

### 建議定價

```
一次性建置：
  - 公開 repo 建立 + issue template + cron job
  - 約 2-3 小時 → NT$4,000-6,000

持續維護：
  - 每月的 cron job 監控 + bug fix
  - 視使用量約 1-2 小時/月 → NT$2,000-4,000/月

每次查詢的運算成本：
  - 小查詢（僅列表）: ~100 tokens → 約 NT$0.01
  - 標準查詢（含模擬）: ~5,000 tokens → 約 NT$0.5
  - 甲方不需自付 token 費用（已含在維護費）
```

### 對甲方的提案話術

> 「你不需要學習任何工具，只要會開 GitHub issue 就行。
> 把你想要找的人設條件和想問的問題寫進去，
> 系統會自動處理，結果直接貼回 issue。
> 之後同一個 issue 還能追問。」

---

## 已知限制 & 風險

### 限制

| 限制 | 說明 |
|:-----|:------|
| **查詢品質受限於 prompt 品質** | 甲方寫的條件愈精確，結果愈好。模糊條件（如「年輕女性」）可能回傳太多或太少 |
| **Sub-agent 模擬是 self-report** | 模擬回答是 LLM 生成的，不是真人訪談。LLM 可能 hallucinate 具體數字或品牌偏好 |
| **最多同時處理 3 個 sub-agent** | 受 delegation 限制，大量查詢需排隊 |
| **公開 repo 的 issue 全世界可見** | 如果查詢內容敏感，不適合用 public repo。可改用 private repo + 加甲方為 collaborator |
| **無即時回應** | 最多 10 分鐘延遲（cron 週期） |

### 風險

| 風險 | 緩解方式 |
|:-----|:---------|
| 甲方開 spam issue | 加 label: spam 後忽略；太誇張可 close |
| 甲方期望過高（當成真人群體） | FAQ 明確寫「這是合成人設，不是真人樣本」 |
| Issue template 被 bypass | 程式只處理有正確 prefix 的 title，亂填的忽略 |
| GitHub API rate limit | 每 10 分鐘最多掃 30 個 issue，遠低於限制 |

---

## 甲方常見 QA（給 FAQ 用）

### Q: 可以查什麼？
> 任何 Persona DB 中有定義的維度：年齡、性別、居住地、職業、收入、家庭狀況、婚姻、政治傾向、興趣等。也可以組合多個條件。

### Q: 查不到我要的怎麼辦？
> 試著放寬一兩個條件。例如「新竹市 + 45-54 + 科技 + 4口」可能沒人，可以放寬到「新竹市 + 35-54 + 科技」或「新竹市 + 45-54 + 科技」。

### Q: 模擬回答跟真人一樣嗎？
> 這是 LLM 根據 persona 的維度資料進行的角色扮演。語氣和價值觀會貼近該 persona 的設定，但不是真實訪談數據。建議用於趨勢探索和假設驗證，不建議用於統計推論。

### Q: 我可以同時開多個查詢嗎？
> 可以，每個 issue 獨立處理。但同時最多處理 3 個，超過的會排隊等候。

### Q: 結果可以下載嗎？
> 目前結果寫在 issue comment 裡。如果需要大量輸出，可以另案討論。

---

## 下一步行動

- [ ] 決定方案 A（新 repo）或方案 B（併入現有 repo）
- [ ] 決定 repo 要 public 還是 private + collaborator
- [ ] 建立 GitHub issue template
- [ ] 寫 `process-persona-queries.py` cron job
- [ ] 設定 cron（每 10 分鐘）
- [ ] 撰寫 FAQ.md + query-examples.md
- [ ] 甲方教育：示範一次完整的 query flow
- [ ] 上線後觀察一週，調整 issue template 和 prompt
