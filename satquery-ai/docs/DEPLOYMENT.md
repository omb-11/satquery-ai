# SatQuery AI — Deployment Guide

**Smart India Hackathon 2026 — Problem Statement 26167**  
**Organization:** Indian Space Research Organisation (ISRO)  

---

## 1. Deployment Modalities

SatQuery AI is designed for flexibility across air-gapped workstations, cloud edge nodes, container clusters, and modern static edge networks.

| Target | Description | Recommended For |
| :--- | :--- | :--- |
| **Local Standalone (`run.bat`)** | Complete full-stack local execution | Evaluation, SIH live judges, demo laptops |
| **Docker Compose** | Multi-container orchestrated setup | On-premise servers & air-gapped lab nodes |
| **Vercel Edge Network** | Serverless frontend deployment | Public web presentation & UI inspection |
| **GCP Cloud Run / Compute** | Containerized backend hosting | High-throughput cloud API hosting |

---

## 2. Local Standalone Deployment (Windows / Linux)

### Automated 1-Click Startup (Windows)
Run `run.bat` from root or the `satquery-ai/` subfolder:
```bat
run.bat
```
The script runs a 7-step pre-flight check:
1. Validates Python 3.10+
2. Validates Node.js 18+
3. Configures virtual environment (`satquery-ai/venv`)
4. Verifies dependencies via `scripts/check_dependencies.py`
5. Verifies demo GeoTIFF imagery
6. Dispatches backend (Port 8000) and frontend (Port 5173)
7. Launches browser at `http://localhost:5173`

---

## 3. Docker Compose Deployment

The repository includes a ready-to-use `docker-compose.yml`:
```bash
docker-compose up --build
```
- **Backend Service:** Exposes port `8000`, mounts `./data/uploads` and `./data/results`.
- **Frontend Service:** Exposes port `5173`, proxies `/api/v1` calls to backend.

---

## 4. Vercel Frontend Deployment

The static React + Vite frontend is pre-configured for Vercel:
- **Build Command:** `cd satquery-ai/frontend && npm install && npm run build`
- **Output Directory:** `satquery-ai/frontend/dist`
- **Vercel URL:** `https://sqai-psi.vercel.app`
