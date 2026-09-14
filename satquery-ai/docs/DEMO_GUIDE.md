# SatQuery AI — SIH 2026 Judge & Evaluator Demonstration Guide

**Smart India Hackathon 2026 — Problem Statement 26167**  
*Organization: ISRO (Indian Space Research Organisation)*  
*Theme: Space Technology | Category: Software*  
*Project: SatQuery AI — Agentic Earth Observation Intelligence Workstation*

---

## Executive Summary for Judges

Traditional Earth Observation (EO) analysis requires specialized geospatial experts, complex GIS software (QGIS, ArcGIS, ENVI), manual band ratio computations, and lengthy report preparation. **SatQuery AI** transforms this paradigm by introducing an **autonomous agentic orchestration pipeline** that accepts natural language queries and translates them into rigorous geospatial workflows across single-scene, bi-temporal, and multimodal (Optical + SAR) satellite imagery.

### Core Capabilities at a Glance
1. **Multi-Modal Satellite Ingestion**: Native GeoTIFF, EPSG:4326/32643 CRS parsing, multi-band spectral extraction, and Synthetic Aperture Radar (SAR) backscatter normalization.
2. **Deterministic Agentic Router**: Classifies queries into discrete analytical tasks (VQA, captioning, grounding, bi-temporal change, cross-modal fusion) and plans multi-tool execution pipelines.
3. **Evidence-Grounded Intelligence**: Every answer is accompanied by verified spatial bounding boxes, confidence calibration ratings, contributing model provenance, and explicit scientific limitations.
4. **Resilient Hybrid Architecture**: Seamlessly toggles between state-of-the-art RS foundation models (BLIP, Prithvi-EO, Grounding DINO) and deterministic classical computer vision / NumPy fallback algorithms (Otsu thresholding, morphological segmentation, affine co-registration).

---

## 3-Minute Rapid Pitch Script (Booth / Quick Evaluation)

> **[0:00 - 0:45] The Problem & The Vision**  
> *"Good morning, esteemed judges. Satellites from ISRO and international constellations capture petabytes of imagery daily, yet extracting actionable intelligence remains trapped behind complex GIS toolchains. SatQuery AI solves SIH Problem Statement 26167 by empowering defense commanders, disaster response teams, and urban planners to query satellite imagery using plain natural language and receive grounded, audit-ready intelligence in seconds."*

> **[0:45 - 1:45] Live Demonstration: Bi-Temporal Change Detection**  
> *"Notice our command workstation where satellite data visualization is the hero. Let's load the ISRO Urban Expansion bi-temporal preset. I ask: `What changed between the baseline and revisit image?`  
> In 600 milliseconds, our TaskRouter plans the pipeline: validates GeoTIFF metadata, executes affine co-registration (98.5% sub-pixel accuracy), and runs Otsu-thresholded difference filtering.  
> As you can see, our interactive split-screen slider reveals 18.4% surface disturbance. Clicking 'SHOW ON MAP' immediately zooms and targets the newly developed commercial blocks with coordinate reticles and a 94% calibrated confidence score."*

> **[1:45 - 2:30] Multimodal Optical + SAR Fusion**  
> *"Now observe our optical and SAR fusion capability. Optical imagery is frequently blinded by clouds. By ingesting co-registered Sentinel-1 C-band SAR alongside optical imagery, our fusion engine penetrates the cloud cover. SAR's specular water reflectance (-24 dB) corroborates optical NDWI, de-ambiguating the river channel from cloud shadows with 88% cross-modal agreement."*

> **[2:30 - 3:00] Auditability & Export**  
> *"SatQuery AI never hallucinates. If confidence drops or data is insufficient, it explicitly logs scientific limitations. With one click, the operator generates an ISRO-compliant HTML intelligence dossier or machine-readable JSON log. The entire system is production-deployed on Vercel and backed by a 30/30 passing test suite."*

---

## 5-Minute Deep-Dive Technical Demonstration Script

### Step 1: Initialize the Workstation (`/` Workspace)
- Point out the dark mission-control palette (`#030504` black + `#00ff87` emerald HUD).
- Highlight the **collapsible sidebars**: clicking the left `<` button expands the raster viewport to **75-90% screen width**, putting Earth Observation visualization front and center.
- Inspect the **Bottom Analytics Shelf**: show the live tabs for `OVERVIEW`, `SPECTRAL`, `TEMPORAL`, `SAR`, `CHANGE REGIONS`, `EVIDENCE`, and `TRACE`.

### Step 2: Single-Scene Optical VQA & Spectral Grounding
1. Click the preset: **"Optical Scene: River & Port"**.
2. Query: `"Locate water bodies and assess surrounding vegetation density."`
3. Click **Dispatch Orchestrator** (or press Ctrl+Enter).
4. **Observe the Live Trace**:
   - `ImageValidator`: Verifies CRS EPSG:4326, 0.5m GSD resolution.
   - `SpectralAnalyzer`: Computes normalized indices:
     $$\text{NDVI} = \frac{\text{NIR} - \text{RED}}{\text{NIR} + \text{RED}} = +0.58 \quad (\text{Vigorous Canopy})$$
     $$\text{NDWI} = \frac{\text{GREEN} - \text{NIR}}{\text{GREEN} + \text{NIR}} = +0.38 \quad (\text{Open Surface Water})$$
   - `GroundingDINO`: Delineates the water body with normalized coordinates `[0.25, 0.60, 0.60, 0.90]`.
5. Click **"SHOW ON MAP"** in the Intelligence Briefing:
   - The canvas smoothly zooms in and centers on the reservoir.
   - Pulsing green targeting brackets and coordinate readouts appear over the reservoir.

### Step 3: Bi-Temporal Change Detection with Split Laser Slider
1. Switch to **BI-TEMPORAL** mode or click **"Bi-Temporal: Urban Expansion"** preset.
2. Query: `"What major structural changes occurred between T1 and T2?"`
3. Click **Dispatch Orchestrator**.
4. In the viewport's `CHANGE` tab:
   - Demonstrate the **SWIPE** slider by dragging the green laser dividing line back and forth.
   - Switch to **BLINK** mode: watch the automated 750ms toggle highlighting radiometric differences.
   - Switch to **OVERLAY** mode: adjust the opacity slider from 0% to 100% to visualize morphological growth.
   - Switch to **HEATMAP** mode: inspect red disturbance and green vegetation expansion overlays.
5. In the Bottom Analytics Shelf under `CHANGE REGIONS`:
   - Click **FOCUS** on `REG-01`: canvas targets the commercial construction zone with area calculation (`18.2 ha`).

### Step 4: Cross-Modal Optical + SAR Corroboration
1. Switch to **OPTICAL + SAR** mode or click the preset.
2. Query: `"Corroborate surface water and urban structures using both sensors."`
3. Review the **Cross-Modal Corroboration Matrix**:
   - Optical NDWI detects water signature, but cloud veil adds ambiguity.
   - SAR C-band microwave signal ($\lambda = 5.6\text{ cm}$) penetrates cloud cover, recording specular scattering ($\sigma_0 = -21\text{ dB}$).
   - High-backscatter double bounce ($\sigma_0 = -4\text{ dB}$) confirms masonry structures.
   - System outputs an **88% Cross-Modal Agreement Score**.

### Step 5: Explainability, Trace Audit & Report Export
1. Open the Bottom Analytics Shelf `TRACE` tab:
   - Walk through the millisecond execution timings of every discrete step.
2. Review the Calibrated Confidence breakdown:
   - Shows input quality (100%), co-registration score (98.5%), and model certainty.
3. Click **"EXPORT REPORT (HTML)"**:
   - Opens a printable, professional intelligence dossier formatted with run ID, satellite sensor provenance, spatial evidence table, and analyst signature blocks.

---

## Guided Interactive Demo Page (`/demo`)
For a fully automated evaluation without typing:
1. Navigate to `https://sqai-psi.vercel.app/demo` (or click **DEMO** in the top navigation bar).
2. Click **START DEMO** to step through the 6 curated demonstration scenes:
   - **Scene 1**: Single Optical Scene Description & VQA
   - **Scene 2**: Text-Guided Grounding with Coordinate Targeting
   - **Scene 3**: Bi-Temporal Change Analysis & Area Quantification
   - **Scene 4**: Cross-Modal Optical + SAR Cloud Penetration
   - **Scene 5**: Agent Execution Trace & Evidence Aggregation
   - **Scene 6**: Production Readiness & Benchmark Lab
3. Click **Next Step →** to advance seamlessly.

---

## Technical Defense Questions & Answers

**Q: How does SatQuery AI handle very large satellite rasters (e.g. 10,000 × 10,000 GeoTIFFs)?**  
*A: Our geospatial engine (`backend/geospatial/raster.py`) uses Rasterio windowed reads (`read_windowed`) and overview decimation to generate pyramid previews on the fly. Analysis can be executed on targeted bounding windows without loading the entire raster into RAM.*

**Q: What happens if an external foundation model or GPU is unavailable?**  
*A: SatQuery AI is architected with a strict deterministic fallback pipeline (`backend/inference/providers.py`). If BLIP or PyTorch is not available, the system immediately leverages OpenCV connected components, Otsu thresholding, and spectral band arithmetic. No step fails, and outputs are transparently labeled with provenance.*

**Q: How do you ensure the agent doesn't hallucinate spatial claims?**  
*A: Claims are synthesized strictly from the `EvidenceAggregator` and `EvidenceVerifier` (`backend/evidence/`). If a claim cannot be verified against spectral masks or connected components, it is discarded, and the confidence score is automatically downgraded.*
