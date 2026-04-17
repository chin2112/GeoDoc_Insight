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
echo [1/3] 正在安裝相依套件 (requirements.txt)...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] 套件安裝可能未完全成功，嘗試繼續運行...
)

:: 3. Run data pipeline
echo [2/3] 正在執行數據分析管線 (run_pipeline.py)...
set PYTHONPATH=%CD%
python run_pipeline.py
if %errorlevel% neq 0 (
    echo [ERROR] 數據管線執行失敗。
    pause
    exit /b
)

:: 4. Start Server and Browser
echo [3/3] 正在啟動網頁服務...
start http://localhost:8000
echo 服務已啟動，請勿關閉此視窗。
cd src\dashboard
python -m http.server 8000 --bind 127.0.0.1

pause
