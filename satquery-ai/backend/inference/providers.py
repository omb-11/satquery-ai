from abc import ABC, abstractmethod
import PIL.Image
from loguru import logger

class VisionLanguageProvider(ABC):
    @abstractmethod
    def caption(self, image: PIL.Image.Image) -> str: ...
    @abstractmethod
    def vqa(self, image: PIL.Image.Image, question: str) -> str: ...
    @abstractmethod
    def health_check(self) -> dict: ...

class BLIPProvider(VisionLanguageProvider):
    def __init__(self):
        self.processor = None
        self.model = None
        self.vqa_model = None
        self.is_loaded = False

    def _load(self):
        if self.is_loaded: return
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            try:
                self.vqa_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
            except Exception as e:
                logger.warning(f"Could not load BLIP VQA: {e}")
            self.is_loaded = True
        except ImportError:
            logger.error("transformers library not found.")
            raise
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

    def caption(self, image: PIL.Image.Image) -> str:
        self._load()
        if not self.processor or not self.model: return ""
        inputs = self.processor(image, return_tensors="pt")
        out = self.model.generate(**inputs)
        return self.processor.decode(out[0], skip_special_tokens=True)

    def vqa(self, image: PIL.Image.Image, question: str) -> str:
        self._load()
        if not self.processor: return ""
        if self.vqa_model:
            inputs = self.processor(image, question, return_tensors="pt")
            out = self.vqa_model.generate(**inputs)
            return self.processor.decode(out[0], skip_special_tokens=True)
        else:
            inputs = self.processor(image, text=f"Question: {question} Answer:", return_tensors="pt")
            out = self.model.generate(**inputs)
            return self.processor.decode(out[0], skip_special_tokens=True)

    def health_check(self) -> dict:
        return {"status": "healthy" if self.is_loaded else "unloaded"}

class MockProvider(VisionLanguageProvider):
    def caption(self, image: PIL.Image.Image) -> str:
        try:
            import numpy as np
            arr = np.array(image)
            return f"[MOCK/FALLBACK] Image with mean brightness {np.mean(arr):.2f}."
        except:
            return "[MOCK/FALLBACK] A remote sensing image."

    def vqa(self, image: PIL.Image.Image, question: str) -> str:
        return f"[MOCK/FALLBACK] Answer for '{question}' based on image stats."

    def health_check(self) -> dict:
        return {"status": "healthy", "model_type": "Mock"}
