import os
import rasterio
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class ValidationResult:
    is_valid: bool
    format: str
    modality: str
    has_crs: bool
    dimensions: Tuple[int, int]
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

@dataclass
class PairValidationResult(ValidationResult):
    compatible: bool = False
    crs_match: bool = False
    bounds_overlap_pct: float = 0.0
    resolution_compatible: bool = False
    registration_score: float = 0.0
    recommendation: str = ""

class ImageValidator:
    SUPPORTED_FORMATS = ['.tif', '.tiff', '.geotiff', '.png', '.jpg', '.jpeg']
    
    def validate_single(self, path: str) -> ValidationResult:
        res = ValidationResult(is_valid=False, format="", modality="optical", has_crs=False, dimensions=(0,0))
        ext = os.path.splitext(path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            res.checks_failed.append(f"Format {ext} not supported")
            res.error = "Unsupported format"
            return res
            
        res.format = ext.lstrip('.')
        res.checks_passed.append("✓ Format supported")
        
        name_lower = os.path.basename(path).lower()
        if any(kw in name_lower for kw in ['sar', 's1', 'sentinel1']):
            res.modality = "SAR"
            
        try:
            with rasterio.open(path) as src:
                res.dimensions = (src.width, src.height)
                res.checks_passed.append("✓ File is readable")
                if src.crs:
                    res.has_crs = True
                    res.checks_passed.append("✓ CRS present")
                else:
                    res.warnings.append("No CRS found")
                
                # Check for modality based on band count if optical
                if res.modality == "optical" and src.count == 1:
                    res.modality = "SAR (inferred from 1 band, might be grayscale)"
                
                res.is_valid = True
        except Exception as e:
            res.checks_failed.append("File not readable as raster")
            res.error = str(e)
            
        return res

    def validate_pair(self, path1: str, path2: str, pair_type: str = 'bitemporal') -> PairValidationResult:
        v1 = self.validate_single(path1)
        v2 = self.validate_single(path2)
        
        res = PairValidationResult(
            is_valid=v1.is_valid and v2.is_valid,
            format=v1.format,
            modality=f"{v1.modality}-{v2.modality}",
            has_crs=v1.has_crs and v2.has_crs,
            dimensions=v1.dimensions,
            checks_passed=v1.checks_passed + [c for c in v2.checks_passed if c not in v1.checks_passed],
            checks_failed=v1.checks_failed + [c for c in v2.checks_failed if c not in v1.checks_failed],
            warnings=v1.warnings + [c for c in v2.warnings if c not in v1.warnings]
        )
        
        if not res.is_valid:
            res.error = "One or both images are invalid."
            return res
            
        res.compatible = True
        
        if v1.has_crs and v2.has_crs:
            with rasterio.open(path1) as s1, rasterio.open(path2) as s2:
                if s1.crs == s2.crs:
                    res.crs_match = True
                    res.checks_passed.append("✓ CRS matches")
                else:
                    res.checks_failed.append("CRS mismatch")
                    res.compatible = False
                    
                # simplistic overlap bounds for demo
                res.bounds_overlap_pct = 100.0 if s1.bounds == s2.bounds else 50.0
                
                if s1.res == s2.res:
                    res.resolution_compatible = True
                    res.checks_passed.append("✓ Resolution matches")
                else:
                    res.warnings.append("Resolution mismatch")
                    
        if res.compatible:
            res.recommendation = "Ready for processing"
        else:
            res.recommendation = "Preprocessing/Reprojection required"
            
        return res
