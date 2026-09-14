"""
SatQuery AI — Agent Orchestrator
Real agentic pipeline connecting all specialist tools.
"""
from __future__ import annotations
import asyncio
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator
from loguru import logger

from .state import AgentState, TraceStep, EvidenceItem, ConfidenceReport
from .router import TaskRouter
from .planner import TaskPlanner


class AgentOrchestrator:
    """
    Main agentic controller.
    
    Pipeline: validate → classify → plan → execute tools → aggregate evidence
             → estimate confidence → synthesize answer → verify
    """

    def __init__(self):
        self.router = TaskRouter()
        self.planner = TaskPlanner()

    def _trace(self, state: AgentState, step_num: int, name: str, status: str,
               tool: str, output: str, elapsed_ms: float):
        step = TraceStep(
            step_num=step_num,
            name=name,
            status=status,
            tool=tool,
            output=output[:200],
            elapsed_ms=elapsed_ms,
            timestamp=datetime.utcnow().isoformat(),
        )
        state.trace.append(step)
        logger.info(f"[{step_num:02d}] {name} | {tool} | {elapsed_ms:.0f}ms | {output[:80]}")

    async def analyze(
        self, query: str, input_paths: list[str], input_mode: str, parameters: dict = None
    ) -> AgentState:
        """Run full analysis pipeline. Returns completed AgentState."""
        t_total = time.time()
        from backend.core.config import settings
        
        initial_params = dict(parameters or {})
        prec_mode = initial_params.get("precision_mode", settings.precision_mode or "balanced")
        initial_params["precision_mode"] = prec_mode
        
        # Configure precision-specific thresholds
        if prec_mode == "fast":
            initial_params.setdefault("target_dim", 512)
            initial_params.setdefault("threshold", 0.20)
            initial_params.setdefault("min_area_px", 100)
        elif prec_mode == "precise":
            initial_params.setdefault("target_dim", 1536)
            initial_params.setdefault("threshold", 0.10)
            initial_params.setdefault("min_area_px", 25)
        else: # balanced or expert
            initial_params.setdefault("target_dim", 1024)
            initial_params.setdefault("threshold", 0.15)
            initial_params.setdefault("min_area_px", 50)

        state = AgentState(
            run_id=str(uuid.uuid4()),
            query=query,
            input_mode=input_mode,
            input_paths=input_paths,
            input_metadata=[],
            task_type="",
            selected_tools=[],
            tool_results={},
            evidence=[],
            confidence=ConfidenceReport(score=0.0, level="low", factors=[], limitations=[]),
            final_answer="",
            findings=[],
            models_used=[],
            parameters=initial_params,
            limitations=[],
            trace=[],
            status="running",
            error="",
            created_at=datetime.utcnow().isoformat(),
            completed_at="",
            processing_times={},
            precision_mode=prec_mode,
            tools_used=[]
        )

        try:
            step = 1

            # ── Step 1: Input Validation ──────────────────────────────────
            t0 = time.time()
            from backend.tools.validator import ImageValidator
            validator = ImageValidator()
            validation_results = []
            input_quality = 1.0
            for path in input_paths:
                if not Path(path).exists():
                    # File not found — use metadata from path name only
                    vr = type('VR', (), {'is_valid': False, 'checks_passed': [], 'checks_failed': ['File not found'], 'warnings': [], 'modality': 'unknown'})()
                else:
                    vr = validator.validate_single(path)
                validation_results.append(vr)

            failed = [v for v in validation_results if not v.is_valid]
            if failed and len(failed) == len(input_paths):
                state.status = "error"
                state.error = "All input files failed validation"
                self._trace(state, step, "Input Validation", "error", "ImageValidator",
                            "All files invalid", (time.time() - t0) * 1000)
                return state

            input_quality = sum(1 for v in validation_results if v.is_valid) / len(validation_results)
            state.parameters["input_quality"] = input_quality
            validation_summary = f"{len(validation_results) - len(failed)}/{len(validation_results)} files valid"
            self._trace(state, step, "Input Validation", "done", "ImageValidator",
                        validation_summary, (time.time() - t0) * 1000)
            step += 1

            # ── Step 2: Metadata Extraction ───────────────────────────────
            t0 = time.time()
            from backend.geospatial.metadata import extract_metadata
            metadata_list = []
            for path in input_paths:
                if Path(path).exists():
                    try:
                        meta = extract_metadata(path)
                        metadata_list.append(meta.__dict__ if hasattr(meta, '__dict__') else vars(meta))
                    except Exception as e:
                        metadata_list.append({"error": str(e), "path": path})
                else:
                    metadata_list.append({"path": path, "available": False})
            state.input_metadata = metadata_list
            meta_summary = f"Extracted metadata for {len(metadata_list)} inputs"
            self._trace(state, step, "Metadata Extraction", "done", "RasterMetadataExtractor",
                        meta_summary, (time.time() - t0) * 1000)
            step += 1

            # ── Step 3: Task Classification ───────────────────────────────
            t0 = time.time()
            state.task_type = self.router.classify(query, input_mode, state.input_metadata)
            state.selected_tools = self.router.get_required_tools(state.task_type, input_mode)
            self._trace(state, step, "Task Classification", "done", "TaskRouter",
                        f"→ {state.task_type} | Tools: {', '.join(state.selected_tools)}",
                        (time.time() - t0) * 1000)
            step += 1

            # ── Step 4: Preprocessing ─────────────────────────────────────
            t0 = time.time()
            from backend.tools.preprocessor import RasterPreprocessor
            preprocessor = RasterPreprocessor()
            preprocess_results = {}
            for i, path in enumerate(input_paths):
                if Path(path).exists():
                    try:
                        modality = "sar" if (input_mode == "optical_sar" and i == 1) else "optical"
                        pr = preprocessor.preprocess(path, {}, target_dim=512)
                        preprocess_results[path] = pr
                    except Exception as e:
                        preprocess_results[path] = {"error": str(e)}
            state.tool_results["preprocessing"] = {k: "ok" for k in preprocess_results}
            self._trace(state, step, "Preprocessing", "done", "RasterPreprocessor",
                        f"Preprocessed {len(preprocess_results)} images",
                        (time.time() - t0) * 1000)
            step += 1

            # ── Step 5: Spectral Analysis ─────────────────────────────────
            t0 = time.time()
            spectral_results = {}
            if input_paths and Path(input_paths[0]).exists():
                try:
                    from backend.tools.spectral import SpectralAnalyzer
                    sa = SpectralAnalyzer()
                    sr = sa.analyze_raster(input_paths[0], metadata_list[0] if metadata_list else {})
                    spectral_results = sr.__dict__ if hasattr(sr, '__dict__') else {}
                    state.tool_results["spectral"] = spectral_results
                    indices = spectral_results.get("available_indices", [])
                    self._trace(state, step, "Spectral Analysis", "done", "SpectralAnalyzer",
                                f"Indices: {indices if indices else 'RGB only — multispectral unavailable'}",
                                (time.time() - t0) * 1000)
                    state.models_used.append("SpectralAnalyzer")
                except Exception as e:
                    self._trace(state, step, "Spectral Analysis", "skipped", "SpectralAnalyzer",
                                f"Skipped: {e}", (time.time() - t0) * 1000)
            step += 1

            # ── Step 6: Task-specific Analysis ───────────────────────────
            registration_score = 1.0

            if state.task_type in ("CHANGE_DETECTION", "CHANGE_VQA", "CHANGE_DESCRIPTION") \
                    and len(input_paths) >= 2:
                # Change Detection
                t0 = time.time()
                try:
                    from backend.tools.change_detector import ChangeDetector
                    cd = ChangeDetector()
                    threshold = float(state.parameters.get("threshold", 0.15))
                    cr = cd.detect(input_paths[0], input_paths[1],
                                   threshold=threshold, query=query)
                    state.tool_results["change_detection"] = cr.__dict__ if hasattr(cr, '__dict__') else {}
                    state.parameters["change_pct"] = getattr(cr, "overall_change_pct", 0)
                    state.parameters["threshold"] = threshold
                    state.parameters["change_backend"] = getattr(cr, "backend_used", "classical")
                    # Add evidence from change regions
                    for region in getattr(cr, "regions", [])[:10]:
                        ev = EvidenceItem(
                            source="change_detector",
                            claim=f"Change detected: {getattr(region, 'change_type', 'unknown')}",
                            region=list(getattr(region, 'bbox', [0, 0, 1, 1])),
                            score=float(getattr(region, 'confidence', 0.7)),
                            image_key="T2",
                            category=getattr(region, 'change_type', 'unknown'),
                        )
                        state.evidence.append(ev)
                    n_regions = len(getattr(cr, "regions", []))
                    self._trace(state, step, "Change Detection", "done", "ChangeDetector",
                                f"{n_regions} regions | {getattr(cr, 'overall_change_pct', 0):.1f}% change | backend: {getattr(cr, 'backend_used', 'classical')}",
                                (time.time() - t0) * 1000)
                    state.models_used.append("ChangeDetector (classical)")
                except Exception as e:
                    logger.error(f"Change detection error: {e}")
                    self._trace(state, step, "Change Detection", "error", "ChangeDetector",
                                str(e), (time.time() - t0) * 1000)
                step += 1

            elif state.task_type in ("OPTICAL_SAR_FUSION", "OPTICAL_SAR_VQA") \
                    and len(input_paths) >= 2:
                # SAR Processing + Fusion
                t0 = time.time()
                try:
                    from backend.tools.sar_processor import SARProcessor
                    sp = SARProcessor()
                    sar_result = sp.process(input_paths[1], {})
                    state.tool_results["sar_processing"] = sar_result.__dict__ if hasattr(sar_result, '__dict__') else {}
                    state.models_used.append("SARProcessor (classical)")
                    self._trace(state, step, "SAR Processing", "done", "SARProcessor",
                                f"Water: {getattr(sar_result, 'water_pct', 0):.1f}% | Built-up: {getattr(sar_result, 'buildup_pct', 0):.1f}%",
                                (time.time() - t0) * 1000)
                except Exception as e:
                    self._trace(state, step, "SAR Processing", "error", "SARProcessor",
                                str(e), (time.time() - t0) * 1000)
                step += 1

                t0 = time.time()
                try:
                    from backend.tools.fusion_engine import OpticalSARFusionEngine
                    fe = OpticalSARFusionEngine()
                    fr = fe.fuse(input_paths[0], input_paths[1], query=query)
                    state.tool_results["fusion"] = fr.__dict__ if hasattr(fr, '__dict__') else {}
                    state.parameters["agreement_score"] = getattr(fr, "agreement_score", 0)
                    fused_ev = getattr(fr, "fused_evidence", {})
                    for feat, score in fused_ev.items():
                        state.evidence.append(EvidenceItem(
                            source="fusion_engine",
                            claim=f"Fused evidence: {feat}",
                            region=[0, 0, 1, 1],
                            score=float(score),
                            image_key="fusion",
                            category=feat,
                        ))
                    state.models_used.append("OpticalSARFusionEngine")
                    self._trace(state, step, "Optical-SAR Fusion", "done", "FusionEngine",
                                f"Agreement: {getattr(fr, 'agreement_score', 0):.2f}",
                                (time.time() - t0) * 1000)
                except Exception as e:
                    self._trace(state, step, "Optical-SAR Fusion", "error", "FusionEngine",
                                str(e), (time.time() - t0) * 1000)
                step += 1

            # ── Step 7: Grounding ─────────────────────────────────────────
            if state.task_type in ("SINGLE_GROUNDING", "OBJECT_IDENTIFICATION", "LAND_COVER_ANALYSIS") \
                    and input_paths:
                t0 = time.time()
                if Path(input_paths[0]).exists():
                    try:
                        from backend.tools.grounding import GroundingAnalyzer
                        ga = GroundingAnalyzer()
                        gr = ga.ground(input_paths[0], query, metadata_list[0] if metadata_list else {})
                        state.tool_results["grounding"] = gr.__dict__ if hasattr(gr, '__dict__') else {}
                        for box in getattr(gr, "boxes", [])[:8]:
                            state.evidence.append(EvidenceItem(
                                source="grounding",
                                claim=f"Located: {box.get('label', 'object')}",
                                region=list(box.get("bbox_norm", [0, 0, 1, 1])),
                                score=float(box.get("confidence", 0.6)),
                                image_key="original",
                                category=box.get("label", "object"),
                            ))
                        n_boxes = len(getattr(gr, "boxes", []))
                        self._trace(state, step, "Text-guided Grounding", "done", "GroundingAnalyzer",
                                    f"{n_boxes} objects located | method: {getattr(gr, 'method_used', 'spectral')}",
                                    (time.time() - t0) * 1000)
                        state.models_used.append("GroundingAnalyzer (spectral)")
                    except Exception as e:
                        self._trace(state, step, "Grounding", "error", "GroundingAnalyzer",
                                    str(e), (time.time() - t0) * 1000)
                step += 1

            # ── Step 8: VQA / Caption ─────────────────────────────────────
            t0 = time.time()
            if input_paths and Path(input_paths[0]).exists():
                try:
                    if state.task_type in ("SINGLE_VQA", "CHANGE_VQA", "OPTICAL_SAR_VQA"):
                        from backend.inference.vqa import VQASpecialist
                        vqa = VQASpecialist()
                        vqa_result = vqa.run(input_paths[0], query,
                                             metadata_list[0] if metadata_list else {})
                        state.tool_results["vqa"] = vqa_result.__dict__ if hasattr(vqa_result, '__dict__') else {}
                        state.models_used.append(getattr(vqa_result, "model_name", "VQA"))
                        self._trace(state, step, "VQA Inference", "done",
                                    getattr(vqa_result, "model_name", "VQA"),
                                    f"Answer: {str(getattr(vqa_result, 'answer', ''))[:80]}",
                                    (time.time() - t0) * 1000)
                    else:
                        from backend.inference.captioning import CaptioningSpecialist
                        cap = CaptioningSpecialist()
                        cap_result = cap.run(input_paths[0], metadata_list[0] if metadata_list else {},
                                             spectral_results=spectral_results)
                        state.tool_results["captioning"] = cap_result.__dict__ if hasattr(cap_result, '__dict__') else {}
                        state.models_used.append(getattr(cap_result, "method_used", "Captioning"))
                        self._trace(state, step, "Caption Generation", "done",
                                    getattr(cap_result, "method_used", "Captioning"),
                                    str(getattr(cap_result, "caption", ""))[:80],
                                    (time.time() - t0) * 1000)
                except Exception as e:
                    logger.warning(f"VQA/Caption error: {e}")
                    self._trace(state, step, "VQA/Caption", "error", "VLM",
                                f"Fallback: {e}", (time.time() - t0) * 1000)
            step += 1

            # ── Step 9: Evidence Aggregation ──────────────────────────────
            t0 = time.time()
            try:
                from backend.evidence.aggregator import EvidenceAggregator
                agg = EvidenceAggregator()
                additional = agg.aggregate(state.tool_results, state.task_type, query)
                state.evidence.extend(additional)
                # Deduplicate and sort
                state.evidence = sorted(state.evidence, key=lambda e: e.score, reverse=True)[:20]
                self._trace(state, step, "Evidence Aggregation", "done", "EvidenceAggregator",
                            f"{len(state.evidence)} evidence items aggregated",
                            (time.time() - t0) * 1000)
            except Exception as e:
                self._trace(state, step, "Evidence Aggregation", "error", "EvidenceAggregator",
                            str(e), (time.time() - t0) * 1000)
            step += 1

            # ── Step 10: Confidence Estimation ────────────────────────────
            t0 = time.time()
            try:
                from backend.evidence.confidence import ConfidenceEstimator
                ce = ConfidenceEstimator()
                state.confidence = ce.estimate(
                    [e.__dict__ if hasattr(e, '__dict__') else e for e in state.evidence],
                    input_quality,
                    registration_score,
                    state.tool_results,
                    state.task_type,
                )
                self._trace(state, step, "Confidence Estimation", "done", "ConfidenceEstimator",
                            f"Score: {state.confidence.score:.2f} ({state.confidence.level})",
                            (time.time() - t0) * 1000)
            except Exception as e:
                state.confidence = ConfidenceReport(0.5, "medium", [], [str(e)])
                self._trace(state, step, "Confidence Estimation", "error", "ConfidenceEstimator",
                            str(e), (time.time() - t0) * 1000)
            step += 1

            # ── Step 11: Answer Synthesis (Gemini Analyst with Local Fallback) ──
            t0 = time.time()
            try:
                from backend.agents.synthesizer import AnswerSynthesizer
                synth = AnswerSynthesizer()
                local_answer = synth.synthesize(state)
                state.final_answer = local_answer
                
                # Check for Gemini AI Analyst
                try:
                    from backend.inference.gemini import GeminiAnalyst
                    gemini = GeminiAnalyst()
                    if gemini.is_configured():
                        briefing = await gemini.synthesize_briefing(
                            query, state.task_type, state.tool_results, state.evidence,
                            state.confidence, state.input_metadata, state.parameters
                        )
                        if briefing and briefing.get("answer"):
                            state.final_answer = briefing["answer"]
                            state.summary = briefing.get("summary", "")
                            state.intent = briefing.get("intent", "")
                            state.models_used.append(f"Google {gemini.model} (Analyst)")
                            self._trace(state, step, "Intelligence Synthesis", "done",
                                        f"Gemini {gemini.model}", "Structured evidence-backed briefing",
                                        (time.time() - t0) * 1000)
                        else:
                            self._trace(state, step, "Answer Synthesis", "done", "AnswerSynthesizer",
                                        "Evidence-backed response ready (local engine)",
                                        (time.time() - t0) * 1000)
                    else:
                        self._trace(state, step, "Answer Synthesis", "done", "AnswerSynthesizer",
                                    "Evidence-backed response ready (deterministic fallback)",
                                    (time.time() - t0) * 1000)
                except Exception as gem_e:
                    logger.debug(f"Gemini analyst bypassed: {gem_e}")
                    self._trace(state, step, "Answer Synthesis", "done", "AnswerSynthesizer",
                                "Evidence-backed response ready",
                                (time.time() - t0) * 1000)
            except Exception as e:
                logger.error(f"Synthesis error: {e}")
                state.final_answer = self._fallback_answer(state)
                self._trace(state, step, "Answer Synthesis", "error", "AnswerSynthesizer",
                            str(e), (time.time() - t0) * 1000)
            step += 1

            # ── Step 12: Evidence Verification ───────────────────────────
            t0 = time.time()
            try:
                from backend.evidence.verifier import EvidenceVerifier
                ev = EvidenceVerifier()
                state.evidence, removed = ev.verify(state)
                if removed:
                    state.limitations.extend([f"Removed unsupported claim: {c}" for c in removed[:3]])
                self._trace(state, step, "Evidence Verification", "done", "EvidenceVerifier",
                            f"{len(state.evidence)} verified | {len(removed)} claims removed",
                            (time.time() - t0) * 1000)
            except Exception as e:
                self._trace(state, step, "Evidence Verification", "error", "EvidenceVerifier",
                            str(e), (time.time() - t0) * 1000)
            step += 1

            # ── Step 13: Spatial Focus & Visualization Planning ──────────
            t0 = time.time()
            try:
                from backend.tools.spatial_focus import SpatialFocusEngine
                from backend.tools.visualization_planner import VisualizationPlanner
                
                sfe = SpatialFocusEngine()
                state.spatial_focus = sfe.extract_focus(query, state.evidence, state.input_metadata)
                
                vp = VisualizationPlanner()
                v_plan = vp.plan(query, input_mode, state.tool_results, state.evidence, state.input_metadata, state.parameters)
                state.visualizations = v_plan.get("visualizations", [])
                state.charts = v_plan.get("charts", [])
                state.follow_up_questions = v_plan.get("follow_up_questions", [])
                state.tools_used = list(set(state.selected_tools + [t.tool for t in state.trace]))
                
                self._trace(state, step, "Visualization Planning", "done", "VisualizationPlanner",
                            f"{len(state.visualizations)} views & {len(state.charts)} charts planned",
                            (time.time() - t0) * 1000)
            except Exception as e:
                logger.warning(f"Visualization planning warning: {e}")
                self._trace(state, step, "Visualization Planning", "skipped", "VisualizationPlanner",
                            str(e), (time.time() - t0) * 1000)
            step += 1

            state.status = "complete"

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            state.status = "error"
            state.error = str(e)
            state.final_answer = f"Analysis encountered an error: {e}"
            state.confidence = ConfidenceReport(0.0, "low", [], [str(e)])

        finally:
            state.completed_at = datetime.utcnow().isoformat()
            total_ms = (time.time() - t_total) * 1000
            state.processing_times["total_ms"] = total_ms
            logger.info(f"Analysis complete | {state.task_type} | {total_ms:.0f}ms | confidence: {state.confidence.score:.2f}")

        return state

    async def analyze_stream(
        self, query: str, input_paths: list[str], input_mode: str, parameters: dict = None
    ) -> AsyncGenerator[str, None]:
        """Run analysis and yield SSE JSON strings for each trace step."""
        import json
        t_total = time.time()

        # Patch trace to yield events as steps are added
        events_queue: asyncio.Queue = asyncio.Queue()

        # Run analyze in a task and stream trace steps
        state_holder = {}

        async def run_analysis():
            state = await self.analyze(query, input_paths, input_mode, parameters=parameters)
            state_holder["state"] = state
            await events_queue.put(None)  # sentinel

        task = asyncio.create_task(run_analysis())

        # Simple approach: run fully, then stream trace
        await task
        state = state_holder.get("state")

        if state:
            for trace_step in state.trace:
                yield json.dumps({"type": "step", "data": trace_step.to_dict()})
                await asyncio.sleep(0.05)  # small delay for UI effect

            yield json.dumps({
                "type": "complete",
                "result": state.to_dict(),
            })

    def _fallback_answer(self, state: AgentState) -> str:
        """Generate a basic answer from available evidence when synthesis fails."""
        n_ev = len(state.evidence)
        if n_ev == 0:
            return (
                "FINDING\nInsufficient evidence to provide a reliable answer.\n\n"
                "LIMITATION\nAnalysis could not be completed. Please check image format and try again."
            )
        top = state.evidence[0] if state.evidence else None
        claim = top.claim if top else "No specific findings"
        return (
            f"FINDING\n{claim}\n\n"
            f"EVIDENCE\n• {n_ev} evidence item(s) collected\n\n"
            f"CONFIDENCE\n{state.confidence.level.upper()} — {state.confidence.score:.2f}"
        )
