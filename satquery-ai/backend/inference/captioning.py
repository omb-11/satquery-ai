from dataclasses import dataclass
from typing import Dict, Any, Optional
import PIL.Image
from .registry import ModelRegistry

@dataclass
class CaptionResult:
    caption: str
    structured_description: Dict[str, Any]
    confidence: float
    method_used: str

class CaptioningSpecialist:
    def __init__(self, registry: Optional[ModelRegistry] = None):
        if registry is None:
            from .registry import ModelRegistry
            registry = ModelRegistry()
        self.registry = registry

    def run(self, image_path: str, metadata: Dict[str, Any], spectral_results: Optional[Dict[str, Any]] = None) -> CaptionResult:
        try:
            image = PIL.Image.open(image_path).convert('RGB')
        except Exception:
            return CaptionResult("Error loading image", {}, 0.0, "error")

        provider = self.registry.get_provider('captioning')
        raw_caption = provider.caption(image)
        
        structured = {
            'land_cover': 'unknown',
            'objects': [],
            'vegetation': 'unknown',
            'water': 'unknown',
            'built_up': 'unknown',
            'roads': 'unknown',
            'uncertainty': 'high'
        }
        
        confidence = 0.7
        method = "vlm"
        
        if spectral_results:
            method = "vlm+spectral"
            confidence += 0.15
            if spectral_results.get('ndvi', 0) > 0.3:
                structured['vegetation'] = 'present'
            if spectral_results.get('ndwi', 0) > 0.1:
                structured['water'] = 'present'
                
        caption = raw_caption
        if spectral_results:
            caption += ". " + ", ".join([f"{k}: {v:.2f}" for k, v in spectral_results.items() if isinstance(v, float)])
            
        return CaptionResult(
            caption=caption,
            structured_description=structured,
            confidence=confidence,
            method_used=method
        )
