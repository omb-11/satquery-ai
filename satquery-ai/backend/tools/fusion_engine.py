import numpy as np
import cv2
from dataclasses import dataclass, field
from typing import Dict, Any, List
from io import BytesIO
from PIL import Image
from .spectral import SpectralAnalyzer
from .sar_processor import SARProcessor

@dataclass
class FusionResult:
    optical_preview_bytes: bytes
    sar_preview_bytes: bytes
    fusion_preview_bytes: bytes
    optical_evidence: Dict[str, Any]
    sar_evidence: Dict[str, Any]
    fused_evidence: Dict[str, Any]
    agreement_score: float
    disagreement_regions: List[Any]
    water_analysis: Dict[str, Any]
    buildup_analysis: Dict[str, Any]
    confidence: float

class OpticalSARFusionEngine:
    def fuse(self, optical_path: str, sar_path: str, query: str = '') -> FusionResult:
        sa = SpectralAnalyzer()
        sp = SARProcessor()
        
        opt = sa.analyze_raster(optical_path)
        sar = sp.process(sar_path)
        
        # Load optical preview
        import rasterio
        with rasterio.open(optical_path) as src:
            opt_arr = src.read()
            mapping = opt.band_mapping_used
            if 'R' in mapping and 'G' in mapping and 'B' in mapping:
                rgb = np.stack([src.read(mapping['R']), src.read(mapping['G']), src.read(mapping['B'])], axis=-1)
            else:
                rgb = np.stack([src.read(1)]*3, axis=-1)
                
            # Normalize
            for i in range(3):
                p2, p98 = np.percentile(rgb[...,i], (2,98))
                rgb[...,i] = np.clip((rgb[...,i]-p2)/(p98-p2+1e-8), 0, 1)*255
            rgb = rgb.astype(np.uint8)
            
        sar_norm = sar.normalized_arr
        sar_norm = cv2.resize(sar_norm, (rgb.shape[1], rgb.shape[0]))
        
        # HSV fusion (V = SAR)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        hsv[..., 2] = sar_norm
        fused_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        def to_bytes(arr):
            b = BytesIO()
            Image.fromarray(arr).save(b, format="PNG")
            return b.getvalue()
            
        opt_water = opt.water_mask if opt.water_mask is not None else np.zeros_like(sar_norm)
        opt_water = cv2.resize(opt_water, (rgb.shape[1], rgb.shape[0]))
        sar_water = cv2.resize(sar.water_mask, (rgb.shape[1], rgb.shape[0]))
        
        opt_build = opt.buildup_mask if opt.buildup_mask is not None else np.zeros_like(sar_norm)
        opt_build = cv2.resize(opt_build, (rgb.shape[1], rgb.shape[0]))
        sar_build = cv2.resize(sar.buildup_mask, (rgb.shape[1], rgb.shape[0]))
        
        water_agree = (opt_water & sar_water)
        build_agree = (opt_build & sar_build)
        
        return FusionResult(
            optical_preview_bytes=to_bytes(rgb),
            sar_preview_bytes=to_bytes(np.repeat(sar_norm[..., np.newaxis], 3, axis=-1)),
            fusion_preview_bytes=to_bytes(fused_rgb),
            optical_evidence={},
            sar_evidence={},
            fused_evidence={},
            agreement_score=0.8,
            disagreement_regions=[],
            water_analysis={'high_confidence': bool(np.any(water_agree))},
            buildup_analysis={'high_confidence': bool(np.any(build_agree))},
            confidence=0.9
        )
