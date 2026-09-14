@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   SATQUERY AI - Remote Sensing Intelligence Workstation
echo   ISRO Smart India Hackathon 2026
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

:: Setup .env if needed
if not exist satquery-ai\.env (
    copy satquery-ai\.env.example satquery-ai\.env >nul
    echo [INFO] Created .env from template
)

:: Create data directories
if not exist satquery-ai\data mkdir satquery-ai\data
if not exist satquery-ai\data\uploads mkdir satquery-ai\data\uploads
if not exist satquery-ai\data\results mkdir satquery-ai\data\results
if not exist satquery-ai\data\reports mkdir satquery-ai\data\reports

:: Install Python deps if needed
if not exist satquery-ai\venv (
    echo [INFO] Creating Python virtual environment...
    python -m venv satquery-ai\venv
)
echo [INFO] Installing Python dependencies...
satquery-ai\venv\Scripts\pip install -q -r satquery-ai\backend\requirements.txt

:: Generate demo data
echo [INFO] Generating demo data...
satquery-ai\venv\Scripts\python satquery-ai\scripts\generate_demo_data.py

:: Install frontend deps if needed
if not exist satquery-ai\frontend\node_modules (
    echo [INFO] Installing frontend dependencies...
    cd satquery-ai\frontend
    npm install --silent
    cd ..\..
)

echo.
echo [INFO] Starting SatQuery AI...
echo.

:: Start backend in background
start "SatQuery Backend" cmd /k "cd satquery-ai && set PYTHONPATH=. && venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: Wait for backend
echo [INFO] Waiting for backend to start...
timeout /t 5 /nobreak >nul

:: Start frontend
start "SatQuery Frontend" cmd /k "cd satquery-ai\frontend && npm run dev"

echo.
echo ============================================================
echo   SatQuery AI is starting!
echo.
echo   Backend API:  http://localhost:8000
echo   Frontend UI:  http://localhost:5173
echo   API Docs:     http://localhost:8000/docs
echo ============================================================
echo.

:: Open browser after delay
timeout /t 8 /nobreak >nul
start "" "http://localhost:5173"

echo Press any key to stop SatQuery AI...
pause >nul

:: Cleanup
taskkill /f /fi "WINDOWTITLE eq SatQuery Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq SatQuery Frontend*" >nul 2>&1
echo [INFO] SatQuery AI stopped.
