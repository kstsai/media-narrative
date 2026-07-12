# Mock Billing Report — AI 自動回報工作時數

> 日期：2026-07-11
> Session：Persona DB 精進迭代（`20260711_023946_2b0b9327`）
> 費率：NT$3,000/hr，最低計費 15 min
> 幣別：新台幣（NTD）

---

## 工作紀錄

### Cycle 1 — Context Handoff + 現狀盤點
| 欄位 | 內容 |
|:----|:------|
| 起始 | 使用者傳入 context handoff，要求從主 session 延續 persona improvement 討論 |
| AI 工作 | 載入 tw-persona-db skill、搜尋歷史 session、讀取 _generate_997.py 和 qa_validate.py、產生現狀摘要與改進提案 |
| 終止 | 使用者決定走 hybrid 方向（分層抽樣 tool + AI review） |
| 時數 | 0.3 hr（AI 回報：02:39 → 02:54，含 context 建立與三個提案討論） |
| 金額 | **NT$900** |

### Cycle 2 — 建立分層抽樣 Review Tool
| 欄位 | 內容 |
|:----|:------|
| 起始 | 「建立分層抽樣 review tool，產 112 sample persona entries」 |
| AI 工作 | 分析 7 區域 × 8 年齡 × 2 性別共 112 組合覆蓋率、撰寫 `sample_stratified.py`（從每組合抽 1 人）|
| 驗證 | 執行驗證：所有 112 組合都有至少 1 筆人員 |
| 終止 | 樣本產生成功，可繼續下一步 |
| 時數 | 0.5 hr |
| 金額 | **NT$1,500** |

### Cycle 3 — 65+ Prompt Prefix 自然化（三模板全改）
| 欄位 | 內容 |
|:----|:------|
| 起始 | 要求改善長者 prompt_prefix 自然度 |
| AI 工作 | 更新 Template A/B/C 中 65+ 的輸出版本（Before:「碧嬸是阿姨，住花蓮縣」→ After:「你們可以叫我碧嬸，72歲了，住花蓮縣」）|
| 驗證 | `qa_validate.py` 9 rules PASS，檢查樣本自然度 |
| 終止 | commit 到 git（gitea + GitHub） |
| 時數 | 0.5 hr |
| 金額 | **NT$1,500** |

### Cycle 4 — 全量 Pro Review（6 chunks）
| 欄位 | 內容 |
|:----|:------|
| 起始 | 要求 spawn sub-agent（DeepSeek Pro）做全面性內容不自然查找 |
| AI 工作 | 分割 1069 筆為 6 chunks、dispatch sub-agent、彙整 6 份報告 |
| 發現 | 3 個真實 bug：story_nochild_contra、story_hantai_contra、「一個人過日子」模板污染 |
| 終止 | 全部修復、regeneration、QA pass、commit |
| 時數 | 0.75 hr（含子 agent 協調與 bug 修復） |
| 金額 | **NT$2,250** |

### Cycle 5 — 婚姻真實統計資料整合
| 欄位 | 內容 |
|:----|:------|
| 起始 | 「流程改用 spawn 獨立 AI agent 做分布分析 vs 改用 hybrid？」→ 決定 hybrid |
| AI 工作 | 從 ODRP014 API + 離婚統計 ODS + 離婚率 CSV 計算真實 MARRIAGE_PROB_MALE/FEMALE、patch 進 `_generate_997.py`、regenerate、QA pass |
| 發現 | 19-24 未婚 88%→97%、25-34 未婚 40%→75%、離婚率 7-18%→<3%（之前嚴重高估）|
| 終止 | commit + push |
| 時數 | 1.0 hr（含 sub-agent 資料計算 + 整合） |
| 金額 | **NT$3,000** |

### Cycle 6 — 碧霞 Bug（45+未婚跟爸媽住）
| 欄位 | 內容 |
|:----|:------|
| 起始 | 使用者發現 p0620 碧霞：55-64 未婚 4口之家「跟爸爸媽媽和一個哥哥住」，不合理 |
| AI 工作 | 掃描 28 筆同類問題、新增 HH_FAM4_UNMARRIED_SENIOR 和 HH_FAM5_UNMARRIED_SENIOR phrase pool、更新 infer_background() 分支、新增 QA R20、regenerate → verify 0→28→0 |
| 終止 | commit + push（"28 cases → 0. All 20 QA rules pass."）|
| 時數 | 0.5 hr |
| 金額 | **NT$1,500** |

---

## 小計

| Cycle | 工作項目 | 時數 | 金額 |
|:----:|:---------|:---:|:----:|
| 1 | Context handoff + 策略討論 | 0.3 hr | NT$900 |
| 2 | 分層抽樣 review tool | 0.5 hr | NT$1,500 |
| 3 | 65+ Prompt Prefix 自然化 | 0.5 hr | NT$1,500 |
| 4 | 全量 Pro Review 6 chunks | 0.75 hr | NT$2,250 |
| 5 | 婚姻真實統計資料整合 | 1.0 hr | NT$3,000 |
| 6 | 碧霞 Bug（45+未婚家庭描述） | 0.5 hr | NT$1,500 |
| | **總計** | **3.55 hr** | **NT$10,650** |

---

## 透明度附註

### 什麼算在時數內
- 使用者提出需求到 AI 完成產出並經使用者確認的完整 cycle
- AI 執行工具、讀寫檔案、sub-agent 協調的時間
- 使用者 review output 後要求修正的 iteration

### 什麼不算
- background 發想的時間（使用者沒給指令時 AI 沒在動）
- 使用者在 slack 上閒聊的無關訊息
- AI 執行的 API 費用（NT$~0.4 for Pro review — 客戶不負擔）

### 原始資料查驗
客戶可要求查看該 session 的完整對話記錄以驗證工作內容與時數。
每次 cycle 的起訖時間點在 session log 中均有 timestamp 可對照。

---

## 定價建議總結

| 項目 | 數值 |
|:----|:----:|
| 費率 | NT$3,000/hr |
| 最低計費 | 15 min |
| 時數來源 | AI session log 自動回報 |
| 驗證方式 | 客戶可看 raw log |
| 月上限（建議） | 可設 NT$30K/月，讓客戶安心試水 |
