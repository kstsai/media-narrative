# TW Persona DB — Lite 方案

> **NT$25,000 賣斷** | 資料 + 生成引擎 + 查詢 CLI，不含 QA
> 後續升級計費同 Transfer 模式（NT$2,000/hr，依 session log）

---

## 一句話

> NT$25,000，拿到 1,069 筆台灣人設資料庫 + 查詢 CLI + 生成引擎。**可自行修改 regenerate，可賣改進後的 1069.json。但再生品質不保固。**

---

## 交付內容

```
Lite 方案 v3.2（NT$25,000 賣斷）
├── data/
│   ├── tw_persona_1069.json      ← 1,069 筆，18 維度
│   ├── tw-persona-db-rfc.md      ← 規格文件
│   └── qualified-memory.md       ← 24 條 domain knowledge
├── tools/
│   ├── query_persona.py          ← 查詢 CLI
│   ├── _generate_997.py          ← 重新生成引擎 🔑
│   └── auto-import-qualified.sh  ← 更新腳本
├── README.md + FAQ.md            ← 快速入門
└── VERSION                       ← v3.2
```

**不含：** `qa_validate.py`、機率表、scripts 審查工具、skills 目錄

---

## 授權條款

| 項目 | 允許 | 不允許 |
|:-----|:----|:-------|
| 使用資料 | ✅ 可用於商業產品內部 | ❌ 不可轉售 tool 本身 |
| 修改 regenerate | ✅ **可自行修改、重新 generate** | ❌ 品質結果不保固 |
| 販售改進資料 | ✅ **可賣改進後的 1069.json** | ❌ 不可轉售 `_generate_997.py` |
| 重新生成 | ✅ 可用 `_generate_997.py` | |
| 子授權 | | ❌ 不可再授權予第三方 |

> ⚠️ **品質免責**：Lite 方案不含 QA 驗證工具和方法論交接。自行 regenerate 的資料品質由甲方自行驗證。

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
| **價格** | **NT$25,000** | **NT$60,000-80,000** |
| 資料（1069.json） | ✅ | ✅ |
| 查詢 CLI | ✅ | ✅ |
| `_generate_997.py` | ✅ | ✅ |
| **qa_validate.py** | ❌ | ✅ |
| **機率表 + scripts** | ❌ | ✅ |
| **skills 目錄** | ❌ | ✅ |
| **可賣改進後的 1069.json** | ✅ | ✅ |
| **品質保固** | ❌ 自行負責 | ✅ 含 QA 驗證 |
| 後續升級計費 | NT$2,000/hr | NT$2,000/hr |

---

## 適合誰

- **預算有限但想要完整功能** — NT$25K 拿到資料 + 生成引擎
- **自己有 QA 能力** — 能自行驗證 regenerate 品質
- **先試水再升級** — Lite 用得好，補差價 NT$35K-55K 升級到 Transfer 含 QA

> Lite 跟 Transfer 的核心差異在於：Lite 給你工具，但不保固品質。Transfer 含 QA 驗證 + 方法論交接，品質有 baseline。

---

_文件版本: v1.0 | 最後更新: 2026-07-13_
