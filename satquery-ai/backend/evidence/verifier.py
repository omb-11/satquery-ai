from typing import List, Tuple, Any
from .aggregator import EvidenceItem

# Mock AgentState for type hints since not fully defined here
class AgentState:
    evidence: List[EvidenceItem]
    
class EvidenceVerifier:
    def verify(self, state: Any) -> Tuple[List[EvidenceItem], List[str]]:
        verified = []
        removed = []
        
        for item in getattr(state, 'evidence', []):
            if item.score <= 0.1:
                removed.append(item.claim)
                continue
            if item.claim.strip() == "":
                removed.append("Empty claim")
                continue
            if item.score > 1.0:
                item.score = 1.0
            if item.score < 0.0:
                item.score = 0.0
                
            verified.append(item)
            
        return verified, removed
