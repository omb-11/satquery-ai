#!/usr/bin/env bash
set -e

echo ""
echo "============================================================"
echo "  SATQUERY AI - Remote Sensing Intelligence Workstation"
echo "  ISRO Smart India Hackathon 2026"
echo "============================================================"
echo ""

# Verify Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+"
    exit 1
fi

# Verify Node
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js could not be found. Please install Node.js 18+"
    exit 1
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

if [ ! -f "satquery-ai/.env" ]; then
    cp satquery-ai/.env.example satquery-ai/.env
    echo "[INFO] Created .env from template"
fi

mkdir -p satquery-ai/data/uploads satquery-ai/data/results satquery-ai/data/reports

if [ ! -d "satquery-ai/venv" ]; then
    echo "[INFO] Creating Python virtual environment..."
    python3 -m venv satquery-ai/venv
fi

echo "[INFO] Installing Python dependencies..."
satquery-ai/venv/bin/pip install --quiet -r satquery-ai/backend/requirements.txt

echo "[INFO] Generating synthetic test imagery..."
PYTHONPATH="satquery-ai" satquery-ai/venv/bin/python satquery-ai/scripts/generate_demo_data.py

if [ ! -d "satquery-ai/frontend/node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    (cd satquery-ai/frontend && npm install --silent)
fi

echo ""
echo "[INFO] Launching SatQuery AI Services..."
echo ""

# Start backend in background
(cd satquery-ai && PYTHONPATH="." ./venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

# Start frontend in background
(cd satquery-ai/frontend && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit" SIGINT SIGTERM EXIT

echo "============================================================"
echo "  SatQuery AI is running!"
echo "  Backend API:  http://localhost:8000"
echo "  Frontend UI:  http://localhost:5173"
echo "  API Docs:     http://localhost:8000/docs"
echo "============================================================"
echo "Press Ctrl+C to terminate all services."

wait
