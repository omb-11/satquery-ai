"""
SatQuery AI — Confidence Estimator
Computes evidence-based confidence scores.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ConfidenceReport:
    score: float
    level: str
    factors: List[dict]
    limitations: List[str]

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "level": self.level,
            "factors": self.factors,
            "limitations": self.limitations,
        }


class ConfidenceEstimator:
    """
    Computes confidence from real evidence.
    Weighted combination of:
      model_score * 0.30
    + evidence_score * 0.30
    + input_quality * 0.20
    + registration_score * 0.20
    Minus penalties for missing CRS, poor registration, low confidence.
    """

    def estimate(
        self,
        evidence: List[Any],  # list of dicts or EvidenceItem
        input_quality: float,
        registration_score: float,
        tool_results: Dict[str, Any],
        task_type: str,
    ) -> "ConfidenceReport":

        if not evidence:
            return ConfidenceReport(
                score=0.3,
                level="low",
                factors=[{"reason": "no evidence collected"}],
                limitations=["No evidence was produced by any analysis tool."],
            )

        # Extract scores safely from dicts or dataclass instances
        scores = []
        for ev in evidence:
            if isinstance(ev, dict):
                scores.append(float(ev.get("score", 0.5)))
            elif hasattr(ev, "score"):
                scores.append(float(ev.score))
            else:
                scores.append(0.5)

        model_score = sum(scores) / len(scores) if scores else 0.3
        evidence_score = min(1.0, len(evidence) / 10.0)  # saturates at 10+ items

        final_score = (
            model_score * 0.30
            + evidence_score * 0.30
            + input_quality * 0.20
            + registration_score * 0.20
        )

        factors = [
            {"name": "model_score", "value": round(model_score, 3), "weight": 0.30},
            {"name": "evidence_count", "value": len(evidence), "weight": 0.30},
            {"name": "input_quality", "value": round(input_quality, 3), "weight": 0.20},
            {"name": "registration", "value": round(registration_score, 3), "weight": 0.20},
        ]
        limitations = []

        # Penalty: no georeference
        spectral = tool_results.get("spectral", {})
        if isinstance(spectral, dict) and not spectral.get("has_crs", True):
            final_score -= 0.08
            limitations.append("Image lacks georeferencing — spatial coordinates unavailable.")

        # Penalty: poor registration
        if registration_score < 0.5:
            final_score -= 0.15
            limitations.append("Low pair registration score — results may be misaligned.")

        # Penalty: low model confidence
        if model_score < 0.45:
            final_score -= 0.08
            limitations.append("Model confidence is low for this image/query combination.")

        # Task-specific adjustments
        if task_type in ("OPTICAL_SAR_FUSION",):
            agreement = tool_results.get("fusion", {}).get("agreement_score", None)
            if isinstance(agreement, (int, float)):
                if agreement > 0.8:
                    final_score = min(1.0, final_score + 0.05)
                    factors.append({"name": "cross_modal_agreement", "value": round(agreement, 3)})
                elif agreement < 0.5:
                    final_score -= 0.05
                    limitations.append("Low optical-SAR agreement in some regions.")

        final_score = max(0.0, min(1.0, final_score))

        if final_score >= 0.75:
            level = "high"
        elif final_score >= 0.50:
            level = "medium"
        else:
            level = "low"

        return ConfidenceReport(
            score=round(final_score, 3),
            level=level,
            factors=factors,
            limitations=limitations,
        )
