@echo off
setlocal enabledelayedexpansion

echo ====================================================
echo   GeoDoc Insight: 交通陳情 GIS 戰情室 - 一鍵啟動
echo ====================================================

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 找不到 Python，請先安裝 Python 10 以上版本並加入 PATH。
    pause
    exit /b
)

:: 2. Install dependencies
echo [1/4] 正在安裝相依套件 (requirements.txt)...
pip install -r requirements.txt --quiet

:: 3. Run data pipeline
echo [2/4] 正在執行數據分析管線 (run_pipeline.py)...
set PYTHONPATH=%CD%
python run_pipeline.py

:: 4. Ask for Ngrok
echo [3/4] 是否要啟動 Ngrok 進行公網發布? (Y/N)
set /p start_ngrok="請輸入: "
if /i "!start_ngrok!"=="Y" (
    echo [INFO] 正在後台啟動 Ngrok...
    start "Ngrok Service" ngrok http 8000
    timeout /t 3 >nul
)

:: 5. Start Server and Browser
echo [4/4] 正在啟動網頁服務...
start http://localhost:8000
echo 服務已啟動，請勿關閉此視窗。
cd src\dashboard
python -m http.server 8000 --bind 127.0.0.1

pause
