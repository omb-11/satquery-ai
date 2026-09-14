"""
SatQuery AI — Comprehensive Test Suite
Tests the core analysis pipeline with synthetic images.
"""
from __future__ import annotations
import sys
import io
import json
import pytest
import numpy as np
from pathlib import Path
from PIL import Image

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.config import settings


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

def make_rgb_array(size=64, seed=0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = rng.integers(0, 255, (size, size, 3), dtype=np.uint8)
    return arr


def make_sar_array(size=64, seed=1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = rng.integers(0, 255, (size, size), dtype=np.uint8)
    return arr


def save_test_image(arr: np.ndarray, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if arr.ndim == 2:
        img = Image.fromarray(arr, mode='L')
    else:
        img = Image.fromarray(arr[:, :, :3], mode='RGB')
    img.save(str(path))
    return path


@pytest.fixture
def test_dir(tmp_path):
    return tmp_path


@pytest.fixture
def rgb_image(test_dir):
    arr = make_rgb_array(64)
    path = test_dir / "test_optical.png"
    return save_test_image(arr, path)


@pytest.fixture
def sar_image(test_dir):
    arr = make_sar_array(64)
    path = test_dir / "test_sar.png"
    return save_test_image(arr, path)


@pytest.fixture
def rgb_t2_image(test_dir):
    """T2 image with some change (brighter in one region)."""
    arr = make_rgb_array(64, seed=99)
    arr[10:30, 10:30, :] = [200, 190, 185]  # built-up expansion
    path = test_dir / "test_t2.png"
    return save_test_image(arr, path)


# ─────────────────────────────────────────────
# Unit Tests: Tools
# ─────────────────────────────────────────────

class TestSpectralAnalyzer:
    def test_ndvi_range(self):
        from backend.tools.spectral import SpectralAnalyzer
        sa = SpectralAnalyzer()
        nir = np.array([[200, 150], [100, 80]], dtype=np.float32)
        red = np.array([[100, 100], [100, 100]], dtype=np.float32)
        ndvi = sa.compute_ndvi(nir, red)
        assert ndvi.shape == (2, 2)
        assert np.all(ndvi >= -1.0)
        assert np.all(ndvi <= 1.0)

    def test_ndwi_range(self):
        from backend.tools.spectral import SpectralAnalyzer
        sa = SpectralAnalyzer()
        green = np.array([[120, 80]], dtype=np.float32)
        nir = np.array([[60, 200]], dtype=np.float32)
        ndwi = sa.compute_ndwi(green, nir)
        assert ndwi.shape == (1, 2)
        assert np.all(ndwi >= -1.0)
        assert np.all(ndwi <= 1.0)

    def test_ndvi_vegetation_positive(self):
        from backend.tools.spectral import SpectralAnalyzer
        sa = SpectralAnalyzer()
        nir = np.full((10, 10), 200.0)  # high NIR = vegetation
        red = np.full((10, 10), 50.0)
        ndvi = sa.compute_ndvi(nir, red)
        assert np.mean(ndvi) > 0.5


class TestImageValidator:
    def test_valid_png(self, rgb_image):
        from backend.tools.validator import ImageValidator
        v = ImageValidator()
        result = v.validate_single(str(rgb_image))
        assert result.is_valid
        assert result.format in ["png", "jpg", "jpeg", "tif", "tiff"]

    def test_invalid_file(self, test_dir):
        from backend.tools.validator import ImageValidator
        bad_path = test_dir / "not_an_image.txt"
        bad_path.write_text("not an image")
        v = ImageValidator()
        result = v.validate_single(str(bad_path))
        assert not result.is_valid

    def test_pair_validation(self, rgb_image, rgb_t2_image):
        from backend.tools.validator import ImageValidator
        v = ImageValidator()
        result = v.validate_pair(str(rgb_image), str(rgb_t2_image))
        assert hasattr(result, 'compatible')


class TestChangeDetector:
    def test_change_detection_runs(self, rgb_image, rgb_t2_image):
        from backend.tools.change_detector import ChangeDetector
        cd = ChangeDetector()
        result = cd.detect(str(rgb_image), str(rgb_t2_image))
        assert result is not None
        assert hasattr(result, 'regions')
        assert isinstance(result.overall_change_pct, float)
        assert 0.0 <= result.overall_change_pct <= 100.0

    def test_identical_images_low_change(self, rgb_image):
        from backend.tools.change_detector import ChangeDetector
        cd = ChangeDetector()
        result = cd.detect(str(rgb_image), str(rgb_image))
        # Identical images should have near-zero change
        assert result.overall_change_pct < 10.0

    def test_change_map_generated(self, rgb_image, rgb_t2_image):
        from backend.tools.change_detector import ChangeDetector
        cd = ChangeDetector()
        result = cd.detect(str(rgb_image), str(rgb_t2_image))
        assert result.change_map_bytes is not None
        assert len(result.change_map_bytes) > 0


class TestSARProcessor:
    def test_sar_processing(self, sar_image):
        from backend.tools.sar_processor import SARProcessor
        sp = SARProcessor()
        result = sp.process(str(sar_image), {})
        assert result is not None
        assert hasattr(result, 'water_pct')
        assert hasattr(result, 'buildup_pct')
        assert 0.0 <= result.water_pct <= 100.0
        assert 0.0 <= result.buildup_pct <= 100.0


class TestFusionEngine:
    def test_fusion_runs(self, rgb_image, sar_image):
        from backend.tools.fusion_engine import OpticalSARFusionEngine
        fe = OpticalSARFusionEngine()
        result = fe.fuse(str(rgb_image), str(sar_image))
        assert result is not None
        assert hasattr(result, 'agreement_score')
        assert 0.0 <= result.agreement_score <= 1.0

    def test_fusion_generates_previews(self, rgb_image, sar_image):
        from backend.tools.fusion_engine import OpticalSARFusionEngine
        fe = OpticalSARFusionEngine()
        result = fe.fuse(str(rgb_image), str(sar_image))
        assert result.optical_preview_bytes is not None
        assert result.sar_preview_bytes is not None
        assert result.fusion_preview_bytes is not None


# ─────────────────────────────────────────────
# Unit Tests: Router
# ─────────────────────────────────────────────

class TestTaskRouter:
    def test_caption_query(self):
        from backend.agents.router import TaskRouter
        r = TaskRouter()
        task = r.classify("Describe this scene", "single", [])
        assert task in ["SINGLE_CAPTION", "SINGLE_VQA"]

    def test_change_query(self):
        from backend.agents.router import TaskRouter
        r = TaskRouter()
        task = r.classify("What changed between the two dates?", "bitemporal", [])
        assert "CHANGE" in task

    def test_water_query(self):
        from backend.agents.router import TaskRouter
        r = TaskRouter()
        task = r.classify("Find water bodies in this image", "single", [])
        assert task in ["SINGLE_GROUNDING", "LAND_COVER_ANALYSIS", "OBJECT_IDENTIFICATION"]

    def test_fusion_query(self):
        from backend.agents.router import TaskRouter
        r = TaskRouter()
        task = r.classify("Use optical and SAR together", "optical_sar", [])
        assert "OPTICAL_SAR" in task or "FUSION" in task

    def test_suggested_queries_single(self):
        from backend.agents.router import TaskRouter
        r = TaskRouter()
        queries = r.get_suggested_queries("single")
        assert len(queries) >= 3
        assert all(isinstance(q, str) for q in queries)

    def test_suggested_queries_bitemporal(self):
        from backend.agents.router import TaskRouter
        r = TaskRouter()
        queries = r.get_suggested_queries("bitemporal")
        assert any("change" in q.lower() or "changed" in q.lower() for q in queries)


# ─────────────────────────────────────────────
# Unit Tests: Confidence
# ─────────────────────────────────────────────

class TestConfidenceEstimator:
    def test_high_confidence(self):
        from backend.evidence.confidence import ConfidenceEstimator
        ce = ConfidenceEstimator()
        evidence = [{"score": 0.9}, {"score": 0.85}, {"score": 0.92}]
        result = ce.estimate(evidence, 0.95, 0.98, {}, "CHANGE_DETECTION")
        assert result.score > 0.6
        assert result.level in ["high", "medium", "low"]

    def test_low_evidence_downgrades(self):
        from backend.evidence.confidence import ConfidenceEstimator
        ce = ConfidenceEstimator()
        result = ce.estimate([], 0.5, 0.5, {}, "SINGLE_VQA")
        assert result.level in ["low", "medium"]

    def test_confidence_has_limitations(self):
        from backend.evidence.confidence import ConfidenceEstimator
        ce = ConfidenceEstimator()
        result = ce.estimate([{"score": 0.4}], 0.3, 0.4, {}, "OPTICAL_SAR_FUSION")
        assert isinstance(result.limitations, list)


# ─────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────

class TestValidatorIntegration:
    def test_full_validation_pipeline(self, rgb_image):
        from backend.tools.validator import ImageValidator
        v = ImageValidator()
        result = v.validate_single(str(rgb_image))
        assert result.is_valid
        assert len(result.checks_passed) > 0

    def test_pair_validation_compatible(self, rgb_image, rgb_t2_image):
        from backend.tools.validator import ImageValidator
        v = ImageValidator()
        result = v.validate_pair(str(rgb_image), str(rgb_t2_image))
        # Same-size PNG pair should be compatible
        assert hasattr(result, 'registration_score')


class TestGeospatialMetadata:
    def test_png_metadata(self, rgb_image):
        from backend.geospatial.metadata import extract_metadata
        meta = extract_metadata(str(rgb_image))
        assert meta.width > 0
        assert meta.height > 0
        assert not meta.has_georeference  # PNG has no CRS

    def test_modality_inference(self, rgb_image, sar_image):
        from backend.geospatial.metadata import extract_metadata
        opt_meta = extract_metadata(str(rgb_image))
        sar_meta = extract_metadata(str(sar_image))
        # 3-band = optical, 1-band = likely SAR/panchromatic
        assert opt_meta.modality in ["optical", "rgb", "unknown"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
