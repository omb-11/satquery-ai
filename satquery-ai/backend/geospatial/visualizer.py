import numpy as np
import rasterio
from rasterio.enums import Resampling
import io
from PIL import Image
from pathlib import Path

def array_to_png_bytes(arr: np.ndarray) -> bytes:
    """Convert numpy array to PNG bytes."""
    if len(arr.shape) == 3 and arr.shape[0] in [1, 3, 4]:
        # C, H, W to H, W, C
        arr = np.transpose(arr, (1, 2, 0))
    if len(arr.shape) == 3 and arr.shape[2] == 1:
        arr = arr[:, :, 0]
        
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def normalize_stretch(arr: np.ndarray, pct_low=2.0, pct_high=98.0) -> np.ndarray:
    arr = arr.astype(np.float32)
    valid = np.isfinite(arr)
    if not np.any(valid):
        return np.zeros_like(arr, dtype=np.uint8)
    p_low, p_high = np.percentile(arr[valid], (pct_low, pct_high))
    if p_low == p_high:
        return np.zeros_like(arr, dtype=np.uint8)
    stretched = np.clip((arr - p_low) / (p_high - p_low), 0, 1) * 255
    return stretched.astype(np.uint8)

def _get_scaled_shape(src, max_dim):
    scale = min(1.0, max_dim / max(src.height, src.width))
    return int(src.height * scale), int(src.width * scale)

def generate_rgb_preview(path: str, max_dim: int = 1024) -> bytes:
    """RGB preview as PNG bytes."""
    path = str(Path(path))
    with rasterio.open(path) as src:
        out_h, out_w = _get_scaled_shape(src, max_dim)
        bands = (1, 2, 3) if src.count >= 3 else (1, 1, 1)
        data = src.read(bands, out_shape=(len(bands), out_h, out_w), resampling=Resampling.bilinear)
        
        rgb = np.zeros((out_h, out_w, 3), dtype=np.uint8)
        for i in range(3):
            rgb[:,:,i] = normalize_stretch(data[min(i, len(bands)-1)])
            
        return array_to_png_bytes(rgb)

def generate_false_color(path: str, bands: list[int], max_dim: int = 1024) -> bytes:
    """False color composite."""
    path = str(Path(path))
    with rasterio.open(path) as src:
        out_h, out_w = _get_scaled_shape(src, max_dim)
        read_bands = [min(b, src.count) for b in bands[:3]]
        data = src.read(read_bands, out_shape=(len(read_bands), out_h, out_w), resampling=Resampling.bilinear)
        
        rgb = np.zeros((out_h, out_w, 3), dtype=np.uint8)
        for i in range(min(3, len(read_bands))):
            rgb[:,:,i] = normalize_stretch(data[i])
            
        return array_to_png_bytes(rgb)

def generate_sar_visualization(path: str, max_dim: int = 1024) -> bytes:
    """SAR grayscale with dB normalization."""
    path = str(Path(path))
    with rasterio.open(path) as src:
        out_h, out_w = _get_scaled_shape(src, max_dim)
        data = src.read(1, out_shape=(out_h, out_w), resampling=Resampling.bilinear)
        
        # Apply dB normalization heuristic if values are linear
        # Assuming linear amplitude or intensity if positive and large variance
        data = data.astype(np.float32)
        valid = data > 0
        if np.any(valid):
            db = np.zeros_like(data)
            db[valid] = 10 * np.log10(data[valid])
            gray = normalize_stretch(db, 2, 98)
        else:
            gray = normalize_stretch(data)
            
        return array_to_png_bytes(gray)

def generate_fusion_view(optical_path: str, sar_path: str, max_dim: int = 1024) -> bytes:
    """Optical+SAR composite."""
    opt_p = str(Path(optical_path))
    sar_p = str(Path(sar_path))
    
    with rasterio.open(opt_p) as src_opt:
        out_h, out_w = _get_scaled_shape(src_opt, max_dim)
        bands = (1, 2, 3) if src_opt.count >= 3 else (1, 1, 1)
        opt_data = src_opt.read(bands, out_shape=(3, out_h, out_w), resampling=Resampling.bilinear)
        
    with rasterio.open(sar_p) as src_sar:
        # Assuming already aligned or reprojected!
        sar_data = src_sar.read(1, out_shape=(out_h, out_w), resampling=Resampling.bilinear)
        
    opt_rgb = np.zeros((out_h, out_w, 3), dtype=np.uint8)
    for i in range(3):
        opt_rgb[:,:,i] = normalize_stretch(opt_data[i])
        
    sar_gray = normalize_stretch(sar_data)
    
    # Simple blend: 70% optical, 30% SAR
    fusion = (opt_rgb * 0.7 + np.stack([sar_gray]*3, axis=-1) * 0.3).astype(np.uint8)
    return array_to_png_bytes(fusion)
