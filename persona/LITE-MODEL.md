# TW Persona DB — Lite 方案

> **NT$15,000 賣斷** | 資料 + 查詢工具，不含生成引擎
> 後續升級計費同 Transfer 模式（NT$2,000/hr，依 session log）

---

## 一句話

> NT$15,000，拿到 1,069 筆台灣人設資料庫 + 查詢 CLI。不能自己 regenerate，但能馬上開始 query 你的目標客群。

---

## 交付內容

```
Lite 方案 v3.2（NT$15,000 賣斷）
├── data/
│   ├── tw_persona_1069.json      ← 1,069 筆，18 維度
│   ├── tw-persona-db-rfc.md      ← 規格文件
│   └── qualified-memory.md       ← 24 條 domain knowledge
├── tools/
│   ├── query_persona.py          ← 查詢 CLI（唯讀）
│   └── sample_stratified.py      ← 分層抽樣檢視
├── README.md + FAQ.md            ← 快速入門
└── VERSION                       ← v3.2
```

**不含：** `_generate_997.py`、`qa_validate.py`、機率表、scripts 目錄、skills 目錄

---

## 授權條款

| 項目 | 允許 | 不允許 |
|:-----|:----|:-------|
| 使用資料 | ✅ 可用於商業產品內部 | ❌ 不可轉售原始資料 |
| 查詢使用 | ✅ 可自由 query、分析 | ❌ 不可自行 regenerate |
| 販售成果 | ✅ 可販售基於資料的分析報告 | ❌ 不可轉售 JSON 本體 |
| 修改資料 | ✅ 可手動編輯 JSON | ❌ 不可重新生成 |
| 子授權 | | ❌ 不可再授權予第三方 |

---

## 後續升級（同 Transfer 模式）

需要新版資料或功能時：

```
費率：NT$2,000/hr
計費：依 actual session log，透明可查
範例：major upgrade v3.2→v4.0 約 3h ≈ NT$6,000
```

每次 upgrade 產出 `WORKLOG.md` 記錄每個時間段的工作內容、對應 commit、產出檔案。

---

## 與 Transfer 方案對比

| | Lite | Transfer |
|:--|:----:|:--------:|
| **價格** | **NT$15,000** | **NT$60,000-80,000** |
| 資料（1069.json） | ✅ | ✅ |
| 查詢 CLI | ✅ | ✅ |
| 文件（RFC + FAQ） | ✅ | ✅ |
| qualified memory | ✅ | ✅ |
| **_generate_997.py** | ❌ | ✅ |
| **qa_validate.py** | ❌ | ✅ |
| **完整 scripts** | ❌ | ✅ |
| **skills 目錄** | ❌ | ✅ |
| 可自行 regenerate | ❌ | ✅ |
| 可賣改進後的 1069.json | ❌ | ✅ |
| 後續升級計費 | NT$2,000/hr | NT$2,000/hr |

---

## 適合誰

- **只想先用資料看看品質**，不確定要不要投入完整工具
- **預算有限**，NT$15K 門檻低，先驗證資料價值
- **不需要自己 regenerate**，現有 1,069 筆就夠用

Lite 用得好，之後補差價升級到 Transfer 即可（NT$45K-65K）。

---

_文件版本: v1.0 | 最後更新: 2026-07-13_
