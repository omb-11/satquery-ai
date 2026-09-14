from dataclasses import dataclass
from typing import Optional, Tuple
from pathlib import Path
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import from_bounds
import logging

logger = logging.getLogger(__name__)

@dataclass
class CoRegistrationResult:
    is_compatible: bool
    crs_match: bool
    bounds_overlap_pct: float
    resolution_ratio: float
    registration_score: float
    needs_reprojection: bool
    reprojected_paths: Tuple[Optional[str], Optional[str]]
    error_message: str

def check_pair_compatibility(path1: str, path2: str) -> CoRegistrationResult:
    """Checks CRS, bounds overlap, resolution for two paths."""
    p1, p2 = str(Path(path1)), str(Path(path2))
    
    try:
        with rasterio.open(p1) as src1, rasterio.open(p2) as src2:
            if not src1.crs or not src2.crs:
                return CoRegistrationResult(False, False, 0.0, 0.0, 0.0, False, (None, None), "Missing CRS in one or both files.")
                
            crs_match = src1.crs == src2.crs
            
            # Simple overlap check in native CRS if matching, else we'd need to reproject bounds
            # For simplicity in this check, if CRS doesn't match, we assume they need reprojection and don't calculate exact overlap here.
            needs_reproj = not crs_match
            overlap_pct = 0.0
            
            if crs_match:
                intersection = (
                    max(src1.bounds.left, src2.bounds.left),
                    max(src1.bounds.bottom, src2.bounds.bottom),
                    min(src1.bounds.right, src2.bounds.right),
                    min(src1.bounds.top, src2.bounds.top)
                )
                if intersection[0] < intersection[2] and intersection[1] < intersection[3]:
                    area_int = (intersection[2] - intersection[0]) * (intersection[3] - intersection[1])
                    area_1 = (src1.bounds.right - src1.bounds.left) * (src1.bounds.top - src1.bounds.bottom)
                    area_2 = (src2.bounds.right - src2.bounds.left) * (src2.bounds.top - src2.bounds.bottom)
                    overlap_pct = (area_int / min(area_1, area_2)) * 100
                
            res1 = src1.transform[0]
            res2 = src2.transform[0]
            # avoid div by zero
            res_ratio = (res1 / res2) if res2 != 0 else 0.0
            if res_ratio < 1 and res_ratio > 0:
                res_ratio = 1.0 / res_ratio
                
            is_compat = (overlap_pct > 0 or not crs_match) and (0 < res_ratio < 100)
            
            return CoRegistrationResult(
                is_compatible=is_compat,
                crs_match=crs_match,
                bounds_overlap_pct=overlap_pct,
                resolution_ratio=res_ratio,
                registration_score=1.0 if is_compat else 0.0,
                needs_reprojection=needs_reproj,
                reprojected_paths=(None, None),
                error_message="" if is_compat else "Incompatible extents or resolutions."
            )
    except Exception as e:
        return CoRegistrationResult(False, False, 0.0, 0.0, 0.0, False, (None, None), str(e))

def reproject_to_match(source_path: str, target_path: str, output_path: str) -> str:
    """Reprojects source to match target CRS/grid."""
    s_path, t_path, o_path = str(Path(source_path)), str(Path(target_path)), str(Path(output_path))
    
    with rasterio.open(t_path) as dst_src:
        dst_crs = dst_src.crs
        dst_transform = dst_src.transform
        dst_width = dst_src.width
        dst_height = dst_src.height
        
    with rasterio.open(s_path) as src:
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': dst_transform,
            'width': dst_width,
            'height': dst_height
        })
        
        with rasterio.open(o_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest
                )
                
    return o_path

def crop_to_intersection(path1: str, path2: str, out1: str, out2: str) -> tuple[str, str]:
    """Crops both to overlapping extent."""
    p1, p2 = str(Path(path1)), str(Path(path2))
    o1, o2 = str(Path(out1)), str(Path(out2))
    
    with rasterio.open(p1) as src1, rasterio.open(p2) as src2:
        if src1.crs != src2.crs:
            raise ValueError("CRS must match to crop to intersection.")
            
        intersection = (
            max(src1.bounds.left, src2.bounds.left),
            max(src1.bounds.bottom, src2.bounds.bottom),
            min(src1.bounds.right, src2.bounds.right),
            min(src1.bounds.top, src2.bounds.top)
        )
        
        if intersection[0] >= intersection[2] or intersection[1] >= intersection[3]:
            raise ValueError("No intersection between bounds.")
            
        def crop(src, out_path):
            window = from_bounds(*intersection, transform=src.transform)
            window = window.round_offsets().round_lengths()
            
            kwargs = src.meta.copy()
            kwargs.update({
                'height': window.height,
                'width': window.width,
                'transform': src.window_transform(window)
            })
            
            with rasterio.open(out_path, 'w', **kwargs) as dst:
                dst.write(src.read(window=window))
                
            return out_path
            
        crop(src1, o1)
        crop(src2, o2)
        
    return (o1, o2)
