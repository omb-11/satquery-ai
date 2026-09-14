"""
SatQuery AI — Spatial Focus Engine
Interprets spatial constraints in natural language queries and extracts focus regions.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional

class SpatialFocusEngine:
    """Interprets directional & entity spatial language to target raster regions."""

    DIRECTION_MAP = {
        "north": [0.0, 0.0, 1.0, 0.5],
        "northern": [0.0, 0.0, 1.0, 0.5],
        "south": [0.0, 0.5, 1.0, 1.0],
        "southern": [0.0, 0.5, 1.0, 1.0],
        "east": [0.5, 0.0, 1.0, 1.0],
        "eastern": [0.5, 0.0, 1.0, 1.0],
        "west": [0.0, 0.0, 0.5, 1.0],
        "western": [0.0, 0.0, 0.5, 1.0],
        "northeast": [0.5, 0.0, 1.0, 0.5],
        "north-east": [0.5, 0.0, 1.0, 0.5],
        "northwest": [0.0, 0.0, 0.5, 0.5],
        "north-west": [0.0, 0.0, 0.5, 0.5],
        "southeast": [0.5, 0.5, 1.0, 1.0],
        "south-east": [0.5, 0.5, 1.0, 1.0],
        "southwest": [0.0, 0.5, 0.5, 1.0],
        "south-west": [0.0, 0.5, 0.5, 1.0],
        "center": [0.25, 0.25, 0.75, 0.75],
        "central": [0.25, 0.25, 0.75, 0.75],
    }

    def extract_focus(self, query: str, evidence: List[Any] = None, metadata: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extract query-directed spatial bounding boxes and associate with real metadata coordinates.
        """
        q = query.lower()
        focus_items = []

        # 1. Match directional keywords
        for keyword, bbox in self.DIRECTION_MAP.items():
            if f" {keyword} " in f" {q} ":
                item = {
                    "type": "directional_sector",
                    "label": f"{keyword.capitalize()} Sector",
                    "bbox_norm": bbox,
                    "reason": f"Query specifically referenced the {keyword} sector"
                }
                # If georeference metadata exists, attach geographic coordinates
                if metadata and len(metadata) > 0 and "bounds" in metadata[0]:
                    b = metadata[0]["bounds"]
                    # Calculate sub-bounds
                    left, bottom, right, top = b.get("left", 0), b.get("bottom", 0), b.get("right", 1), b.get("top", 1)
                    sub_w = right - left
                    sub_h = top - bottom
                    item["geo_bounds"] = {
                        "left": left + bbox[0] * sub_w,
                        "bottom": bottom + (1.0 - bbox[3]) * sub_h,
                        "right": left + bbox[2] * sub_w,
                        "top": bottom + (1.0 - bbox[1]) * sub_h,
                    }
                focus_items.append(item)
                break

        # 2. Check for change/disturbance focus
        if any(w in q for w in ["changed area", "where changed", "difference area", "new structure"]):
            if evidence:
                change_evs = [e for e in evidence if getattr(e, 'source', '') == 'change_detector']
                if change_evs:
                    top_ev = change_evs[0]
                    reg = getattr(top_ev, 'region', [0.2, 0.2, 0.8, 0.8])
                    focus_items.append({
                        "type": "change_cluster",
                        "label": "Primary Disturbance Cluster",
                        "bbox_norm": reg,
                        "reason": f"Top detected change zone: {getattr(top_ev, 'claim', 'Surface discrepancy')}"
                    })

        # 3. Check for specific entity references (water body, building)
        if "water" in q or "river" in q or "lake" in q:
            if evidence:
                water_evs = [e for e in evidence if "water" in getattr(e, 'category', '').lower() or "water" in getattr(e, 'claim', '').lower()]
                if water_evs:
                    top_w = water_evs[0]
                    focus_items.append({
                        "type": "water_target",
                        "label": "Water Body Target",
                        "bbox_norm": getattr(top_w, 'region', [0.25, 0.60, 0.60, 0.90]),
                        "reason": "Spectral NDWI and specular backscatter identified water feature"
                    })

        return focus_items
