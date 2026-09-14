"""
SatQuery AI — VQA Specialist
Remote-sensing aware Visual Question Answering.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional
from loguru import logger


@dataclass
class VQAResult:
    answer: str
    confidence: float
    method_used: str
    model_name: str
    raw_output: str
    processing_time_ms: float

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "method_used": self.method_used,
            "model_name": self.model_name,
            "processing_time_ms": self.processing_time_ms,
        }


class VQASpecialist:
    """
    VQA specialist using BLIP or MockProvider with graceful fallback.
    Augments VLM answers with spectral evidence when available.
    """

    def __init__(self, registry=None):
        """registry is optional — will create ModelRegistry if not provided."""
        self._registry = registry

    @property
    def registry(self):
        if self._registry is None:
            from backend.inference.registry import ModelRegistry
            self._registry = ModelRegistry()
        return self._registry

    def run(self, image_path: str, question: str, metadata: Dict[str, Any],
            spectral_results: Optional[Dict] = None) -> VQAResult:
        """Run VQA on an image with a question."""
        start = time.time()

        try:
            from PIL import Image
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            logger.warning(f"Could not open image {image_path}: {e}")
            elapsed = (time.time() - start) * 1000
            return VQAResult(
                answer=f"Could not process image: {e}",
                confidence=0.0,
                method_used="error",
                model_name="none",
                raw_output=str(e),
                processing_time_ms=elapsed,
            )

        try:
            provider = self.registry.get_provider("remote_sensing_vqa")
            raw_answer = provider.vqa(image, question)
            model_name = getattr(provider, "model_name", type(provider).__name__)
        except Exception as e:
            logger.warning(f"VQA provider error: {e}; using image-statistics fallback")
            raw_answer = self._statistics_answer(image, question, metadata, spectral_results)
            model_name = "ImageStatisticsFallback"

        # Augment answer with spectral evidence if available
        final_answer = self._augment_with_spectral(raw_answer, question, spectral_results)

        elapsed = (time.time() - start) * 1000
        return VQAResult(
            answer=final_answer,
            confidence=0.65,
            method_used=model_name,
            model_name=model_name,
            raw_output=raw_answer,
            processing_time_ms=elapsed,
        )

    def _augment_with_spectral(self, answer: str, question: str,
                                spectral_results: Optional[Dict]) -> str:
        """Adds spectral evidence to VQA answer when relevant."""
        if not spectral_results:
            return answer

        q_lower = question.lower()
        augmentations = []

        ndvi_stats = spectral_results.get("ndvi_stats") or {}
        if "vegetation" in q_lower or "green" in q_lower or "forest" in q_lower:
            mean_ndvi = ndvi_stats.get("mean", None)
            if mean_ndvi is not None:
                augmentations.append(
                    f"Spectral analysis: Mean NDVI = {mean_ndvi:.2f} "
                    f"({'vegetation present' if mean_ndvi > 0.3 else 'sparse vegetation'})."
                )

        ndwi_stats = spectral_results.get("ndwi_stats") or {}
        if "water" in q_lower or "river" in q_lower or "lake" in q_lower:
            mean_ndwi = ndwi_stats.get("mean", None)
            if mean_ndwi is not None:
                augmentations.append(
                    f"Spectral analysis: Mean NDWI = {mean_ndwi:.2f} "
                    f"({'water likely present' if mean_ndwi > 0.0 else 'low water signal'})."
                )

        if augmentations:
            return answer + "\n\n[Spectral verification] " + " ".join(augmentations)
        return answer

    def _statistics_answer(self, image, question: str, metadata: dict,
                           spectral_results: Optional[dict]) -> str:
        """
        Evidence-based answer using image statistics only.
        Never invents facts. States when evidence is insufficient.
        """
        import numpy as np
        arr = np.array(image)
        mean_r, mean_g, mean_b = arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean()
        brightness = (mean_r + mean_g + mean_b) / 3

        q_lower = question.lower()

        if "water" in q_lower or "river" in q_lower or "lake" in q_lower:
            if mean_b > mean_r * 1.1 and brightness < 100:
                return "Based on spectral characteristics (blue-dominant, low brightness), water is likely present in the image."
            return "Based on image statistics, no strong water signature detected. A higher-resolution multispectral image with NIR bands would improve water detection accuracy."

        if "vegetation" in q_lower or "green" in q_lower:
            if mean_g > mean_r * 1.05:
                return "Green channel dominance suggests vegetation presence."
            return "Image statistics do not show strong vegetation signature."

        if "urban" in q_lower or "built" in q_lower or "building" in q_lower:
            if brightness > 130 and abs(mean_r - mean_g) < 15:
                return "High brightness and uniform RGB channels suggest potential built-up/urban surfaces."
            return "Insufficient spectral evidence to determine urban extent without multispectral bands."

        if "describe" in q_lower or "what" in q_lower:
            if brightness > 150:
                dom = "bright (possibly built-up or bare soil)"
            elif mean_g > mean_r and mean_g > mean_b:
                dom = "vegetation-dominant (green)"
            elif mean_b > mean_r:
                dom = "water-like or dark"
            else:
                dom = "mixed land cover"
            return (
                f"The image shows {dom} land cover based on pixel statistics. "
                f"Mean brightness: {brightness:.0f}/255. "
                f"RGB channels: R={mean_r:.0f}, G={mean_g:.0f}, B={mean_b:.0f}. "
                "For detailed semantic analysis, a remote-sensing VLM model is recommended."
            )

        return (
            "The image statistics provide limited information for this query. "
            "A pretrained remote-sensing VLM (e.g., BLIP or GeoChat) would provide richer answers. "
            f"Image brightness: {brightness:.0f}/255."
        )
