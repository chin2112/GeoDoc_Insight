#!/bin/bash

echo "===================================================="
echo "  GeoDoc Insight: 交通陳情 GIS 戰情室 - Mac 啟動器"
echo "===================================================="

# 1. Check Python 3
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] 找不到 python3，請先安裝 Python 3。"
    exit 1
fi

# 2. Install dependencies
echo "[1/3] 正在安裝相依套件 (requirements.txt)..."
python3 -m pip install -r requirements.txt --quiet

# 3. Run data pipeline
echo "[2/3] 正在執行數據分析管線 (run_pipeline.py)..."
export PYTHONPATH=$PWD
python3 run_pipeline.py

# 4. Start Server and Browser
echo "[3/3] 正在啟動網頁服務..."
# Open URL (Mac command)
open http://localhost:8000

echo "服務已啟動，請勿關閉此視窗。"
cd src/dashboard
python3 -m http.server 8000 --bind 127.0.0.1
