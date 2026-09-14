import os
from dataclasses import dataclass
from typing import Optional, List, Tuple
from pathlib import Path
import rasterio
from rasterio.warp import transform_bounds
import logging

logger = logging.getLogger(__name__)

@dataclass
class RasterMetadata:
    crs: Optional[str]
    transform: Optional[list]
    bounds: Optional[Tuple[float, float, float, float]]
    bounds_wgs84: Optional[Tuple[float, float, float, float]]
    width: int
    height: int
    count: int
    dtype: str
    nodata: Optional[float]
    pixel_width_m: Optional[float]
    pixel_height_m: Optional[float]
    file_size_mb: float
    modality: str
    band_names: List[str]
    acquisition_date: Optional[str]
    has_georeference: bool

def extract_metadata(path: str) -> RasterMetadata:
    p = Path(path)
    file_size_mb = p.stat().st_size / (1024 * 1024) if p.exists() else 0.0
    
    try:
        with rasterio.open(str(p)) as src:
            crs_str = src.crs.to_string() if src.crs else None
            transform_list = list(src.transform) if src.transform else None
            bounds = tuple(src.bounds) if src.bounds else None
            
            bounds_wgs84 = None
            if src.crs and bounds:
                try:
                    # rasterio left, bottom, right, top
                    bounds_wgs84 = transform_bounds(src.crs, 'EPSG:4326', *bounds)
                except Exception as e:
                    logger.warning(f"Could not transform bounds for {path}: {e}")
            
            pixel_width_m = None
            pixel_height_m = None
            if src.transform and src.crs:
                # If projected, assuming meters. If geographic, would need conversion (approximate).
                pixel_width_m = abs(src.transform[0])
                pixel_height_m = abs(src.transform[4])
                
            modality = 'unknown'
            # Simple heuristic
            if src.count == 3 or src.count == 4:
                modality = 'optical'
            elif src.count > 4:
                modality = 'multispectral'
            elif src.count == 1:
                if 'dB' in str(src.tags()).lower() or 'sar' in str(src.tags()).lower():
                    modality = 'sar'
            
            band_names = list(src.descriptions) if any(src.descriptions) else [f"Band_{i+1}" for i in range(src.count)]
            tags = src.tags()
            acquisition_date = tags.get('TIFFTAG_DATETIME') or tags.get('ACQUISITION_DATE')
            
            has_geo = src.crs is not None or (src.transform and not src.transform.is_identity)
            
            return RasterMetadata(
                crs=crs_str,
                transform=transform_list,
                bounds=bounds,
                bounds_wgs84=bounds_wgs84,
                width=src.width,
                height=src.height,
                count=src.count,
                dtype=str(src.dtypes[0]) if src.dtypes else 'unknown',
                nodata=src.nodatavals[0] if src.nodatavals else None,
                pixel_width_m=pixel_width_m,
                pixel_height_m=pixel_height_m,
                file_size_mb=file_size_mb,
                modality=modality,
                band_names=band_names,
                acquisition_date=acquisition_date,
                has_georeference=has_geo
            )
            
    except rasterio.errors.RasterioIOError:
        # Possibly PNG/JPEG without spatial data
        from PIL import Image
        try:
            with Image.open(str(p)) as img:
                return RasterMetadata(
                    crs=None, transform=None, bounds=None, bounds_wgs84=None,
                    width=img.width, height=img.height,
                    count=len(img.getbands()),
                    dtype='uint8', nodata=None,
                    pixel_width_m=None, pixel_height_m=None,
                    file_size_mb=file_size_mb,
                    modality='unknown',
                    band_names=list(img.getbands()),
                    acquisition_date=None,
                    has_georeference=False
                )
        except Exception as e:
            logger.error(f"Failed to read image {path}: {e}")
            raise ValueError(f"Could not open file {path} as raster or image.")
