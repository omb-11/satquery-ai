# SatQuery AI — Model Registry & Attribution

This document details the various foundation models, architectures, and datasets utilized or referenced within the SatQuery AI system.

## 1. BLIP (Bootstrapping Language-Image Pre-training)
- **Model Name**: BLIP
- **Paper / Reference**: *BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation* (Li et al., 2022)
- **Official Repository**: https://github.com/salesforce/BLIP
- **License**: BSD 3-Clause
- **Role in SatQuery AI**: Primary Visual Question Answering (VQA) and image captioning for standard optical imagery.
- **Integration Status**: Integrated
- **Notes**: Served via HuggingFace `transformers`. Lightweight and efficient for general feature extraction.

## 2. BLIP-2
- **Model Name**: BLIP-2
- **Paper / Reference**: *BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models* (Li et al., 2023)
- **Official Repository**: https://github.com/salesforce/LAVIS
- **License**: BSD 3-Clause
- **Role in SatQuery AI**: Enhanced VQA for complex spatial reasoning and detailed captioning.
- **Integration Status**: Integrated
- **Notes**: Used when the orchestrator determines high-complexity reasoning is required.

## 3. GeoChat
- **Model Name**: GeoChat
- **Paper / Reference**: *GeoChat: Grounded Large Vision-Language Model for Remote Sensing* (Kuckreja et al., 2023)
- **Official Repository**: https://github.com/mbzuai-oryx/GeoChat
- **License**: Apache 2.0
- **Role in SatQuery AI**: Remote Sensing specific VLM architecture guiding prompt engineering and visual-language alignment strategies.
- **Integration Status**: Reference
- **Notes**: Serves as a reference for RS-specific adaptation techniques.

## 4. Prithvi-EO-2.0
- **Model Name**: Prithvi-EO-2.0
- **Paper / Reference**: *Prithvi: A Foundation Model for Earth Observation* (Jakubik et al., 2023)
- **Official Repository**: https://github.com/NASA-IMPACT/hls-foundation-os
- **License**: Apache 2.0
- **Role in SatQuery AI**: Multispectral and temporal remote sensing foundation model for feature extraction.
- **Integration Status**: Planned
- **Notes**: Targeted for advanced multispectral analysis and land cover classification tasks.

## 5. Grounding DINO
- **Model Name**: Grounding DINO
- **Paper / Reference**: *Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection* (Liu et al., 2023)
- **Official Repository**: https://github.com/IDEA-Research/GroundingDINO
- **License**: Apache 2.0
- **Role in SatQuery AI**: Text-guided open-vocabulary object detection and spatial grounding.
- **Integration Status**: Integrated
- **Notes**: Used by the agent to highlight specific entities (e.g., "Find all airplanes").

## 6. SAM2 (Segment Anything Model 2)
- **Model Name**: SAM 2
- **Paper / Reference**: *Segment Anything 2* (Ravi et al., 2024)
- **Official Repository**: https://github.com/facebookresearch/segment-anything-2
- **License**: Apache 2.0
- **Role in SatQuery AI**: Zero-shot high-precision segmentation.
- **Integration Status**: Integrated
- **Notes**: Can be prompted via bounding boxes from Grounding DINO to produce precise masks.

## 7. BigEarthNet
- **Model Name**: BigEarthNet
- **Paper / Reference**: *BigEarthNet: A Large-Scale Multispectral Image Archive for Remote Sensing Image Understanding* (Sumbul et al., 2019)
- **Official Repository**: https://bigearth.net/
- **License**: Open Data Commons Open Database License (ODbL)
- **Role in SatQuery AI**: Dataset for fine-tuning adapter modules to adapt generic vision models to RS imagery.
- **Integration Status**: Reference
- **Notes**: Used in the training pipeline (`train_rs_adapter.py`).

## 8. VRSBench
- **Model Name**: VRSBench
- **Paper / Reference**: *VRSBench: A Comprehensive Benchmark for Visual Question Answering in Remote Sensing*
- **Official Repository**: N/A
- **License**: Varies
- **Role in SatQuery AI**: Benchmark dataset used in the Benchmark Lab.
- **Integration Status**: Integrated
- **Notes**: Used to evaluate system reasoning and VQA capabilities on RS specific tasks.

## 9. RSVQA
- **Model Name**: RSVQA
- **Paper / Reference**: *RSVQA: Visual Question Answering for Remote Sensing Data* (Lobry et al., 2020)
- **Official Repository**: https://github.com/syed-zain-raza/RSVQA
- **License**: CC BY-NC-SA 4.0
- **Role in SatQuery AI**: Benchmark dataset.
- **Integration Status**: Integrated
- **Notes**: Used in the validation suite.

## 10. CDVQA
- **Model Name**: CDVQA (Change Detection VQA)
- **Paper / Reference**: *Change Detection Visual Question Answering*
- **Official Repository**: N/A
- **License**: Varies
- **Role in SatQuery AI**: Benchmark dataset for bi-temporal visual question answering.
- **Integration Status**: Integrated
- **Notes**: Assesses the system's ability to analyze temporal changes.

## 11. LEVIR-CD
- **Model Name**: LEVIR-CD
- **Paper / Reference**: *Spatial-Temporal Attention Neural Network for Building Change Detection in Remote Sensing Images* (Chen et al., 2020)
- **Official Repository**: https://justcheneng.github.io/LEVIR/
- **License**: CC BY-NC-SA 4.0
- **Role in SatQuery AI**: Change detection dataset.
- **Integration Status**: Reference
- **Notes**: Used to evaluate the bi-temporal change analysis tool.

## 12. OpenCV
- **Model Name**: OpenCV
- **Paper / Reference**: *Open Source Computer Vision Library*
- **Official Repository**: https://github.com/opencv/opencv
- **License**: Apache 2.0
- **Role in SatQuery AI**: Classical computer vision processing, image pre-processing, transformations, and alignment.
- **Integration Status**: Integrated
- **Notes**: Core dependency for the execution trace and evidence verification.

## 13. Rasterio / GDAL
- **Model Name**: Rasterio / GDAL
- **Paper / Reference**: N/A
- **Official Repository**: https://github.com/rasterio/rasterio
- **License**: BSD 3-Clause / MIT
- **Role in SatQuery AI**: Geospatial data reading, writing, coordinate reference system (CRS) management, and large image block processing.
- **Integration Status**: Integrated
- **Notes**: Crucial for handling GeoTIFFs and large geospatial arrays.
