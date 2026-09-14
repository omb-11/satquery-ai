import numpy as np
import cv2
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from io import BytesIO
from PIL import Image
from .preprocessor import RasterPreprocessor

@dataclass
class ChangeRegion:
    region_id: int
    bbox: Tuple[float, float, float, float]
    area_px: int
    area_pct: float
    centroid: Tuple[float, float]
    confidence: float
    change_type: str
    change_direction: str

@dataclass
class ChangeResult:
    regions: List[ChangeRegion]
    change_map_bytes: bytes
    diff_visualization_bytes: bytes
    t1_preview_bytes: bytes
    t2_preview_bytes: bytes
    overall_change_pct: float
    dominant_change_type: str
    backend_used: str
    confidence_score: float
    stats: Dict[str, Any]

class ChangeDetector:
    def detect(self, t1_path: str, t2_path: str, threshold: float = 0.15, min_area_px: int = 50, query: str = '') -> ChangeResult:
        prep = RasterPreprocessor()
        r1 = prep.preprocess(t1_path, {})
        r2 = prep.preprocess(t2_path, {})
        
        arr1 = r1.normalized_arr
        arr2 = r2.normalized_arr
        
        # Ensure same size
        h, w = min(arr1.shape[0], arr2.shape[0]), min(arr1.shape[1], arr2.shape[1])
        arr1 = cv2.resize(arr1, (w, h))
        arr2 = cv2.resize(arr2, (w, h))
        
        # Grayscale diff
        g1 = cv2.cvtColor(arr1[..., :3], cv2.COLOR_RGB2GRAY) if arr1.shape[-1] >= 3 else arr1[..., 0]
        g2 = cv2.cvtColor(arr2[..., :3], cv2.COLOR_RGB2GRAY) if arr2.shape[-1] >= 3 else arr2[..., 0]
        
        diff = cv2.absdiff(g1, g2)
        _, thresh = cv2.threshold(diff, int(threshold * 255), 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
        
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cleaned, connectivity=8)
        
        regions = []
        total_pixels = h * w
        
        change_map = np.zeros((h, w, 3), dtype=np.uint8)
        change_map[..., 1] = 255 # Green background
        
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area < min_area_px:
                continue
                
            x, y, bw, bh = stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP], stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
            mask = (labels == i)
            
            m1 = g1[mask].mean()
            m2 = g2[mask].mean()
            direction = "brighter" if m2 > m1 else "darker"
            ctype = "built-up/bare" if direction == "brighter" else "water/vegetation"
            
            color = (255, 0, 0) if direction == "brighter" else (0, 0, 255) # Red or Blue
            change_map[mask] = color
            
            regions.append(ChangeRegion(
                region_id=i,
                bbox=(x/w, y/h, (x+bw)/w, (y+bh)/h),
                area_px=int(area),
                area_pct=(area/total_pixels)*100,
                centroid=(centroids[i][0]/w, centroids[i][1]/h),
                confidence=min(1.0, area/1000.0),
                change_type=ctype,
                change_direction=direction
            ))
            
        change_pct = (sum(r.area_px for r in regions) / total_pixels) * 100
        types = [r.change_type for r in regions]
        dominant = max(set(types), key=types.count) if types else "none"
        
        def to_bytes(arr):
            b = BytesIO()
            Image.fromarray(arr).save(b, format="PNG")
            return b.getvalue()
            
        return ChangeResult(
            regions=regions,
            change_map_bytes=to_bytes(change_map),
            diff_visualization_bytes=to_bytes(np.hstack((arr1[...,:3], arr2[...,:3]))),
            t1_preview_bytes=r1.preview_bytes,
            t2_preview_bytes=r2.preview_bytes,
            overall_change_pct=change_pct,
            dominant_change_type=dominant,
            backend_used="classical_cv",
            confidence_score=0.85,
            stats={"num_regions": len(regions)}
        )
