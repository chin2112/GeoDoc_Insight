# 🗺️ GeoDoc Insight: 交通局陳情 GIS 分析系統 — 交接與開發指南

本文件旨在提供專案的完整上下文，確保後續開發或 AI 代理人能無縫接軌維護此系統。

---

## 🎯 1. 專案核心目標 (Project Vision)
本系統將高雄市 1999 陳情報表（Excel/PDF）轉化為 **互動式 GIS 儀表板**。其核心價值在於：
- **治理視覺化**：讓交通局長官一眼看出「民怨熱點」與「行政區壓力」。
- **業務標籤化**：自動將非結構化文字分類至對應的「負責單位（課室）」。
- **決策支持**：透過熱度與趨勢分析，評估交通政策的成效。

---

## 🏗️ 2. 技術架構與資料流 (Architecture)
系統採用 **Offline-First (離線優先)** 策略，主要流程如下：
1.  **Ingestion**: 讀取 `_docs/` 下的原始 Excel 報表。
2.  **Geocoding**: 透過 `extractor.py` 處理高雄 38 區路名，匹配 OSM 座標。
3.  **Enrichment**: 
    - 計算 **「怨念值 (Severity)」**：同路口重複陳情即加分。
    - **業務分流**：自動標記行政區 (District) 與負責課室 (Dept)。
4.  **Export**: 將 SQLite 數據導出為 `data.js` 供前端讀取。
5.  **Dashboard**: 使用 Leaflet (地圖) 與 ECharts (圖表) 展示。

---

## 📂 3. 檔案地圖 (File Structure)
| 路徑 | 功能說明 |
| :--- | :--- |
| `src/db/` | 資料庫初始化與 SQL 邏輯。 |
| `src/geocoder/` | 核心地理編碼邏輯、路口識別器 (Aho-Corasick)。 |
| `src/pipeline/` | **最重要的目錄**。包含 `geocoding_job.py` (定位) 與 `enrich_business_data.py` (業務分類)。 |
| `src/dashboard/` | 前端視覺化代碼。`main.js` 負責所有圖表連動邏輯。 |
| `data/geodoc.db` | **核心資料庫 (SQLite)**。 |
| `_docs/` | 存放原始陳情報表（Excel/PDF）。 |

---

## 💾 4. 資料庫做法與欄位 (Database Schema)
**資料庫名**: `geodoc.db` | **主要表**: `cases`

| 欄位 | 說明 | 來源/產出邏輯 |
| :--- | :--- | :--- |
| `case_id` | 1999 案號 | 原始報表 |
| `content` | 陳情內容原文 | 原始報表 |
| `severity` | 嚴重度 (1.0 - 5.0) | 基於密度聚合算法產出 |
| `latitude/longitude` | GIS 座標 | Geocoding Pipeline 產出 |
| `district` | 行政區標籤 | `enrich_business_data.py` 語義提取 |
| `dept` | 負責課室標籤 | 依關鍵字自動分配至交通工程、停管中心等 |
| `suggestion_date` | 建議日期 | 報表日期標準化 |

---

## ✅ 5. 已完成功能 (Completed)
- [x] **四宮格分析看板**：包含 Top 10 地址、月/週趨勢、行政區排行、課室佔比。
- [x] **聚類點擊點 (Hotspot Cluster)**：同一座標多筆案件可透過抽屜切換。
- [x] **地圖 Focus 高亮**：點擊詳情時自動以青色圈環鎖定位置。
- [x] **文字摺疊閱讀器**：報表長文案自動收合，支援點擊展開。
- [x] **數據匯出**：支援過濾結果匯出為 CSV。
- [x] **公網發佈**：支援 Ngrok 隧道佈署。

## 🚧 6. 待開發/未完成 (Future Work)
- [ ] **人工覆核 UI**：目前的 `geocode_status` 為 `MANUAL_REVIEW_NEEDED` 的案子需要一個介面讓人員手動修正座標。
- [ ] **自動化排程**：將讀取、定位、增強、導出整合為一個監控腳本（Watchdog）。
- [ ] **回覆質量分析**：利用 AI 分析「回覆內容」是否解決了民眾問題。

---

## 🛠️ 7. 維運指令 (Maintenance)
1.  **啟動本地伺服器**:
    `cd src/dashboard; python -m http.server 8000`
2.  **數據重新定位與標籤化**:
    `python src/pipeline/geocoding_job.py`
    `python src/pipeline/enrich_business_data.py`
3.  **發佈數據到前端**:
    `python src/dashboard/data_exporter.py`

---
**本文件由 Antigravity 整理，旨在確保 GeoDoc Insight 專案的知識傳承。**
