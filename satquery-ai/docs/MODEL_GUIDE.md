# SatQuery AI — Specialist Models & Inference Guide

**Smart India Hackathon 2026 — Problem Statement 26167**  
**Organization:** Indian Space Research Organisation (ISRO)  

---

## 1. Specialist Registry Overview

SatQuery AI decouples remote sensing tasks into modular specialists registered in `backend/inference/registry.py`:

| Model ID | Component Name | Primary Task | Checkpoint / Framework | Execution Device | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `remote_sensing_vqa` | BLIP VQA Specialist | Visual Question Answering | `Salesforce/blip-vqa-base` | CPU / CUDA | Ready |
| `captioning` | BLIP Image Captioner | Land-cover Description | `Salesforce/blip-image-captioning-base` | CPU / CUDA | Ready |
| `grounding` | Grounding Analyzer | Text-guided BBox Extraction | Spectral + Morphological CV | CPU | Ready |
| `change_detection` | Otsu Radiometric Detector | Bi-temporal Change Masking | NumPy + OpenCV + Scipy | CPU | Ready |
| `sar_processor` | SAR Microwave Processor | Backscatter dB & Water Detection | Radiometric Terrain Corrected (RTC) | CPU | Ready |
| `optical_sar_fusion` | Cross-Modal Fusion Engine | Sensor Corroboration | Luminance Overlay & Alpha Blend | CPU | Ready |
| `gemini_analyst` | Gemini Multimodal Analyst | Zero-Hallucination Reasoning | Google Gemini 1.5 Flash / Pro / 2.0 | Cloud API | Configurable |
| `bigearthnet_adapter` | BigEarthNet Domain Adapter | Multi-label Land Classification | PyTorch LoRA Adapter | CPU / CUDA | Training UI Ready |

---

## 2. Gemini Multimodal Analyst Integration

### Purpose
High-level remote sensing queries often involve complex nuance (e.g., distinguishing natural reservoir seasonal drawdown from man-made industrial drainage). `GeminiAnalyst` accepts validated quantitative evidence from local engines and performs expert-grade reasoning.

### Tool Declarations Exposed to Gemini
1. `calculate_spectral_indices(index_types: ['NDVI', 'NDWI', 'NDBI'])`
2. `detect_change(threshold: float)`
3. `analyze_optical_sar()`
4. `ground_text(concept: str)`

### Strict Grounding Contract
Gemini is prompted with explicit constraints:
- **No Hallucinated Numbers:** Never invent pixel counts, area percentages, or decimal index averages.
- **Structured JSON Synthesis:** Outputs must conform strictly to `intent`, `summary`, `visualizations`, and `follow_up_questions`.
- **Local Fallback:** If the API is unreachable, `AnswerSynthesizer` immediately takes over using pure deterministic local logic.

---

## 3. Remote Sensing Adaptation & LoRA Fine-Tuning

The workstation includes dedicated infrastructure for fine-tuning Vision-Language adapters on remote sensing corpora:
- **Training Endpoint:** `POST /api/v1/training/start`
- **Adapter Pipeline:** `training/train_rs_adapter.py`
- **Dataset Support:** BigEarthNet (Sentinel-2 multispectral + Sentinel-1 SAR), RSVQA, and VRSBench.
