# SatQuery AI — System Architecture & Design Specification

**Smart India Hackathon 2026 — Problem Statement 26167**  
**Organization:** Indian Space Research Organisation (ISRO)  
**Category:** Software | **Theme:** Space Technology  

---

## 1. Executive Summary

SatQuery AI is an agentic Earth Observation (EO) intelligence workstation designed for non-expert and expert operators alike. It transforms natural language inquiries into rigorous, multi-step analytical pipelines across single-scene, bi-temporal, and cross-modal optical + SAR imagery.

### Core Architectural Axioms
1. **Deterministic Grounding First:** Machine learning and vision-language models never operate in a vacuum. Every high-level claim must be corroborated by raw radiometric computations (e.g., NDVI, NDWI, Otsu difference masks, radar backscatter $\sigma^0$ dB).
2. **Zero-Hallucination Multimodal Reasoning:** High-parameter foundation models (e.g., Google Gemini 1.5 Flash / Pro) receive structured tool declarations and verified raster metrics, functioning strictly as reasoning analysts rather than ungrounded generative engines.
3. **Calibrated Confidence:** Confidence scores explicitly incorporate signal quality, geographic co-registration overlap, and model uncertainty factors, penalizing missing projections or high atmospheric attenuation.
4. **Offline Intelligence Dossiers:** Every analysis run produces an executive HTML dossier that is 100% self-contained, embeddable, and printable without active internet connectivity.

---

## 2. High-Level System Architecture

```
                                  +---------------------------------------+
                                  |    OPERATOR / JUDGE WEB INTERFACE     |
                                  | (React + Vite + Tailwind + SVG Canvas)|
                                  +-------------------+-------------------+
                                                      |
                                     REST / SSE Stream (Port 8000)
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       FASTAPI AGENT ORCHESTRATOR      |
                                  |        (backend/main.py:app)          |
                                  +-------------------+-------------------+
                                                      |
                 +------------------------------------+-----------------------------------+
                 |                                    |                                   |
                 v                                    v                                   v
      +----------------------+             +----------------------+            +----------------------+
      |   PRE-FLIGHT STAGE   |             |   EXECUTION PIPELINE |            |  SYNTHESIS & REPORT  |
      +----------------------+             +----------------------+            +----------------------+
      | 1. Image Validator   |             | 4. Task Router       |            | 8. Evidence Verifier |
      | 2. Rasterio / GDAL   |             | 5. Task Planner      |            | 9. Gemini RS Analyst |
      | 3. Co-Registration   |             | 6. Specialist Tools  |            | 10. Dossier Engine   |
      +----------------------+             +----------------------+            +----------------------+
                                                      |
                  +-----------------------------------+-----------------------------------+
                  |                                   |                                   |
                  v                                   v                                   v
       [Spectral Index Engine]            [Bi-Temporal Change]                 [Optical+SAR Fusion]
       - NDVI (Vegetation)                - Normalized Absolute Diff           - S2 RGB Luminance
       - NDWI (Surface Water)             - Otsu Dynamic Threshold            - S1 Backscatter dB
       - NDBI (Built-Up Areas)            - Morphological Filtering            - Cross-Modal Agreement
```

---

## 3. Seven-Stage Agentic Pipeline

1. **VALIDATE:** Rasterio & GDAL inspect image headers, CRS projection (EPSG), pixel aspect ratio, and bit depth. If bi-temporal or optical+SAR pairs are provided, spatial intersection and GSD resolution ratios are verified.
2. **CLASSIFY:** `TaskRouter` analyzes natural language syntax and token embeddings to route to `SINGLE_VQA`, `SINGLE_CAPTION`, `CHANGE_DETECTION`, `CHANGE_VQA`, or `OPTICAL_SAR_FUSION`.
3. **SPATIAL FOCUS:** `SpatialFocusEngine` detects cardinal compass sectors (e.g., "northwest quadrant") or entity targets, mapping normalized coordinates $[x_1, y_1, x_2, y_2]$ to WGS-84 bounding coordinates.
4. **DISPATCH & EXECUTE:** `TaskPlanner` sequences specialist modules:
   - `SpectralAnalyzer` computes floating-point index arrays and vegetation/water masks.
   - `ChangeDetector` computes Otsu radiometric difference, extracting bounding clusters and pixel shifts.
   - `SARProcessor` calibrates Sentinel-1 backscatter to decibel scale ($\text{dB}$) and identifies specular vs. double-bounce surfaces.
   - `OpticalSARFusionEngine` integrates optical multispectral signatures with microwave penetration.
5. **EVIDENCE AGGREGATION:** `EvidenceAggregator` and `EvidenceVerifier` prune ungrounded hypotheses, enforce spatial consistency, and compute a calibrated confidence metric.
6. **REASONING & SYNTHESIS:** `GeminiAnalyst` (or local deterministic fallback) processes the verified evidence items and produces structured JSON verdicts, follow-up investigation questions, and executive summaries.
7. **AUDIT & DOSSIER:** `ReportGenerator` compiles an offline HTML intelligence briefing embedding SVG charts, execution trace timestamps, and raster provenance.

---

## 4. Precision Control Modes

SatQuery AI introduces selectable precision tiers:

| Mode | Pipeline Scope | Typical Latency | Key Use Case |
| :--- | :--- | :--- | :--- |
| **FAST** | Rapid VQA + Screening Spectral Indices | ~1.2s | Tactical triage & quick visual Q&A |
| **BALANCED** | Standard evidence aggregation & validation | ~2.8s | Operational mission workflows |
| **PRECISE** | Multimodal fusion & spatial focus reticles | ~4.5s | Detailed geospatial land-use analysis |
| **EXPERT** | Complete audit trace + deep Gemini reasoning | ~6.0s | Official mission debriefs & SIH judging |

---

## 5. Security & Credentials Architecture

- **Zero Client Exposure:** `GEMINI_API_KEY` is strictly confined to backend execution. The frontend never accesses raw keys.
- **Masked Configuration:** The `/api/v1/settings/gemini` endpoint masks API keys (`AIzaSy••••••••`), preventing unauthorized inspection.
- **Local Fallback Mode:** When an external API key is absent, the system automatically engages local remote sensing deterministic synthesizers with zero runtime exceptions.
