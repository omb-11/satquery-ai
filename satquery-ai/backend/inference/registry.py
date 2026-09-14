from typing import List, Dict, Any
from .providers import VisionLanguageProvider, BLIPProvider, MockProvider
from loguru import logger

SPECIALISTS = {
    'remote_sensing_vqa': {'name': 'BLIP VQA', 'version': '1.0', 'task_types': ['vqa'], 'modalities': ['optical'], 'status': 'not_loaded', 'device': 'cpu', 'checkpoint': 'Salesforce/blip-vqa-base', 'fallback': 'MockProvider', 'description': 'General purpose VQA for optical imagery'},
    'captioning': {'name': 'BLIP Captioning', 'version': '1.0', 'task_types': ['captioning'], 'modalities': ['optical'], 'status': 'not_loaded', 'device': 'cpu', 'checkpoint': 'Salesforce/blip-image-captioning-base', 'fallback': 'MockProvider', 'description': 'Generates natural language descriptions of images'},
    'grounding': {'name': 'Grounding DINO', 'version': '1.0', 'task_types': ['object_detection', 'grounding'], 'modalities': ['optical'], 'status': 'unavailable', 'device': 'cpu', 'checkpoint': 'groundingdino-base', 'fallback': 'None', 'description': 'Open vocabulary object detection'},
    'change_detection': {'name': 'Siamese ResNet', 'version': '1.0', 'task_types': ['change_detection'], 'modalities': ['optical'], 'status': 'unavailable', 'device': 'cpu', 'checkpoint': 'local/siam_resnet', 'fallback': 'None', 'description': 'Detects changes between image pairs'},
    'sar_processor': {'name': 'SAR Basics', 'version': '1.0', 'task_types': ['sar_analysis'], 'modalities': ['sar'], 'status': 'unavailable', 'device': 'cpu', 'checkpoint': 'none', 'fallback': 'None', 'description': 'Basic SAR processing'},
    'optical_sar_fusion': {'name': 'OpSAR Fusion', 'version': '1.0', 'task_types': ['fusion'], 'modalities': ['optical', 'sar'], 'status': 'unavailable', 'device': 'cpu', 'checkpoint': 'none', 'fallback': 'None', 'description': 'Fuses optical and SAR features'},
    'geospatial_preprocessor': {'name': 'GeoPreproc', 'version': '1.0', 'task_types': ['preprocessing'], 'modalities': ['optical', 'sar'], 'status': 'loaded', 'device': 'cpu', 'checkpoint': 'none', 'fallback': 'None', 'description': 'Handles CRS alignment and co-registration'},
    'report_generator': {'name': 'LLM Reporter', 'version': '1.0', 'task_types': ['synthesis'], 'modalities': ['text'], 'status': 'loaded', 'device': 'api', 'checkpoint': 'gpt-4', 'fallback': 'None', 'description': 'Generates final reports'},
    'bigearthnet_adapter': {'name': 'BigEarthNet Cls', 'version': '1.0', 'task_types': ['classification'], 'modalities': ['optical'], 'status': 'not_installed', 'device': 'cpu', 'checkpoint': 'bigearthnet-resnet50', 'fallback': 'None', 'description': 'Multi-label classification'}
}

class ModelRegistry:
    def __init__(self):
        self.providers: Dict[str, VisionLanguageProvider] = {}

    def get_specialist(self, name: str) -> Dict[str, Any]:
        return SPECIALISTS.get(name, {})

    def list_all(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in SPECIALISTS.items()]

    def health_check_all(self) -> Dict[str, Any]:
        return {k: v['status'] for k, v in SPECIALISTS.items()}

    def get_provider(self, task_type: str) -> VisionLanguageProvider:
        if task_type in self.providers:
            return self.providers[task_type]
        try:
            import transformers
            provider = BLIPProvider()
        except ImportError:
            provider = MockProvider()
            logger.warning("Using MockProvider as transformers is missing")
        self.providers[task_type] = provider
        return provider

    def get_status_table(self) -> List[Dict[str, Any]]:
        return [{'id': k, **v} for k, v in SPECIALISTS.items()]
