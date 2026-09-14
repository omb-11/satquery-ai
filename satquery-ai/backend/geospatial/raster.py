import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window
import io
from PIL import Image
from pathlib import Path

def normalize_band(arr: np.ndarray, pct_low: float = 2, pct_high: float = 98) -> np.ndarray:
    """Percentile stretch to 0-255."""
    arr = arr.astype(np.float32)
    valid_mask = np.isfinite(arr)
    if not np.any(valid_mask):
        return np.zeros_like(arr, dtype=np.uint8)
        
    p_low = np.percentile(arr[valid_mask], pct_low)
    p_high = np.percentile(arr[valid_mask], pct_high)
    
    if p_high == p_low:
        stretched = np.zeros_like(arr)
    else:
        stretched = np.clip((arr - p_low) / (p_high - p_low), 0, 1) * 255
        
    return stretched.astype(np.uint8)

def _get_scale_factors(src, max_dim):
    if max(src.height, src.width) <= max_dim:
        return 1.0, src.height, src.width
    scale = max_dim / max(src.height, src.width)
    return scale, int(src.height * scale), int(src.width * scale)

def read_as_rgb(path: str, max_dim: int = 1024) -> np.ndarray:
    path = str(Path(path))
    with rasterio.open(path) as src:
        scale, out_h, out_w = _get_scale_factors(src, max_dim)
        
        # Determine RGB bands
        if src.count >= 3:
            bands = (1, 2, 3)
        else:
            bands = (1, 1, 1)
            
        data = src.read(
            bands,
            out_shape=(3, out_h, out_w),
            resampling=Resampling.bilinear
        )
        
        rgb = np.zeros((out_h, out_w, 3), dtype=np.uint8)
        for i in range(3):
            rgb[:,:,i] = normalize_band(data[i])
            
        return rgb

def read_band(path: str, band_idx: int = 1, max_dim: int = 1024) -> np.ndarray:
    path = str(Path(path))
    with rasterio.open(path) as src:
        scale, out_h, out_w = _get_scale_factors(src, max_dim)
        data = src.read(
            band_idx,
            out_shape=(out_h, out_w),
            resampling=Resampling.bilinear
        )
        return data

def read_windowed(path: str, window: Window = None, max_dim: int = 1024) -> tuple[np.ndarray, dict]:
    path = str(Path(path))
    with rasterio.open(path) as src:
        if window is None:
            window = Window(0, 0, src.width, src.height)
            
        w_height = window.height
        w_width = window.width
        
        scale = 1.0
        if max(w_height, w_width) > max_dim:
            scale = max_dim / max(w_height, w_width)
            
        out_h = int(w_height * scale)
        out_w = int(w_width * scale)
        
        data = src.read(
            window=window,
            out_shape=(src.count, out_h, out_w),
            resampling=Resampling.bilinear
        )
        
        meta = src.meta.copy()
        meta.update({
            "height": out_h,
            "width": out_w,
            "transform": src.window_transform(window) * rasterio.Affine.scale(1/scale)
        })
        return data, meta

def generate_preview(path: str, max_dim: int = 1024) -> bytes:
    rgb_arr = read_as_rgb(path, max_dim)
    img = Image.fromarray(rgb_arr)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
