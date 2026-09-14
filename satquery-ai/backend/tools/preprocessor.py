import numpy as np
import cv2
import rasterio
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, List
from io import BytesIO
from PIL import Image

@dataclass
class PreprocessResult:
    original_shape: Tuple[int, int]
    processed_shape: Tuple[int, int]
    normalized_arr: np.ndarray
    preview_bytes: bytes
    method_used: str
    warnings: List[str] = field(default_factory=list)

class RasterPreprocessor:
    def preprocess(self, path: str, metadata: Dict[str, Any], target_dim: int = 1024) -> PreprocessResult:
        with rasterio.open(path) as src:
            arr = src.read()
            orig_shape = (src.width, src.height)
            
        arr = np.moveaxis(arr, 0, -1)
        
        resized = self.resize_to_max_dim(arr, target_dim)
        proc_shape = (resized.shape[1], resized.shape[0])
        
        is_sar = 'SAR' in metadata.get('modality', '').upper()
        if is_sar or (resized.shape[-1] == 1 and arr.dtype != np.uint8):
            norm_arr = self.normalize_sar(resized)
            method = "sar_db_normalization"
        else:
            norm_arr = self.normalize_optical(resized)
            method = "optical_percentile_stretch"
            
        if norm_arr.shape[-1] == 1:
            preview_arr = np.repeat(norm_arr, 3, axis=-1)
        elif norm_arr.shape[-1] >= 3:
            preview_arr = norm_arr[..., :3]
        else:
            preview_arr = np.pad(norm_arr, ((0,0), (0,0), (0, 3 - norm_arr.shape[-1])))
            
        img = Image.fromarray(preview_arr)
        bio = BytesIO()
        img.save(bio, format='PNG')
        
        return PreprocessResult(
            original_shape=orig_shape,
            processed_shape=proc_shape,
            normalized_arr=norm_arr,
            preview_bytes=bio.getvalue(),
            method_used=method
        )

    def normalize_optical(self, arr: np.ndarray) -> np.ndarray:
        out = np.zeros_like(arr, dtype=np.uint8)
        for i in range(arr.shape[-1]):
            band = arr[..., i]
            p2, p98 = np.percentile(band[band > 0], (2, 98)) if np.any(band > 0) else (0, 1)
            norm = np.clip((band - p2) / (p98 - p2 + 1e-8), 0, 1)
            out[..., i] = (norm * 255).astype(np.uint8)
        return out

    def normalize_sar(self, arr: np.ndarray) -> np.ndarray:
        out = np.zeros_like(arr, dtype=np.uint8)
        for i in range(arr.shape[-1]):
            band = arr[..., i].astype(float)
            band[band <= 0] = 1e-6
            db = 10 * np.log10(band)
            p1, p99 = np.percentile(db, (1, 99))
            norm = np.clip((db - p1) / (p99 - p1 + 1e-8), 0, 1)
            out[..., i] = (norm * 255).astype(np.uint8)
        return out

    def resize_to_max_dim(self, arr: np.ndarray, max_dim: int) -> np.ndarray:
        h, w = arr.shape[:2]
        if max(h, w) <= max_dim:
            return arr
            
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(arr, (new_w, new_h), interpolation=cv2.INTER_AREA)
