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
echo "[1/4] 正在安裝相依套件 (requirements.txt)..."
python3 -m pip install -r requirements.txt --quiet

# 3. Run data pipeline
echo "[2/4] 正在執行數據分析管線 (run_pipeline.py)..."
export PYTHONPATH=$PWD
python3 run_pipeline.py

# 4. Ask for Ngrok
echo "[3/4] 是否要啟動 Ngrok 進行公網發布? (y/n)"
read -p "請輸入: " start_ngrok

if [[ "$start_ngrok" == "y" || "$start_ngrok" == "Y" ]]; then
    echo "[INFO] 正在後台啟動 Ngrok..."
    # Start ngrok in background and suppress output
    ngrok http 8000 > /dev/null &
    sleep 3
    echo "[SUCCESS] Ngrok 已啟動。您可以在終端機查看網址或前往 http://localhost:4040 查看。"
fi

# 5. Start Server and Browser
echo "[4/4] 正在啟動網頁服務..."
open http://localhost:8000

echo "服務已啟動，請勿關閉此視窗。"
cd src/dashboard
python3 -m http.server 8000 --bind 127.0.0.1
