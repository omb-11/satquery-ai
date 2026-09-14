# SATQUERY AI
**Agentic Earth Observation Intelligence Workstation**
*Smart India Hackathon 2026 — Problem Statement 26167*
*Organization: ISRO | Category: Software | Theme: Space Technology*

## Problem Statement
Earth Observation (EO) analysis typically requires specialized domain experts, expensive software, and considerable manual processing. This makes critical geospatial insights slow to acquire and inaccessible to non-experts, emergency responders, and decision-makers.

## Solution
SatQuery AI democratizes remote sensing by providing a natural language interface to complex EO data. Users can simply ask questions in plain English. Behind the scenes, an agentic orchestration engine formulates a plan, selects specialized vision models, runs analytical tools, validates the findings, and synthesizes an evidence-backed answer.

## Architecture Overview
```text
  [ User Request ] -> [ Natural Language Query ]
                            |
                     [ Orchestrator Agent ]
                     /       |        \
        [ Task Router ] [ Validator ] [ Trace State ]
           /                |               \
    [ CV Models ]     [ Geospatial ]     [ Analytics ]
    - VQA             - GeoTIFF          - Indices
    - Grounding       - Co-register      - Fusion
    - Segmentation    - SAR processing   - Change Detect
           \                |               /
            \_______ [ Aggregator ] _______/
                            |
                   [ Evidence Verifier ]
                            |
                [ Answer + Confidence Score ]
```

## Agentic Workflow
1. **ASK**: User submits a query alongside imagery (Optical, SAR, or Bi-temporal).
2. **PLAN**: Orchestrator builds a multi-step execution plan based on the query.
3. **VALIDATE**: Checks image types, resolutions, and compatibility.
4. **ANALYZE**: Routes tasks to specialized models (e.g., BLIP, SAM2) or classical algorithms (e.g., NDVI, Coregistration).
5. **EVIDENCE**: Collects outputs (masks, boxes, textual features, metric values).
6. **ANSWER**: Synthesizes a coherent natural language response.
7. **AUDIT**: Exposes the complete execution trace and confidence scores to the user.

## Key Features
- **VQA (Visual Question Answering)**: Talk to your satellite imagery.
- **Bi-temporal Change Detection**: Highlight differences between two timestamps.
- **Optical + SAR Fusion**: Leverage multi-modal data for superior analysis.
- **Text-Guided Grounding**: Automatically draw bounding boxes around queried entities.
- **Geospatial Processing**: Native support for GeoTIFFs, metadata, and raster ops.

## Model Registry
See `docs/MODELS.md` for a complete list of integrated foundation models, including BLIP, Grounding DINO, SAM2, and reference architectures like GeoChat.

## Remote Sensing Adaptation
The system includes functionality to adapt generic vision-language models to the remote sensing domain using datasets like BigEarthNet. Check the `training/train_rs_adapter.py` script for adaptation details.

## Benchmarks
Integrated benchmark adapters are provided for standard RS datasets:
- **VRSBench**
- **RSVQA**
- **CDVQA**
Access the Benchmark Lab via the frontend UI to run evaluations.

## Installation

```bash
# Clone the repository
git clone https://github.com/username/satquery-ai.git
cd satquery-ai

# Backend Setup (Requires Python 3.11+)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Frontend Setup (Requires Node 20+)
cd frontend
npm install
cd ..
```

## Running Locally

**Using the launch script (Windows):**
```bash
run.bat
```

**Manual Start:**
Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```
Access the application at `http://localhost:5173`.

### CPU Mode Notes
If running without a dedicated GPU, ensure environment variables (e.g., `USE_CPU=true`, `CUDA_VISIBLE_DEVICES=-1`) are set. Inference will be slower.

## Demo Usage
A dedicated presentation mode for judges is available at the `/demo` route in the frontend app (`JudgeDemo.tsx`), highlighting the core SIH requirements.

## API Documentation
Once the backend is running, visit `http://localhost:8000/docs` for the interactive Swagger OpenAPI documentation.

## Troubleshooting
- **Memory Errors**: Large GeoTIFFs can cause OOM. Ensure `backend/geospatial/raster.py` is utilizing chunking.
- **Model Downloads**: First run will download HF weights. Ensure stable internet.

## Known Limitations
- CPU inference is significantly slower.
- Base configuration does not include advanced GPU scheduling or TensorRT optimizations.
- Multi-gigabyte single-image GeoTIFFs may require pre-tiling.

## Licenses
SatQuery AI is released under the MIT License. Included models (BLIP, SAM2, etc.) are subject to their respective licenses (e.g., Apache 2.0, BSD). See `MODELS.md` for details.

## Citations
* Li, J., et al. (2022). BLIP. ICML.
* Li, J., et al. (2023). BLIP-2. ICML.
* Kuckreja, et al. (2023). GeoChat. CVPR.
* Sumbul, G., et al. (2019). BigEarthNet. IGARSS.
*(Full BibTeX available in project documentation)*
