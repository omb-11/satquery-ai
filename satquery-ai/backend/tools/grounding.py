import numpy as np
import cv2
import rasterio
from dataclasses import dataclass, field
from typing import Dict, Any, List
from io import BytesIO
from PIL import Image, ImageDraw
from .spectral import SpectralAnalyzer
from .sar_processor import SARProcessor

@dataclass
class GroundingResult:
    boxes: List[Dict[str, Any]]
    annotated_image_bytes: bytes
    query_concept: str
    method_used: str
    warnings: List[str] = field(default_factory=list)

class GroundingAnalyzer:
    def ground(self, image_path: str, query: str, metadata: Dict[str, Any] = None) -> GroundingResult:
        query_lower = query.lower()
        concept = "water"
        if any(w in query_lower for w in ["water", "lake", "river", "ocean", "sea", "pond"]):
            concept = "water"
        elif any(w in query_lower for w in ["build", "urban", "city", "road", "structure", "house"]):
            concept = "buildup"
        elif any(w in query_lower for w in ["veg", "tree", "forest", "plant", "crop", "farm", "field", "green"]):
            concept = "vegetation"
            
        mask = None
        method = ""
        
        is_sar = 'sar' in (metadata.get('modality', '') if metadata else '').lower()
        
        if is_sar:
            sp = SARProcessor()
            res = sp.process(image_path)
            if concept == "water":
                mask = res.water_mask
            elif concept == "buildup":
                mask = res.buildup_mask
            method = "sar_intensity_grounding"
        else:
            sa = SpectralAnalyzer()
            res = sa.analyze_raster(image_path, metadata)
            if concept == "water" and res.water_mask is not None:
                mask = res.water_mask
                method = "spectral_ndwi_grounding"
            elif concept == "buildup" and res.buildup_mask is not None:
                mask = res.buildup_mask
                method = "spectral_ndbi_grounding"
            elif concept == "vegetation" and res.vegetation_mask is not None:
                mask = res.vegetation_mask
                method = "spectral_ndvi_grounding"
            
        # If spectral masks weren't generated (e.g. 3-band RGB with no NIR/SWIR), perform RGB optical grounding
        if mask is None or np.sum(mask > 0) == 0:
            try:
                with rasterio.open(image_path) as src:
                    c = min(src.count, 3)
                    bands = [src.read(i+1).astype(np.float32) for i in range(c)]
                    if len(bands) >= 3:
                        r, g, b_band = bands[0], bands[1], bands[2]
                    else:
                        r = g = b_band = bands[0]
                
                brightness = (r + g + b_band) / 3.0
                h, w = r.shape
                
                if concept == "water":
                    # Deep/dark blue or water body signature
                    water_cond = (b_band > r * 1.1) | (brightness < 65) | ((b_band > g) & (b_band > 50) & (r < 80))
                    mask = (water_cond.astype(np.uint8)) * 255
                    method = "optical_color_grounding"
                elif concept == "buildup":
                    # High reflectance, grayish/impervious surface
                    diff_rg = np.abs(r - g)
                    diff_gb = np.abs(g - b_band)
                    buildup_cond = (brightness > 135) & (diff_rg < 35) & (diff_gb < 35)
                    mask = (buildup_cond.astype(np.uint8)) * 255
                    method = "optical_reflectance_grounding"
                elif concept == "vegetation":
                    # Green dominance
                    veg_cond = (g > r * 1.05) & (g > b_band * 1.05) & (g > 40)
                    mask = (veg_cond.astype(np.uint8)) * 255
                    method = "optical_chlorophyll_grounding"
                else:
                    mask = np.zeros((h, w), dtype=np.uint8)
                    method = "fallback"
            except Exception:
                mask = np.zeros((256, 256), dtype=np.uint8)
                method = "fallback_empty"

        if mask.dtype != np.uint8:
            mask = (mask > 0).astype(np.uint8) * 255
            
        # Connected components extraction
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
        
        h, w = mask.shape
        boxes = []
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area < 30: # filter noise
                continue
            x, y, bw, bh = stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP], stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
            norm_box = [round(x/w, 3), round(y/h, 3), round((x+bw)/w, 3), round((y+bh)/h, 3)]
            boxes.append({
                "label": concept,
                "bbox_norm": norm_box,
                "confidence": min(0.92, 0.70 + (area / (w * h)) * 0.5)
            })
            
        # Sort boxes by area (descending) and cap at top 8
        boxes = sorted(boxes, key=lambda b: (b['bbox_norm'][2]-b['bbox_norm'][0])*(b['bbox_norm'][3]-b['bbox_norm'][1]), reverse=True)[:8]
        
        # Load RGB for annotation
        try:
            with rasterio.open(image_path) as src:
                if src.count >= 3:
                    rgb = np.stack([src.read(1), src.read(2), src.read(3)], axis=-1)
                else:
                    rgb = np.stack([src.read(1)]*3, axis=-1)
                    
            for i in range(3):
                p2, p98 = np.percentile(rgb[...,i], (2,98))
                rgb[...,i] = np.clip((rgb[...,i]-p2)/(p98-p2+1e-8), 0, 1)*255
            rgb = rgb.astype(np.uint8)
            img = Image.fromarray(rgb)
        except Exception:
            img = Image.new('RGB', (w, h), color=(30, 40, 50))
            
        draw = ImageDraw.Draw(img)
        for b in boxes:
            x1, y1, x2, y2 = b["bbox_norm"]
            draw.rectangle([x1*w, y1*h, x2*w, y2*h], outline="#00ff87", width=3)
            draw.text((x1*w + 4, y1*h + 4), f"{b['label']} ({b['confidence']:.2f})", fill="#00ff87")
            
        b_io = BytesIO()
        img.save(b_io, format='PNG')
        
        return GroundingResult(
            boxes=boxes,
            annotated_image_bytes=b_io.getvalue(),
            query_concept=concept,
            method_used=method,
            warnings=[]
        )
