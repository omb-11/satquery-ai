@echo off
setlocal enabledelayedexpansion

echo.
echo ===============================================================================
echo   SATQUERY AI -- MULTIMODAL EARTH OBSERVATION INTELLIGENCE WORKSTATION
echo   ISRO Smart India Hackathon 2026 -- Problem Statement 26167
echo ===============================================================================
echo.

:: Detect root directory
if exist satquery-ai (
    set "SQ_ROOT=satquery-ai"
) else (
    set "SQ_ROOT=."
)

:: STEP 1: Python Check
echo [1/7] Inspecting Python runtime...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.10+ is required but not found in PATH.
    pause
    exit /b 1
)

:: STEP 2: Node.js Check
echo [2/7] Inspecting Node.js runtime...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js 18+ is required but not found in PATH.
    pause
    exit /b 1
)

:: STEP 3: Virtual Environment Check
echo [3/7] Verifying Python virtual environment...
if not exist "%SQ_ROOT%\venv" (
    echo [INFO] Creating Python virtual environment at %SQ_ROOT%\venv...
    python -m venv "%SQ_ROOT%\venv"
    echo [INFO] Performing initial dependency installation...
    "%SQ_ROOT%\venv\Scripts\pip" install -q -r "%SQ_ROOT%\backend\requirements.txt"
)

:: Create environment & data directories if needed
if not exist "%SQ_ROOT%\.env" (
    if exist "%SQ_ROOT%\.env.example" (
        copy "%SQ_ROOT%\.env.example" "%SQ_ROOT%\.env" >nul
        echo [INFO] Initialized %SQ_ROOT%\.env from template.
    )
)
if not exist "%SQ_ROOT%\data" mkdir "%SQ_ROOT%\data"
if not exist "%SQ_ROOT%\data\uploads" mkdir "%SQ_ROOT%\data\uploads"
if not exist "%SQ_ROOT%\data\results" mkdir "%SQ_ROOT%\data\results"
if not exist "%SQ_ROOT%\data\reports" mkdir "%SQ_ROOT%\data\reports"

:: STEP 4: Rapid Pre-flight Dependency Check (Skip if satisfied!)
echo [4/7] Performing rapid dependency verification...
"%SQ_ROOT%\venv\Scripts\python" "%SQ_ROOT%\scripts\check_dependencies.py"
if errorlevel 2 (
    echo [INFO] Installing frontend npm dependencies...
    pushd "%SQ_ROOT%\frontend"
    call npm install --silent
    popd
) else if errorlevel 1 (
    echo [INFO] Installing missing Python requirements...
    "%SQ_ROOT%\venv\Scripts\pip" install -r "%SQ_ROOT%\backend\requirements.txt"
) else (
    echo [INFO] Preflight dependencies satisfied. Fast-boot active.
)

:: STEP 5: Verify Demo Assets & Specialist Registry
echo [5/7] Verifying synthetic Earth observation demo scenes...
if not exist "%SQ_ROOT%\demo_data\single_optical\scene_optical.tif" (
    echo [INFO] Generating calibrated demo GeoTIFFs...
    "%SQ_ROOT%\venv\Scripts\python" "%SQ_ROOT%\scripts\generate_demo_data.py"
)

:: STEP 6: Launch Backend & Frontend Services
echo [6/7] Dispatching microservices...

:: Launch backend
start "SatQuery AI Backend Engine" cmd /k "cd %SQ_ROOT% && set PYTHONPATH=. && venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: Launch frontend
start "SatQuery AI Frontend Workstation" cmd /k "cd %SQ_ROOT%\frontend && npm run dev"

:: STEP 7: Startup Banner & Browser Launch
echo [7/7] Awaiting microservice initialization...
timeout /t 3 /nobreak >nul

echo.
echo ===============================================================================
echo   SATQUERY AI SYSTEM ONLINE
echo.
echo   - Mission UI:       http://localhost:5173
echo   - REST & SSE API:   http://localhost:8000/api/v1
echo   - Interactive Docs: http://localhost:8000/docs
echo   - Telemetry Health: http://localhost:8000/api/v1/health
echo ===============================================================================
echo.

start "" "http://localhost:5173"

echo Press any key to stop all SatQuery AI services...
pause >nul

taskkill /f /fi "WINDOWTITLE eq SatQuery AI Backend Engine*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq SatQuery AI Frontend Workstation*" >nul 2>&1
echo [INFO] SatQuery AI services gracefully halted.
