import numpy as np
import rasterio
from dataclasses import dataclass, field
from typing import Dict, Any, List
from io import BytesIO
from PIL import Image

@dataclass
class SARResult:
    normalized_arr: np.ndarray
    water_mask: np.ndarray
    buildup_mask: np.ndarray
    water_pct: float
    buildup_pct: float
    preview_bytes: bytes
    stats: Dict[str, float]
    polarization_hint: str

class SARProcessor:
    def process(self, path: str, metadata: Dict[str, Any] = None) -> SARResult:
        with rasterio.open(path) as src:
            arr = src.read(1).astype(float)
            
        norm = self.normalize_sar_backscatter(arr)
        
        water = self.detect_water_sar(arr)
        buildup = self.detect_buildup_sar(arr)
        
        total = arr.size
        
        preview = np.repeat(norm[..., np.newaxis], 3, axis=-1)
        img = Image.fromarray(preview)
        b = BytesIO()
        img.save(b, format='PNG')
        
        return SARResult(
            normalized_arr=norm,
            water_mask=water,
            buildup_mask=buildup,
            water_pct=(np.count_nonzero(water) / total) * 100,
            buildup_pct=(np.count_nonzero(buildup) / total) * 100,
            preview_bytes=b.getvalue(),
            stats={'mean_db': float(np.mean(10 * np.log10(np.clip(arr, 1e-6, None))))},
            polarization_hint="unknown"
        )
        
    def normalize_sar_backscatter(self, arr: np.ndarray) -> np.ndarray:
        valid = np.clip(arr, 1e-6, None)
        db = 10 * np.log10(valid)
        p1, p99 = np.percentile(db, (1, 99))
        norm = np.clip((db - p1) / (p99 - p1 + 1e-8), 0, 1)
        return (norm * 255).astype(np.uint8)

    def detect_water_sar(self, arr: np.ndarray) -> np.ndarray:
        db = 10 * np.log10(np.clip(arr, 1e-6, None))
        thresh = np.percentile(db, 15) # Heuristic for low backscatter
        return (db < thresh).astype(np.uint8)

    def detect_buildup_sar(self, arr: np.ndarray) -> np.ndarray:
        db = 10 * np.log10(np.clip(arr, 1e-6, None))
        thresh = np.percentile(db, 85) # Heuristic for high backscatter
        return (db > thresh).astype(np.uint8)
