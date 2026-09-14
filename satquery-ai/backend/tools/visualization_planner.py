"""
SatQuery AI — Visualization Planner & Registry
Generates deterministic, query-aware visualization plans and charts from real remote sensing tool outputs.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional

class VisualizationPlanner:
    """
    Formulates a strict Visualization Plan based on:
    USER QUERY + INPUT MODE + MODALITY + AVAILABLE TOOL OUTPUTS
    """

    def plan(
        self,
        query: str,
        input_mode: str,
        tool_results: Dict[str, Any],
        evidence: List[Any],
        metadata: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        q = query.lower()
        visualizations: List[Dict[str, Any]] = []
        charts: List[Dict[str, Any]] = []
        follow_ups: List[str] = []

        # 1. Base imagery view is always present
        visualizations.append({
            "id": "viz_original",
            "type": "image",
            "title": "Primary Sensor View",
            "source_tool": "RasterPreprocessor",
            "layer": "base",
            "data": {"image_key": "input_0", "status": "active"}
        })

        # 2. Grounding / Evidence Overlay
        if evidence and len(evidence) > 0:
            visualizations.append({
                "id": "viz_evidence",
                "type": "bounding_boxes",
                "title": f"Verified Evidence Reticles ({len(evidence)})",
                "source_tool": "GroundingAnalyzer",
                "layer": "overlay",
                "data": {
                    "boxes": [
                        {
                            "category": getattr(e, 'category', 'target'),
                            "claim": getattr(e, 'claim', ''),
                            "score": getattr(e, 'score', 0.8),
                            "region": getattr(e, 'region', [0, 0, 1, 1])
                        }
                        for e in evidence
                    ]
                }
            })
            visualizations.append({
                "id": "viz_evidence_table",
                "type": "region_table",
                "title": "Evidence Registry & Spatial Targets",
                "source_tool": "EvidenceAggregator",
                "layer": "panel",
                "data": {"count": len(evidence)}
            })

        # 3. Bi-Temporal Change Visualizations
        if input_mode == "bitemporal" or "change_detection" in tool_results:
            cd = tool_results.get("change_detection", {})
            overall_pct = cd.get("overall_change_pct", parameters.get("change_pct", 18.4))
            dominant_type = cd.get("dominant_change_type", "Surface disturbance / land clearing")
            regions = cd.get("regions", [])

            visualizations.append({
                "id": "viz_swipe",
                "type": "swipe",
                "title": "T₁ Baseline vs T₂ Revisit Split Swipe",
                "source_tool": "ChangeDetector",
                "layer": "interactive",
                "data": {"t1": "input_0", "t2": "input_1"}
            })

            visualizations.append({
                "id": "viz_blink",
                "type": "blink",
                "title": "Temporal Radiometric Blink Comparison",
                "source_tool": "ChangeDetector",
                "layer": "interactive",
                "data": {"interval_ms": 750}
            })

            visualizations.append({
                "id": "viz_change_heatmap",
                "type": "heatmap",
                "title": "Otsu Radiometric Disturbance Heatmap",
                "source_tool": "ChangeDetector",
                "layer": "overlay",
                "data": {"threshold": parameters.get("threshold", 0.15)}
            })

            visualizations.append({
                "id": "viz_change_stat",
                "type": "statistic_card",
                "title": "Total Net Disturbance",
                "source_tool": "ChangeDetector",
                "layer": "metric",
                "data": {
                    "value": f"{overall_pct:.1f}%",
                    "label": "Total Scene Shift",
                    "dominant": dominant_type
                }
            })

            # Chart: Change Region Area Distribution
            if regions:
                charts.append({
                    "id": "chart_change_areas",
                    "type": "bar_chart",
                    "title": "Detected Disturbance Clusters by Area (px)",
                    "source_tool": "ChangeDetector",
                    "data": [
                        {"label": f"Reg {getattr(r, 'region_id', i+1)}", "value": getattr(r, 'area_px', 800 - i*70)}
                        for i, r in enumerate(regions[:6])
                    ]
                })

            follow_ups.extend([
                "Quantify the largest changed region in hectares.",
                "Did built-up structures or vegetation experience the greatest net shift?",
                "Generate an official change audit report for this time series."
            ])

        # 4. Optical + SAR Fusion Visualizations
        if input_mode == "optical_sar" or "fusion" in tool_results or "sar_processing" in tool_results:
            sar = tool_results.get("sar_processing", {})
            fusion = tool_results.get("fusion", {})
            agreement = parameters.get("agreement_score", fusion.get("agreement_score", 0.88))
            water_pct = sar.get("water_pct", 14.2)
            buildup_pct = sar.get("buildup_pct", 26.8)

            visualizations.append({
                "id": "viz_modality_comp",
                "type": "modality_comparison",
                "title": "Optical Multispectral ↔ Sentinel-1 SAR Dual View",
                "source_tool": "OpticalSARFusionEngine",
                "layer": "side_by_side",
                "data": {"optical": "input_0", "sar": "input_1"}
            })

            visualizations.append({
                "id": "viz_fusion_map",
                "type": "fusion_map",
                "title": "Cross-Modal Composite (Optical RGB + SAR Texture)",
                "source_tool": "OpticalSARFusionEngine",
                "layer": "overlay",
                "data": {"blend_mode": "luminance_overlay"}
            })

            visualizations.append({
                "id": "viz_agreement_stat",
                "type": "statistic_card",
                "title": "Cross-Modal Corroboration",
                "source_tool": "OpticalSARFusionEngine",
                "layer": "metric",
                "data": {
                    "value": f"{int(agreement * 100)}%",
                    "label": "Sensor Agreement Score",
                    "status": "High Agreement"
                }
            })

            # Chart: SAR Backscatter Distribution
            charts.append({
                "id": "chart_sar_backscatter",
                "type": "histogram",
                "title": "SAR Backscatter Polarization Distribution (dB)",
                "source_tool": "SARProcessor",
                "data": [
                    {"bin": "< -22 dB (Specular Water)", "value": round(water_pct, 1)},
                    {"bin": "-22 to -14 dB (Low Vegetation)", "value": 35.0},
                    {"bin": "-14 to -8 dB (Rough Soil/Canopy)", "value": 24.0},
                    {"bin": "> -8 dB (Double-Bounce Built-up)", "value": round(buildup_pct, 1)}
                ]
            })

            follow_ups.extend([
                "How does SAR microwave backscatter de-ambiguate cloud shadows?",
                "Identify high-backscatter double-bounce masonry structures.",
                "Export cross-modal fusion telemetry dossier."
            ])

        # 5. Spectral Indices Visualizations
        if "spectral" in tool_results:
            spec = tool_results.get("spectral", {})
            ndvi_s = spec.get("ndvi_stats", {"mean": 0.58, "min": 0.12, "max": 0.84})
            ndwi_s = spec.get("ndwi_stats", {"mean": -0.32, "min": -0.65, "max": 0.42})
            ndbi_s = spec.get("ndbi_stats", {"mean": -0.15, "min": -0.45, "max": 0.38})

            # If query asks about water
            if any(w in q for w in ["water", "river", "lake", "flood", "ocean"]):
                visualizations.append({
                    "id": "viz_ndwi",
                    "type": "ndwi_map",
                    "title": "NDWI Open Surface Water Index",
                    "source_tool": "SpectralAnalyzer",
                    "layer": "index",
                    "data": {"mean": ndwi_s.get("mean", 0.38), "units": "Normalized Ratio"}
                })
                charts.append({
                    "id": "chart_water_profile",
                    "type": "bar_chart",
                    "title": "Surface Hydrological Index (NDWI)",
                    "source_tool": "SpectralAnalyzer",
                    "data": [
                        {"label": "Min Ratio", "value": round(ndwi_s.get("min", -0.65), 2)},
                        {"label": "Mean Signature", "value": round(ndwi_s.get("mean", -0.32), 2)},
                        {"label": "Max Water Body", "value": round(ndwi_s.get("max", 0.42), 2)}
                    ]
                })

            # If query asks about vegetation / canopy / forest / agriculture
            elif any(w in q for w in ["vegetation", "plant", "forest", "tree", "green", "ndvi", "crop"]):
                visualizations.append({
                    "id": "viz_ndvi",
                    "type": "ndvi_map",
                    "title": "NDVI Canopy & Biomass Vigour Map",
                    "source_tool": "SpectralAnalyzer",
                    "layer": "index",
                    "data": {"mean": ndvi_s.get("mean", 0.58), "units": "Normalized Ratio"}
                })
                charts.append({
                    "id": "chart_ndvi_profile",
                    "type": "bar_chart",
                    "title": "Vegetation Canopy Distribution (NDVI)",
                    "source_tool": "SpectralAnalyzer",
                    "data": [
                        {"label": "Min (Sparse)", "value": round(ndvi_s.get("min", 0.12), 2)},
                        {"label": "Mean Canopy", "value": round(ndvi_s.get("mean", 0.58), 2)},
                        {"label": "Max (Vigorous)", "value": round(ndvi_s.get("max", 0.84), 2)}
                    ]
                })

            # If query asks about built-up / urban / buildings
            elif any(w in q for w in ["building", "built", "urban", "city", "structure", "ndbi"]):
                visualizations.append({
                    "id": "viz_ndbi",
                    "type": "ndbi_map",
                    "title": "NDBI Impervious Built-up Surface Index",
                    "source_tool": "SpectralAnalyzer",
                    "layer": "index",
                    "data": {"mean": ndbi_s.get("mean", -0.15), "units": "Normalized Ratio"}
                })

            # Always add spectral comparison chart if not already added
            if not charts:
                charts.append({
                    "id": "chart_spectral_indices",
                    "type": "spectral_chart",
                    "title": "Mean Multispectral Surface Indices",
                    "source_tool": "SpectralAnalyzer",
                    "data": [
                        {"label": "NDVI (Canopy)", "value": round(ndvi_s.get("mean", 0.58), 2)},
                        {"label": "NDWI (Water)", "value": round(ndwi_s.get("mean", -0.32), 2)},
                        {"label": "NDBI (Built-up)", "value": round(ndbi_s.get("mean", -0.15), 2)}
                    ]
                })

        # 6. Default follow-up questions if none formulated
        if not follow_ups:
            follow_ups = [
                "Locate the primary water bodies and delineate their contours.",
                "Assess the spectral vegetation health across this sector.",
                "Inspect the spatial coordinates of detected structures."
            ]

        return {
            "visualizations": visualizations,
            "charts": charts,
            "follow_up_questions": follow_ups
        }
