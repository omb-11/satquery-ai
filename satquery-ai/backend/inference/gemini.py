"""
SatQuery AI — Gemini AI Analyst
Agentic remote-sensing analyst integrating Google Gemini with structured function calling.
Zero-hallucination policy: Gemini synthesizes explanations from actual remote sensing tool outputs.
"""
from __future__ import annotations
import json
import time
from typing import Dict, Any, List, Optional
from loguru import logger
import httpx

from backend.core.config import settings

# Strict Gemini Tool / Function Declarations
SATQUERY_TOOL_DEFINITIONS = [
    {
        "name": "calculate_spectral_indices",
        "description": "Computes normalized remote-sensing indices (NDVI, NDWI, NDBI) on optical raster bands.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "index_types": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "List of indices to calculate, e.g. ['NDVI', 'NDWI', 'NDBI']"
                }
            },
            "required": ["index_types"]
        }
    },
    {
        "name": "detect_change",
        "description": "Executes Otsu radiometric thresholding & connected-component change analysis between T1 and T2.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "threshold": {
                    "type": "NUMBER",
                    "description": "Radiometric difference threshold (0.05 to 0.40). Default is 0.15."
                }
            }
        }
    },
    {
        "name": "analyze_optical_sar",
        "description": "Corroborates Sentinel-2 optical multispectral imagery with Sentinel-1 SAR C-band radar backscatter.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "ground_text",
        "description": "Detects and localizes specific query concepts (water, buildings, roads, vegetation) with bounding boxes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "concept": {
                    "type": "STRING",
                    "description": "Entity concept to ground, e.g. 'water body', 'structure', 'vegetation'"
                }
            },
            "required": ["concept"]
        }
    }
]

class GeminiAnalyst:
    """
    SatQuery Analyst powered by Google Gemini.
    Interprets natural language queries, selects tools, and synthesizes structured findings.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model or "gemini-1.5-flash"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def is_configured(self) -> bool:
        """Returns True if a non-empty API key is configured."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    async def test_connection(self) -> Dict[str, Any]:
        """Tests connectivity and latency to the configured Gemini model."""
        if not self.is_configured():
            return {
                "status": "NOT_CONFIGURED",
                "message": "Gemini API key is not configured. Local fallback pipeline is active.",
                "latency_ms": 0
            }

        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.api_url}?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": "Respond with the single word: READY"}]}]
                }
                resp = await client.post(url, json=payload)
                elapsed = (time.time() - t0) * 1000

                if resp.status_code == 200:
                    return {
                        "status": "READY",
                        "model": self.model,
                        "latency_ms": round(elapsed, 1),
                        "capabilities": ["Vision", "Function Calling", "Structured Synthesis"]
                    }
                else:
                    return {
                        "status": "ERROR",
                        "message": f"Gemini API returned status {resp.status_code}: {resp.text[:120]}",
                        "latency_ms": round(elapsed, 1)
                    }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Connection error: {str(e)}",
                "latency_ms": round((time.time() - t0) * 1000, 1)
            }

    async def synthesize_briefing(
        self,
        query: str,
        task_type: str,
        tool_results: Dict[str, Any],
        evidence: List[Any],
        confidence_report: Any,
        metadata: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Synthesizes a structured intelligence briefing via Gemini based on ACTUAL tool outputs.
        Returns a dict matching the structured schema if successful, or None on failure/unconfigured.
        """
        if not self.is_configured():
            return None

        # Build prompt containing ONLY real ground-truth numbers & metadata
        evidence_summary = [
            {
                "source": getattr(e, 'source', ''),
                "claim": getattr(e, 'claim', ''),
                "score": getattr(e, 'score', 0.5),
                "region": getattr(e, 'region', []),
                "category": getattr(e, 'category', '')
            }
            for e in evidence
        ]

        system_instruction = (
            "You are the SatQuery AI Remote Sensing Analyst for ISRO SIH 2026. "
            "You are given ACTUAL tool computation results and metadata from satellite rasters. "
            "STRICT ZERO-HALLUCINATION RULE: NEVER invent coordinates, area percentages, or spectral values. "
            "Synthesize a clear, authoritative intelligence answer based strictly on the provided evidence. "
            "Output your answer as a JSON object with this exact schema:\n"
            "{\n"
            "  \"intent\": \"<interpreted intent>\",\n"
            "  \"summary\": \"<one-line executive verdict>\",\n"
            "  \"answer\": \"<detailed findings and physical interpretation>\"\n"
            "}"
        )

        user_content = {
            "operator_query": query,
            "classified_task": task_type,
            "actual_tool_results": {
                k: v for k, v in tool_results.items() if not isinstance(v, bytes)
            },
            "verified_evidence": evidence_summary,
            "confidence_level": getattr(confidence_report, 'level', 'Medium'),
            "confidence_score": getattr(confidence_report, 'score', 0.75),
            "limitations": getattr(confidence_report, 'limitations', [])
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                url = f"{self.api_url}?key={self.api_key}"
                payload = {
                    "contents": [
                        {"role": "user", "parts": [{"text": json.dumps(user_content, default=str)}]}
                    ],
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.2
                    }
                }
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        raw_text = candidates[0]["content"]["parts"][0]["text"]
                        parsed = json.loads(raw_text)
                        return parsed
                else:
                    logger.warning(f"Gemini synthesis returned status {resp.status_code}: {resp.text[:150]}")
        except Exception as e:
            logger.warning(f"Gemini synthesis bypassed due to exception: {e}")

        return None
