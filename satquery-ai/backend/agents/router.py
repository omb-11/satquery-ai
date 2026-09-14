from typing import List, Dict, Any

class TaskRouter:
    def classify(self, query: str, input_mode: str, metadata: List[Dict[str, Any]]) -> str:
        q = query.lower()
        if input_mode == 'bitemporal':
            if any(w in q for w in ['changed', 'change', 'difference', 'before', 'after', 'between']):
                return 'CHANGE_VQA' if any(w in q for w in ['what', 'why', 'how']) else 'CHANGE_DETECTION'
            elif any(w in q for w in ['describe', 'caption', 'what is', 'scene']):
                return 'CHANGE_DESCRIPTION'
            return 'CHANGE_VQA'
        elif input_mode == 'optical_sar':
            if any(w in q for w in ['sar', 'optical', 'both', 'together', 'combine', 'fusion']):
                return 'OPTICAL_SAR_FUSION'
            return 'OPTICAL_SAR_VQA'
        
        # Single input mode
        if any(w in q for w in ['highlight', 'find', 'locate', 'where', 'show me']):
            return 'SINGLE_GROUNDING'
        if any(w in q for w in ['water', 'river', 'lake', 'ocean', 'flood']):
            return 'LAND_COVER_ANALYSIS'
        if any(w in q for w in ['building', 'built', 'urban', 'structure']):
            return 'OBJECT_IDENTIFICATION'
        if any(w in q for w in ['vegetation', 'ndvi', 'forest', 'crop', 'plant']):
            return 'LAND_COVER_ANALYSIS'
        if any(w in q for w in ['describe', 'caption', 'what is', 'scene']):
            return 'SINGLE_CAPTION'
            
        if any(w in q for w in ['what', 'how', 'why', 'is', 'are']):
            return 'SINGLE_VQA'
            
        return 'UNSUPPORTED'

    def get_required_tools(self, task_type: str, input_mode: str) -> List[str]:
        tools = ['load_image', 'extract_metadata']
        if task_type in ['SINGLE_VQA', 'CHANGE_VQA', 'OPTICAL_SAR_VQA']:
            tools.extend(['vqa_model'])
        if task_type in ['SINGLE_GROUNDING', 'OBJECT_IDENTIFICATION']:
            tools.extend(['grounding_model', 'crop_image'])
        if task_type in ['CHANGE_DETECTION']:
            tools.extend(['change_detection_model', 'compute_diff'])
        if task_type == 'LAND_COVER_ANALYSIS':
            tools.extend(['segmentation_model', 'compute_indices'])
        if task_type == 'OPTICAL_SAR_FUSION':
            tools.extend(['coregistration', 'fusion_model'])
        return tools

    def get_suggested_queries(self, input_mode: str) -> List[str]:
        if input_mode == 'bitemporal':
            return ["What changed between these images?", "Describe the difference in urban areas.", "Are there new buildings?"]
        elif input_mode == 'optical_sar':
            return ["Fuse the optical and SAR images.", "Identify flooded areas using SAR.", "What can be seen in SAR but not optical?"]
        else:
            return ["Describe the scene.", "Where are the buildings?", "Is there a river in this image?"]
