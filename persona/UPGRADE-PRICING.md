# TW Persona DB — 升級與 Session Log 計費

> **基於 actual session log 的公平計費標準**
> 費率: NT$2,000/hr | 最低計費: 15 分鐘

---

## 核心原則

Session Log 計費 = 每個工作 session 結束後，產出一份 `WORKLOG.md`，記錄：
1. 工作時間段（幾點到幾點，做什麼）
2. 對應的 git commit hash
3. 產出檔案
4. 工時 × 費率 = 金額

甲方看到 log 就知道「NT$6,000 買了什麼」，不需要猜或信任。

---

## 費率

| 項目 | 費率 | 說明 |
|:-----|:----:|:------|
| Major upgrade / 新功能開發 | **NT$2,000/hr** | 疊加新維度、重大版本升級 |
| Domain 疊加（L2） | NT$2,000/hr | 如選舉投票紀錄、消費偏好 |
| 全新建置（L3） | NT$2,000/hr | 如日本版、越南版 |
| 諮詢 / 交接 | NT$2,000/hr | 超過 2hr 後計費 |

---

## Worklog 產出範例

每次升級完成後，repo 裡會多一份 `WORKLOG-YYYY-MM-DD.md`：

```markdown
# Persona DB v3.0→v3.7 工時紀錄
日期: 2026-07-11 ~ 07-13 | 費率: NT$2,000/hr | 總計: 10.1h = NT$20,200

## 7/11（六）— 主力架構迭代 — 5.7h

### 09:30-10:00 — Session 開啟 + 脈絡重建 (0.5h)
- 從 home session handoff persona improvement 討論
- Skill loading + 現狀 recall（v1.5, 9 rules, 997 人）

### 10:00-10:30 — Hybrid 驗證方向決策 (0.5h)
- 評估 sub-agent 驗證可行性 → 決定 hybrid 路線
- 建立 delegation config（deepseek-v4-pro 子代理）

### 10:30-11:30 — v3.0 核心架構建設 (1.0h)
- prompt_prefix 改為使用 residence（城市名）
- price_tier 維度、hh_income_tier 維度
- gen_econ_context() 經濟描述句

### 15:30-16:00 — v3.1 擴充 + 職業加權 (0.5h)
- 997→1069 擴充
- OCC_CITY_BOOST 城市職業加成
- specific_age() 自然化

### 16:00-17:00 — Pro review #1 + bug fixes (1.0h)
- 2 bugs found: student income + 1人家庭小孩敘述
- 65+ 獨生子 root cause: variable scoping trap
- 含飴弄孫→簡單過日子

...（完整內容見 actual file）

## 總計

| 日期 | 工時 | 內容 | 金額 |
|:----|:----:|:-----|:----:|
| 7/11 | 5.7h | v3.0核心架構 + v3.1 + 65+自然化 + 2輪Pro | NT$11,400 |
| 7/12 | 1.6h | 真實OCC/MARRIAGE數據 + QA R19-R20 | NT$3,200 |
| 7/13 | 2.8h | v3.7全量 + 6×Pro + post-hoc + QA R21-R23 | NT$5,600 |
| 總計 | 10.1h | 25+ commits, 1069 personas, 23 QA rules | NT$20,200 |
```

---

## 透明機制

1. **Session log 自動記錄**：每個工作階段由 Hermes Agent 記錄起迄時間與內容
2. **Git log 交叉驗證**：每個 commit 對應到 worklog 中的工作項目
3. **產出檔案可查**：所有修改過的檔案列在 worklog 中
4. **雙方簽認**：甲方確認 worklog 內容無誤後結算

---

## 估算參考

| 升級類型 | 預估工時 | 預估金額 |
|:---------|:--------:|:--------:|
| Minor bug fix（R24 新增） | 0.5-1.0h | NT$1,000-2,000 |
| Major version bump（v3→v4） | 3.0-5.0h | NT$6,000-10,000 |
| 疊加新維度（如選舉投票） | 2.0-4.0h | NT$4,000-8,000 |
| 全新建置（如日本版） | 8.0-15.0h | NT$16,000-30,000 |

---

_文件版本: v1.0 | 最後更新: 2026-07-13_
