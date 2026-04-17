# 🚀 GeoDoc Insight: 跨機器部署指南 (Deployment Guide)

本文件說明如何將「GeoDoc Insight: 交通陳情 GIS 分析系統」安裝並運行於另一台全新的電腦上。

---

## 🧰 1. 準備工作 (Prerequisites)

在開始之前，請確保目標電腦已安裝：
1.  **Python 3.10+**: [下載連結](https://www.python.org/downloads/) (安裝時請務必勾選 "Add Python to PATH")。
2.  **Git (選配)**: 如果您使用 Git 版控，否則直接拷貝整個專案資料夾即可。
3.  **Ngrok**: 如果需要公網訪問。

---

## 🛠️ 2. 安裝步驟 (Installation)

### Step 1: 複製專案資夾
將本專案的所有檔案（包含 `data/geodoc.db`）完整拷貝至目標電腦的硬碟中。
> 💡 **重要**：請確保路徑中不要有特殊的權限限制。

### Step 2: 安裝相依套件
打開 CMD 或 PowerShell，進入專案目錄，執行以下指令：
```bash
pip install -r requirements.txt
```

---

## ⚙️ 3. 數據初始化 (Data Initialization)

如果您更換了資料源 (Excel 報表)，或者想要確保數據狀態是最新的，請執行一鍵式管線：
```bash
python run_pipeline.py
```
這會自動執行：**讀取 -> 座標解析 -> 空間分析 -> 數據發佈**。

---

## 🌐 4. 啟動服務 (Start Service)

### A. 啟動本地網頁伺服器
進入 `src/dashboard` 目錄：
```bash
cd src/dashboard
python -m http.server 8000
```
完成後，您可以透過瀏覽器開啟：`http://localhost:8000`

### B. 啟動公網訪問 (Ngrok)
如果您需要遠端瀏覽，請在另一個視窗執行：
```bash
ngrok http 8000
```

---

## 📂 5. 檔案清單說明
- `data/geodoc.db`: **核心資料庫**，所有的分析結果都在這裡，更換機器時務必帶走。
- `src/dashboard/`: 存放網頁顯示的所有程式碼。
- `run_pipeline.py`: 當您有新數據要導入時，執行此腳本。

---
**本指南由 Antigravity 整理，祝您部署順利！**
