# SatQuery AI — Troubleshooting & Diagnostics Guide

**Smart India Hackathon 2026 — Problem Statement 26167**  
**Organization:** Indian Space Research Organisation (ISRO)  

---

## 1. Port Conflicts

### Symptom: `Error: [Errno 10048] Only one usage of each socket address is normally permitted`
- **Cause:** Port `8000` (FastAPI backend) or Port `5173` (Vite dev server) is occupied by a previously running process.
- **Resolution (PowerShell):**
  ```powershell
  # Find process occupying port 8000
  Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
  Stop-Process -Id <PID> -Force

  # Find process occupying port 5173
  Get-NetTCPConnection -LocalPort 5173 | Select-Object OwningProcess
  Stop-Process -Id <PID> -Force
  ```

---

## 2. GeoTIFF CRS & Alignment Errors

### Symptom: `PairValidationResult: Bounds overlap 0.0%`
- **Cause:** Comparing two rasters in differing Coordinate Reference Systems (e.g., EPSG:4326 vs. EPSG:32643 UTM) without reprojection.
- **Resolution:** The `backend/geospatial/coregistration.py` engine automatically detects CRS mismatch and offers reprojection. Ensure both images share overlapping geographic extents.

---

## 3. Gemini API Connection Errors

### Symptom: `GeminiAnalyst: Connection test failed / NOT_CONFIGURED`
- **Cause:** `GEMINI_API_KEY` is not set or network egress is blocked.
- **Behavior:** SatQuery AI **does not fail**. It logs a notice and seamlessly routes execution through the local remote sensing deterministic synthesizer (`backend/agents/synthesizer.py`).
- **Fix:** Open the **GEMINI AI** pill in the top bar, input your Google AI Studio key, and click "Test Connection" followed by "Save Configuration".

---

## 4. Node Modules & Vite Build Failures

### Symptom: `Cannot find module '...'` during `npm run build`
- **Resolution:**
  ```powershell
  cd satquery-ai/frontend
  npm install
  npm run build
  ```
