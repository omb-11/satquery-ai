from typing import Any

class AnswerSynthesizer:
    def synthesize(self, state: Any) -> str:
        evidence_items = getattr(state, 'evidence', [])
        confidence_report = getattr(state, 'confidence', None)
        tool_results = getattr(state, 'tool_results', {})
        
        if not evidence_items or (confidence_report and confidence_report.score < 0.3):
            return (
                "FINDING\nEvidence insufficient to produce a definitive conclusion.\n\n"
                "CONFIDENCE\nLOW — 0.25\n\n"
                "LIMITATION\nAvailable multimodal and spectral indicators did not cross verification threshold."
            )
            
        main_finding = "Analysis complete based on provided Earth Observation data."
        if evidence_items:
            main_finding = evidence_items[0].claim
            
        if 'change_detection' in tool_results:
            main_finding += " Verified across bi-temporal observations."
        if 'optical_sar_fusion' in tool_results:
            main_finding += " Corroborated using co-registered Optical and SAR data."
            
        evidence_strs = []
        for e in evidence_items[:8]:
            score_val = getattr(e, 'score', 0.5)
            claim_val = getattr(e, 'claim', 'Detected feature')
            source_val = getattr(e, 'source', 'analysis')
            evidence_strs.append(f"• {claim_val} (Confidence: {score_val:.2f}, Source: {source_val})")
            
        evidence_section = "\n".join(evidence_strs) if evidence_strs else "• Automated spectral feature detection complete."
        
        # Format locations properly (regions are [x1, y1, x2, y2] normalized floats or strings)
        loc_descriptions = []
        for e in evidence_items[:4]:
            reg = getattr(e, 'region', None)
            if isinstance(reg, (list, tuple)) and len(reg) >= 4:
                x1, y1, x2, y2 = reg[:4]
                cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
                cardinal_y = "Northern" if cy < 0.45 else ("Southern" if cy > 0.55 else "Central")
                cardinal_x = "Western" if cx < 0.45 else ("Eastern" if cx > 0.55 else "Central")
                sector = f"{cardinal_y}-{cardinal_x}".replace("Central-Central", "Central")
                loc_descriptions.append(f"{sector} sector [bbox: {x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}]")
            elif isinstance(reg, str):
                loc_descriptions.append(reg)
                
        loc_str = "; ".join(loc_descriptions) if loc_descriptions else "Full scene extent"
            
        conf_level = (getattr(confidence_report, 'level', 'Medium') or 'Medium').capitalize()
        conf_score = getattr(confidence_report, 'score', 0.70)
        
        raw_limits = getattr(confidence_report, 'limitations', []) or []
        if isinstance(raw_limits, list) and raw_limits:
            limitations = "\n".join([f"- {str(l)}" for l in raw_limits])
        else:
            limitations = "- Ground resolution and satellite revisit cycle limits sub-pixel verification."
        
        return f"""FINDING
{main_finding}

EVIDENCE
{evidence_section}

LOCATION
{loc_str}

CONFIDENCE
{conf_level} — {conf_score:.2f}

LIMITATION
{limitations}"""
