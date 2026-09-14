import numpy as np
import rasterio
from dataclasses import dataclass, field
from typing import Dict, Any, List
from io import BytesIO
from PIL import Image

@dataclass
class SpectralResult:
    available_indices: List[str]
    ndvi_stats: Dict[str, float] = field(default_factory=dict)
    ndwi_stats: Dict[str, float] = field(default_factory=dict)
    ndbi_stats: Dict[str, float] = field(default_factory=dict)
    water_mask: np.ndarray = None
    vegetation_mask: np.ndarray = None
    buildup_mask: np.ndarray = None
    band_mapping_used: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

class SpectralAnalyzer:
    def compute_ndvi(self, nir_band: np.ndarray, red_band: np.ndarray) -> np.ndarray:
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band + red_band)
            ndvi = np.nan_to_num(ndvi, nan=0.0)
            return np.clip(ndvi, -1, 1)

    def compute_ndwi(self, green_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        with np.errstate(divide='ignore', invalid='ignore'):
            ndwi = (green_band.astype(float) - nir_band.astype(float)) / (green_band + nir_band)
            ndwi = np.nan_to_num(ndwi, nan=0.0)
            return np.clip(ndwi, -1, 1)

    def compute_ndbi(self, swir_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        with np.errstate(divide='ignore', invalid='ignore'):
            ndbi = (swir_band.astype(float) - nir_band.astype(float)) / (swir_band + nir_band)
            ndbi = np.nan_to_num(ndbi, nan=0.0)
            return np.clip(ndbi, -1, 1)

    def infer_band_mapping(self, metadata: Dict[str, Any]) -> Dict[str, int]:
        count = metadata.get('count', 0)
        mapping = {}
        if count == 3:
            mapping = {'R': 1, 'G': 2, 'B': 3}
        elif count == 4:
            mapping = {'R': 1, 'G': 2, 'B': 3, 'NIR': 4}
        elif count >= 12:
            mapping = {'B': 2, 'G': 3, 'R': 4, 'NIR': 8, 'SWIR': 11}
        return mapping

    def analyze_raster(self, path: str, metadata: Dict[str, Any] = None) -> SpectralResult:
        with rasterio.open(path) as src:
            if metadata is None:
                metadata = src.meta
            mapping = self.infer_band_mapping(metadata)
            
            res = SpectralResult(available_indices=[], band_mapping_used=mapping)
            
            if 'NIR' in mapping and 'R' in mapping:
                nir = src.read(mapping['NIR'])
                red = src.read(mapping['R'])
                ndvi = self.compute_ndvi(nir, red)
                res.available_indices.append('NDVI')
                res.ndvi_stats = {'mean': float(ndvi.mean()), 'max': float(ndvi.max())}
                res.vegetation_mask = (ndvi > 0.3).astype(np.uint8)
                
            if 'G' in mapping and 'NIR' in mapping:
                green = src.read(mapping['G'])
                nir = src.read(mapping['NIR'])
                ndwi = self.compute_ndwi(green, nir)
                res.available_indices.append('NDWI')
                res.ndwi_stats = {'mean': float(ndwi.mean()), 'max': float(ndwi.max())}
                res.water_mask = (ndwi > 0.1).astype(np.uint8)
                
            if 'SWIR' in mapping and 'NIR' in mapping:
                swir = src.read(mapping['SWIR'])
                nir = src.read(mapping['NIR'])
                ndbi = self.compute_ndbi(swir, nir)
                res.available_indices.append('NDBI')
                res.ndbi_stats = {'mean': float(ndbi.mean()), 'max': float(ndbi.max())}
                res.buildup_mask = (ndbi > 0.0).astype(np.uint8)
                
            if not res.available_indices:
                res.warnings.append("Could not compute any indices with available bands.")
                
            return res

    def visualize_index(self, index_arr: np.ndarray, colormap: str = 'RdYlGn') -> bytes:
        import matplotlib.pyplot as plt
        norm = plt.Normalize(vmin=-1, vmax=1)
        cmap = plt.get_cmap(colormap)
        colored = cmap(norm(index_arr))
        colored = (colored[:, :, :3] * 255).astype(np.uint8)
        img = Image.fromarray(colored)
        bio = BytesIO()
        img.save(bio, format='PNG')
        return bio.getvalue()
