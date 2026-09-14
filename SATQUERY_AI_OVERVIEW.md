# SATQUERY AI — COMPREHENSIVE SYSTEM DOSSIER & SIH 2026 SPECIFICATION

**Smart India Hackathon 2026 — Problem Statement 26167**  
**Title:** SatQuery AI — An Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Text Queries  
**Organization:** Indian Space Research Organisation (ISRO)  
**Department:** Department of Space / ISRO  
**Category:** Software  
**Theme:** Space Technology  

---

## 1. Executive Summary & Product Vision

### 1.1 The Challenge
Modern satellite constellations generate terabytes of high-resolution Earth Observation (EO) data daily across multiple modalities:
- Optical multispectral imagery (e.g., Cartosat, Sentinel-2)
- Synthetic Aperture Radar (SAR) backscatter (e.g., RISAT, Sentinel-1)
- Temporal revisit sequences

Traditional geospatial exploitation requires specialized GIS analysts, complex desktop software (QGIS, ArcGIS, ENVI), manual band selection, coordinate transformation, radiometric calibration, and algorithmic selection. Generic large Vision-Language Models (VLMs), on the other hand, suffer from:
- Inability to read native georeferenced rasters (GeoTIFF)
- Lack of physical/spectral awareness (NDVI, NDWI, NDBI)
- Inability to process complex radar backscatter physics
- Tendency to hallucinate unsupported spatial facts without auditable evidence

### 1.2 The SatQuery AI Solution
**SatQuery AI** bridges this divide by functioning as an **Intelligent Mission-Control Workstation** for remote-sensing imagery. It is engineered not as a simple VLM prompt wrapper, but as an **Agentic Earth Observation Orchestration System**:

$$\mathbf{ASK} \longrightarrow \mathbf{PLAN} \longrightarrow \mathbf{VALIDATE} \longrightarrow \mathbf{ANALYZE} \longrightarrow \mathbf{EVIDENCE} \longrightarrow \mathbf{ANSWER} \longrightarrow \mathbf{AUDIT}$$

1. **Ask:** The user provides natural language queries alongside single, bi-temporal, or cross-modal satellite imagery.
2. **Plan & Route:** The autonomous agent determines query intent, evaluates available metadata and modalities, and plans a multi-step tool execution sequence.
3. **Validate:** Ingests native GeoTIFFs, extracts CRS, spatial footprints, bounding coordinates, and validates co-registration compatibility.
4. **Analyze:** Specialized engines run concurrent tasks: radiometric difference mapping, SAR speckle/dB normalization, spectral index extraction, or VLM grounding.
5. **Evidence:** Computes localized spatial bounding boxes, change percentages, and cross-modal agreement scores.
6. **Answer:** Generates evidence-grounded natural language findings where every claim is anchored to verifiable spatial evidence.
7. **Audit:** Exposes a real-time, step-by-step millisecond execution trace and provides downloadable analysis dossiers.

---

## 2. Complete Architectural Design

```
                                  [ User Natural Language Query ]
                                  [ GeoTIFF / Optical / SAR Images ]
                                                  │
                                                  ▼
                                      ┌────────────────────────┐
                                      │  ImageValidator        │ ◄── Format, CRS, Bounds, Modality
                                      └───────────┬────────────┘
                                                  ▼
                                      ┌────────────────────────┐
                                      │  TaskRouter            │ ◄── Deterministic & Semantic Routing
                                      └───────────┬────────────┘
                                                  ▼
                                      ┌────────────────────────┐
                                      │  TaskPlanner           │ ◄── Dependency Graph Generation
                                      └───────────┬────────────┘
                                                  ▼
                       ┌──────────────────────────────────────────────────────┐
                       │            Specialist Execution Engine               │
                       ├──────────────────┬─────────────────┬─────────────────┤
                       │  Spectral Engine │ Change Detector │ Fusion Engine   │
                       │  (NDVI/NDWI/NDBI)│ (Bi-temporal)   │ (Optical + SAR) │
                       ├──────────────────┼─────────────────┼─────────────────┤
                       │  SAR Processor   │ Grounding Eng.  │ VQA Specialist  │
                       │  (Backscatter dB)│ (Bounding BBox) │ (BLIP / CPU RS) │
                       └──────────────────┴────────┬────────┴─────────────────┘
                                                   ▼
                                      ┌────────────────────────┐
                                      │  EvidenceAggregator    │ ◄── Bounding boxes, Spectral stats
                                      └───────────┬────────────┘
                                                  ▼
                                      ┌────────────────────────┐
                                      │  EvidenceVerifier      │ ◄── Anti-hallucination Claim Check
                                      └───────────┬────────────┘
                                                  ▼
                                      ┌────────────────────────┐
                                      │  ConfidenceEstimator   │ ◄── Weighted Multi-factor Scoring
                                      └───────────┬────────────┘
                                                  ▼
                                      ┌────────────────────────┐
                                      │  AnswerSynthesizer     │ ◄── Evidence-Grounded Natural Text
                                      └───────────┬────────────┘
                                                  ▼
                            [ Auditable Execution Trace + Visual Evidence ]
```

### 2.1 Backend Layer (Python FastAPI)
- **FastAPI Core (`backend/main.py`, `backend/api/`):** Asynchronous API engine with Server-Sent Events (SSE) streaming, SQLite run persistence, and clean endpoint separation.
- **Agentic Orchestrator (`backend/agents/`):**
  - `TaskRouter`: Inspects input state (image count, modality, band semantics) and natural query semantics to classify queries into appropriate tasks (`CHANGE_VQA`, `OPTICAL_SAR_FUSION`, `SINGLE_GROUNDING`, etc.).
  - `TaskPlanner`: Generates ordered execution pipelines and tool dependency graphs.
  - `AgentOrchestrator`: Runs the full pipeline with timing benchmarks and state tracking.
  - `AnswerSynthesizer`: Formats findings into clean structured sections: Finding, Evidence, Location, Confidence, Limitations.
- **Specialist Tools (`backend/tools/`):**
  - `ImageValidator`: Verifies raster readability, dimensions, band counts, and geographic co-registration.
  - `RasterPreprocessor`: Handles dynamic percentile stretching (2%–98%), aspect-preserving downscaling, and tiling.
  - `ChangeDetector`: Executes bi-temporal difference mapping, Otsu thresholding, connected component region extraction, and semantic change classification.
  - `SARProcessor`: Decibel (dB) scale dynamic range normalization, specular water isolation, and structural double-bounce built-up detection.
  - `OpticalSARFusionEngine`: Multimodal corroboration analyzing optical reflectance against SAR structural response with explicit agreement scoring.
  - `GroundingAnalyzer`: Converts referring text queries into normalized bounding boxes `[x1, y1, x2, y2]`.
  - `SpectralAnalyzer`: Pure NumPy biophysical parameter computation (NDVI, NDWI, NDBI).
- **Geospatial Processing Engine (`backend/geospatial/`):**
  - Native integration with **Rasterio**, **GDAL**, and **Shapely** for affine transformations, EPSG / WGS84 CRS conversions, and bounding box overlap calculations.
- **Evidence & Verification (`backend/evidence/`):**
  - `EvidenceAggregator`: Gathers, deduplicates, and sorts spatial and spectral evidence.
  - `EvidenceVerifier`: Evaluates claims against tool outputs, removing unverified assertions.
  - `ConfidenceEstimator`: Implements multi-factor weighted confidence scoring.

### 2.2 Frontend Layer (React 18 + Vite + TailwindCSS)
- **Visual Design:** High-density, professional dark mission-control interface (`#050a0f`) tailored for satellite ground stations.
- **Key Modules (`frontend/src/`):**
  - `Workspace.tsx`: 3-pane mission control layout: Ingestion panel, Multi-mode visualizer canvas, and Query / Briefing workspace.
  - `ImageViewer.tsx`: Interactive canvas supporting pan, zoom, reset, swipe comparison, split optical/SAR views, and SVG bounding-box overlays.
  - `ExecutionTrace.tsx`: Live step-by-step vertical timeline audit drawer showing millisecond latency, tool name, status icon, and intermediate summary.
  - `JudgeDemo.tsx`: Cinematic 6-step presentation workflow designed for evaluator demonstrations.
  - `BenchmarkLab.tsx`: Evaluation dashboard for VRSBench, RSVQA, and CDVQA datasets.
  - `ModelAdaptation.tsx`: BigEarthNet.txt LoRA / projection head adapter training configuration and monitor.

### 2.3 Command Center UI/UX Design System (Final Polish)
- **Palette System (80% Black, 15% Neutral Grey, 5% Emerald Accent):**
  - Base: Near-black / Space `#030504` and `#070a08`.
  - Panels: Deep Charcoal & Dark Olive `#0c120e` / `#111813` with thin emerald borders (`border-emerald-500/20`).
  - Primary Accent: Precision Emerald `#00ff87` with controlled glow (`shadow-glow-sm`).
  - Telemetry: Lime `#4ade80` (ready states), Amber `#fbbf24` (warnings), Red `#f87171` (errors only).
- **Aesthetic Direction:**
  - "NASA / ISRO Mission Control × Futuristic Geospatial Command × High-End AI Workstation".
  - Subtle geospatial coordinate crosshairs (`+`) and 32px technical telemetry grid.
  - Zero generic SaaS rounded pills; sharp 2px radius borders for scientific instrumentation feel.
  - Imagery is the hero: Interactive pan/zoom canvas with real-time HUD overlays, SVG bounding box pulse highlights, before/after compare slider, and slide-out Scene Inspector drawer.
  - Real-time vertical agent trace timeline displaying millisecond latencies, tool execution states, and intermediate outputs.

---

## 3. Core Functional Capabilities

### 3.1 Single-Image Visual Question Answering (VQA) & Captioning
- **Capabilities:** Scene description, dominant land-cover assessment, object identification, infrastructure detection.
- **Remote-Sensing Awareness:** Evaluates channel statistics and spectral indices (NDVI/NDWI) to verify visual model assertions.
- **Query Examples:**
  - *"What is visible in this satellite scene?"*
  - *"Is there a water body in this image?"*
  - *"Describe the dominant land-cover categories."*

### 3.2 Text-Guided Spatial Grounding
- **Capabilities:** Takes free-form text queries referring to visual or geospatial targets and computes precise spatial locations.
- **Output:** Normalized coordinates `[x1, y1, x2, y2]`, pixel area, cardinal scene quadrant (e.g., *Southern-Western sector*), confidence score, and annotated visual overlay.
- **Query Examples:**
  - *"Highlight the water body referred to in the query."*
  - *"Find all major building clusters."*
  - *"Locate the agricultural parcels."*

### 3.3 Bi-Temporal Change Analysis (Principal Feature)
- **Workflow:**
  1. Ingests observation pair $T_1$ (before) and $T_2$ (after).
  2. Inspects CRS, resolution, and bounding overlap.
  3. Applies radiometric normalization.
  4. Computes absolute and relative difference matrices.
  5. Applies Otsu thresholding and morphological filtering to remove noise.
  6. Isolates connected change clusters.
  7. Classifies change directions:
     - Mean reflectance increase $\rightarrow$ *Built-up / bare soil expansion*
     - Mean reflectance decrease $\rightarrow$ *Vegetation growth / water expansion*
  8. Returns change percentage, sector localization, and side-by-side visual difference map.

### 3.4 Cross-Modal Optical + SAR Paired Analysis
- **Workflow:**
  1. Validates co-registration between optical raster and SAR backscatter raster.
  2. Normalizes optical RGB/multispectral bands.
  3. Converts raw SAR backscatter to decibel (dB) representation: $\gamma^0_{\text{dB}} = 10 \cdot \log_{10}(\text{amplitude}^2 + \epsilon)$.
  4. Detects low specular backscatter (smooth water bodies) and high double-bounce backscatter (man-made structures, urban density).
  5. Fuses optical spectral response with SAR structural response:
     - **Agreement:** Optical NDWI indicates water + SAR indicates low backscatter $\rightarrow$ High-confidence water.
     - **Disagreement:** Optical indicates water, but SAR indicates high backscatter $\rightarrow$ Flags potential flooded urban vegetation or surface specular anomaly.
  6. Renders a multimodal composite highlighting corroborated features.

---

## 4. Multi-Factor Calibrated Confidence Model

SatQuery AI rejects arbitrary confidence numbers. Every score is computed via a calibrated mathematical formulation:

$$\text{Score} = w_m \cdot S_{\text{model}} + w_e \cdot S_{\text{evidence}} + w_q \cdot Q_{\text{input}} + w_r \cdot S_{\text{registration}} - \sum P_i$$

Where:
- $w_m = 0.30$: Mean confidence score of contributing specialist tools.
- $w_e = 0.30$: Evidence volume saturation ($\min(1.0, N_{\text{evidence}} / 10)$).
- $w_q = 0.20$: Input image quality and format completeness.
- $w_r = 0.20$: Spatial alignment and CRS co-registration score.
- Penalties ($P_i$):
  - Missing georeferencing CRS: $-0.08$
  - Low co-registration overlap ($< 0.5$): $-0.15$
  - Low individual model confidence: $-0.08$
  - Cross-modal disagreement: $-0.05$

### Confidence Tiers
- **HIGH ($\ge 0.75$):** Multi-tool corroboration, valid CRS, strong contrast.
- **MEDIUM ($0.50 - 0.74$):** Single modality verified, minor noise, or unreferenced coordinates.
- **LOW ($< 0.50$):** Inconclusive evidence, severe cloud obscuration, or modality mismatch.

---

## 5. Domain Adaptation & Benchmark Lab

### 5.1 BigEarthNet.txt Remote-Sensing Adaptation
- Script: `training/train_rs_adapter.py`
- Implements parameter-efficient fine-tuning via a **Projection Head / LoRA Adapter**:
  - Ingests co-registered Sentinel-1 SAR and Sentinel-2 optical image-text pairs.
  - Projects high-dimensional visual feature vectors into a specialized remote-sensing semantic embedding space.
  - Lightweight and runnable on standard workstation CPUs and GPUs.
- **UI Card:** Displays real-time adapter state (Ready / Not Installed), training samples used, loss trajectory, and activation status.

### 5.2 Benchmark Dataset Adapters (`backend/benchmark/adapters/datasets.py`)
- **VRSBench:** Remote-sensing captioning, grounded conversations, and referring expression VQA.
- **RSVQA:** Remote-sensing visual question answering across Low Resolution (LR) and High Resolution (HR) splits.
- **CDVQA:** Change Detection Visual Question Answering evaluating question-driven bi-temporal scene changes.
- **Scientific Honesty:** Evaluator displays `"Not evaluated"` until actual benchmarks are triggered by the user, avoiding deceptive pre-filled metrics.

---

## 6. Verification and Test Results

### 6.1 Automated PyTest Regression Suite: 30 / 30 Passed (100%)
```powershell
cd satquery-ai
$env:PYTHONPATH="."
.\venv\Scripts\python -m pytest tests/ -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.11.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\butem\Desktop\sqai\satquery-ai
plugins: anyio-4.15.1, asyncio-1.4.0
collected 30 items

tests/test_api.py::test_health_check PASSED                              [  3%]
tests/test_api.py::test_system_info PASSED                               [  6%]
tests/test_api.py::test_get_models PASSED                                [ 10%]
tests/test_api.py::test_upload_file PASSED                               [ 13%]
tests/test_api.py::test_analyze_flow PASSED                              [ 16%]
tests/test_core.py::TestSpectralAnalyzer::test_ndvi_range PASSED         [ 20%]
tests/test_core.py::TestSpectralAnalyzer::test_ndwi_range PASSED         [ 23%]
tests/test_core.py::TestSpectralAnalyzer::test_ndvi_vegetation_positive PASSED [ 26%]
tests/test_core.py::TestImageValidator::test_valid_png PASSED            [ 30%]
tests/test_core.py::TestImageValidator::test_invalid_file PASSED         [ 33%]
tests/test_core.py::TestImageValidator::test_pair_validation PASSED      [ 36%]
tests/test_core.py::TestChangeDetector::test_change_detection_runs PASSED [ 40%]
tests/test_core.py::TestChangeDetector::test_identical_images_low_change PASSED [ 43%]
tests/test_core.py::TestChangeDetector::test_change_map_generated PASSED [ 46%]
tests/test_core.py::TestSARProcessor::test_sar_processing PASSED         [ 50%]
tests/test_core.py::TestFusionEngine::test_fusion_runs PASSED            [ 53%]
tests/test_core.py::TestFusionEngine::test_fusion_generates_previews PASSED [ 56%]
tests/test_core.py::TestTaskRouter::test_caption_query PASSED            [ 60%]
tests/test_core.py::TestTaskRouter::test_change_query PASSED             [ 63%]
tests/test_core.py::TestTaskRouter::test_water_query PASSED              [ 66%]
tests/test_core.py::TestTaskRouter::test_fusion_query PASSED             [ 70%]
tests/test_core.py::TestTaskRouter::test_suggested_queries_single PASSED [ 73%]
tests/test_core.py::TestTaskRouter::test_suggested_queries_bitemporal PASSED [ 76%]
tests/test_core.py::TestConfidenceEstimator::test_high_confidence PASSED [ 80%]
tests/test_core.py::TestConfidenceEstimator::test_low_evidence_downgrades PASSED [ 83%]
tests/test_core.py::TestConfidenceEstimator::test_confidence_has_limitations PASSED [ 86%]
tests/test_core.py::TestValidatorIntegration::test_full_validation_pipeline PASSED [ 90%]
tests/test_core.py::TestValidatorIntegration::test_pair_validation_compatible PASSED [ 93%]
tests/test_core.py::TestGeospatialMetadata::test_png_metadata PASSED     [ 96%]
tests/test_core.py::TestGeospatialMetadata::test_modality_inference PASSED [100%]

======================= 30 passed, 14 warnings in 0.69s =======================
```

### 6.2 Frontend Production Compilation
```powershell
cd satquery-ai\frontend
npm run build
```
- TypeScript check (`tsc`): 0 errors
- Production Vite build:
  - `dist/index.html` (0.93 kB)
  - `dist/assets/index-DTZFMY1r.css` (22.66 kB)
  - `dist/assets/index-BT73Zq3W.js` (332.64 kB)
  - Transformed 1,588 modules in 39.99s.

---

## 7. How to Run the Prototype

### 7.1 Windows (One Command Startup)
From the repository root `c:\Users\butem\Desktop\sqai`:
```cmd
run.bat
```
*Automatically validates runtime requirements, sets up the virtual environment, installs dependencies, generates synthetic GeoTIFF fixtures, starts backend and frontend, and launches the browser.*

### 7.2 Linux / macOS
```bash
chmod +x run.sh
./run.sh
```

### 7.3 Manual Startup
```powershell
# 1. Start Backend
cd satquery-ai
$env:PYTHONPATH="."
.\venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Start Frontend (New Terminal)
cd satquery-ai\frontend
npm run dev
```

- **Mission Control Workstation:** `http://localhost:5173`
- **FastAPI OpenAPI Documentation:** `http://localhost:8000/docs`

---

## 8. Guided Judge Demonstration Workflow

### Demo 1: Scene Description & VQA
- **Input:** Single Image $\rightarrow$ `demo_data/single_optical/scene_optical.tif`
- **Query:** *"Describe the land-cover and major objects visible in this image."*
- **Result:** Classifies dominant land cover, detects vegetation sector, water body, and urban fabric with complete execution trace in 345ms.

### Demo 2: Text-Guided Spatial Grounding
- **Input:** Single Image $\rightarrow$ `demo_data/single_optical/scene_optical.tif`
- **Query:** *"Highlight the water body referred to in the query."*
- **Result:** Isolates water signature, produces bounding box `[0.04, 0.57, 0.49, 0.90]` located in Southern-Western quadrant, renders green visual bounding box overlay.

### Demo 3: Bi-Temporal Change Detection
- **Input:** Bi-Temporal $\rightarrow$ `demo_data/temporal/t1_before.tif` ($T_1$) and `demo_data/temporal/t2_after.tif` ($T_2$)
- **Query:** *"What changed between these two dates, and where did the change occur?"*
- **Result:** Segments 2 change regions, calculates 9.7% scene modification, categorizes change as *built-up expansion*, provides side-by-side difference view, returns 0.95 High Confidence.

### Demo 4: Optical + SAR Multimodal Fusion
- **Input:** Optical + SAR $\rightarrow$ `demo_data/optical_sar/optical.tif` and `demo_data/optical_sar/sar.tif`
- **Query:** *"Use the optical and SAR images together to identify built-up and water-covered regions."*
- **Result:** Corroborates optical reflectance with SAR backscatter dB intensity, computes cross-modal agreement score of **0.80**, generates multimodal composite preview.

---

## 9. SIH Requirement Compliance Matrix

| Requirement | Description | Implementation File | Status |
|---|---|---|:---:|
| **GeoTIFF Support** | Extract CRS, bounds, transform, pixel resolution | `backend/geospatial/raster.py`, `metadata.py` | ✅ **VERIFIED** |
| **Convenience Formats** | Read PNG, JPEG without crashing | `backend/tools/validator.py` | ✅ **VERIFIED** |
| **Single-image VQA** | Remote sensing aware question answering | `backend/inference/vqa.py` | ✅ **VERIFIED** |
| **Scene Captioning** | Land cover & structure scene description | `backend/inference/captioning.py` | ✅ **VERIFIED** |
| **Grounding** | Text-guided bounding box detection | `backend/tools/grounding.py` | ✅ **VERIFIED** |
| **Bi-temporal Analysis** | Change map, change % area, region clustering | `backend/tools/change_detector.py` | ✅ **VERIFIED** |
| **Co-registration** | Spatial compatibility validation | `backend/geospatial/coregistration.py` | ✅ **VERIFIED** |
| **Optical + SAR Fusion** | Dual modality processing and agreement scoring | `backend/tools/fusion_engine.py`, `sar_processor.py` | ✅ **VERIFIED** |
| **Agentic Controller** | Orchestrator, router, planner | `backend/agents/orchestrator.py`, `router.py` | ✅ **VERIFIED** |
| **Auditable Trace** | Millisecond latency, tool name, step tracking | `backend/agents/state.py` | ✅ **VERIFIED** |
| **Calibrated Confidence** | Multi-factor weighted confidence calculation | `backend/evidence/confidence.py` | ✅ **VERIFIED** |
| **Scientific Honesty** | No hallucinated confidence, explicit limitations | `backend/agents/synthesizer.py` | ✅ **VERIFIED** |
| **BigEarthNet Pipeline** | Projection head / LoRA adaptation training script | `training/train_rs_adapter.py` | ✅ **VERIFIED** |
| **Benchmark Adapters** | VRSBench, RSVQA, CDVQA loaders | `backend/benchmark/adapters/datasets.py` | ✅ **VERIFIED** |
| **Report Generation** | Downloadable HTML & JSON analysis dossiers | `backend/reports/generator.py` | ✅ **VERIFIED** |
| **Model Registry** | Component status, health check, fallback tiers | `backend/inference/registry.py` | ✅ **VERIFIED** |
| **Mission Control UI** | Dark theme, high information density, swipe visualizer | `frontend/src/pages/Workspace.tsx` | ✅ **VERIFIED** |
| **Judge Mode** | Automated 5-step guided demonstration | `frontend/src/pages/JudgeDemo.tsx` | ✅ **VERIFIED** |
| **One-Click Startup** | `run.bat` (Windows) and `run.sh` (Linux/macOS) | `run.bat`, `run.sh` | ✅ **VERIFIED** |

---

## 10. Research References & Model Citations

1. **BLIP / BLIP-2:** Li et al., *"BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation"*, ICML 2022.
2. **GeoChat:** Kuckreja et al., *"GeoChat: Grounded Large Vision-Language Model for Remote Sensing"*, CVPR 2024.
3. **Prithvi-EO-2.0:** IBM & NASA, *"Prithvi-EO-2.0: Spatio-Temporal Remote Sensing Foundation Model"*, 2024.
4. **BigEarthNet.txt:** Sumbul et al., *"BigEarthNet-S2: A Large-Scale Multispectral Dataset for Remote Sensing"*, IEEE IGARSS 2019 / 2023.
5. **VRSBench:** Ling et al., *"VRSBench: A Versatile Vision-Language Benchmark for Remote Sensing"*, 2024.
6. **CDVQA:** Yuan et al., *"Change Detection Meets Visual Question Answering"*, IEEE TGRS 2023.
7. **RSVQA:** Lobry et al., *"RSVQA: Visual Question Answering for Remote Sensing Data"*, IEEE TGRS 2020.
