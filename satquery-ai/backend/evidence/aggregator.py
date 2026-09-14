from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class EvidenceItem:
    source: str
    claim: str
    region: Any
    score: float
    category: str

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "claim": self.claim,
            "region": self.region,
            "score": self.score,
            "category": self.category
        }

class EvidenceAggregator:
    def aggregate(self, tool_results: Dict[str, Any], task_type: str, query: str) -> List[EvidenceItem]:
        evidence = []
        
        if 'vqa' in tool_results:
            res = tool_results['vqa']
            if isinstance(res, dict):
                evidence.append(EvidenceItem('vqa', res.get('answer', ''), 'global', res.get('confidence', 0.75), 'visual'))
            
        if 'spectral' in tool_results and isinstance(tool_results['spectral'], dict):
            for k, v in tool_results['spectral'].items():
                if v is not None and v != [] and v != {}:
                    evidence.append(EvidenceItem('spectral', f"{k} is {v}", 'global', 0.85, 'index'))
                
        if 'grounding' in tool_results:
            gr = tool_results['grounding']
            box_list = []
            if isinstance(gr, dict):
                box_list = gr.get('boxes', [])
            elif isinstance(gr, list):
                box_list = gr
            for item in box_list:
                if isinstance(item, dict):
                    evidence.append(EvidenceItem(
                        'grounding',
                        f"Grounded {item.get('label', 'feature')}",
                        item.get('bbox_norm', item.get('bbox', 'unknown')),
                        float(item.get('confidence', item.get('score', 0.8))),
                        'detection'
                    ))
                
        if 'change_detection' in tool_results and isinstance(tool_results['change_detection'], dict):
            res = tool_results['change_detection']
            pct = res.get('overall_change_pct', 0)
            dominant = res.get('dominant_change_type', 'surface modification')
            evidence.append(EvidenceItem(
                'change_detector',
                f"Bi-temporal change detected: {pct:.1f}% scene change ({dominant})",
                'scene',
                float(res.get('confidence_score', 0.88)),
                'change'
            ))
            
        if 'sar_processing' in tool_results and isinstance(tool_results['sar_processing'], dict):
            sar_res = tool_results['sar_processing']
            evidence.append(EvidenceItem(
                'sar_processor',
                f"SAR Backscatter analysis: Water {sar_res.get('water_pct', 0):.1f}%, Built-up {sar_res.get('buildup_pct', 0):.1f}%",
                'sar_footprint',
                0.86,
                'sar_structural'
            ))

        if 'fusion' in tool_results and isinstance(tool_results['fusion'], dict):
            fus = tool_results['fusion']
            agr = fus.get('agreement_score', 0.8)
            evidence.append(EvidenceItem(
                'fusion_engine',
                f"Cross-modal optical-SAR agreement: {agr:.2f}",
                'fused_scene',
                float(agr),
                'multimodal_agreement'
            ))

        # Deduplicate
        seen = set()
        deduped = []
        for e in evidence:
            reg_key = str(e.region)
            key = f"{e.claim}_{reg_key}"
            if key not in seen:
                seen.add(key)
                deduped.append(e)
                
        return sorted(deduped, key=lambda x: x.score, reverse=True)
