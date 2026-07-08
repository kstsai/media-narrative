# Media Narrative Analysis & Persona Database

> 八家媒體敘事比對、沉默議題偵測、人設資料庫
> TW media narrative direction analysis and silence detection

## 目錄結構

```
persona/          ← TW Persona Database — 997 個台灣人設模板
  README.md               — 專案概念概述
  tw-persona-db-rfc.md    — 規格文件
  tw_persona_997.json     — 997 筆人設資料庫
  MILESTONE_v0.1.md       — 開發歷程
  _generate_997.py        — 批次生成腳本

mediawatch/       ← 媒體敘事風向偵測
  INDEX.md                — 報告目錄
  _eight_media_report.py  — 八媒體爬蟲+全文分析腳本
  eight-media-comparison-*.md  — 各日報告

skills/           — 工作流程參考
  git-workflow.md         — git multi-remote 工作流程
```

## 快速開始

```bash
# 產生當日媒體報告
cd mediawatch
python3 _eight_media_report.py --date $(date +%Y-%m-%d)
```
