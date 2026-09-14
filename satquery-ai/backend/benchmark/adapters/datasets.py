"""
SatQuery AI — Benchmark Adapters
Dataset adapters for VRSBench, RSVQA, CDVQA evaluation.
"""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator


@dataclass
class BenchmarkSample:
    sample_id: str
    image_path: str
    image_t2_path: str | None  # for temporal
    question: str
    reference_answer: str
    task: str  # vqa | captioning | grounding | change_vqa
    metadata: dict


class VRSBenchAdapter:
    """
    Adapter for VRSBench — Remote Sensing Vision-Language Benchmark.
    
    VRSBench contains remote-sensing images with:
    - Human-verified captions
    - Referring expressions
    - Question-answer pairs
    
    Expected dataset structure:
    vrsbench/
        images/
        annotations.json (with image_id, caption, qa_pairs, referring_expressions)
    
    Paper: VRSBench: A Versatile Vision-Language Benchmark for Remote Sensing
    """
    DATASET_NAME = "VRSBench"
    TASKS = ["captioning", "vqa", "grounding"]

    def __init__(self, dataset_path: Path):
        self.path = Path(dataset_path)

    def is_available(self) -> bool:
        return (self.path / "annotations.json").exists()

    def load(self, task: str = "vqa", limit: int = 100) -> list[BenchmarkSample]:
        if not self.is_available():
            return []
        
        with open(self.path / "annotations.json") as f:
            data = json.load(f)

        samples = []
        for item in data[:limit]:
            img_path = str(self.path / "images" / item.get("image_file", ""))
            if task == "captioning":
                samples.append(BenchmarkSample(
                    sample_id=str(item.get("id", len(samples))),
                    image_path=img_path,
                    image_t2_path=None,
                    question="Describe this satellite image.",
                    reference_answer=item.get("caption", ""),
                    task="captioning",
                    metadata={"source": "VRSBench"},
                ))
            elif task == "vqa":
                for qa in item.get("qa_pairs", []):
                    samples.append(BenchmarkSample(
                        sample_id=f"{item.get('id')}_{len(samples)}",
                        image_path=img_path,
                        image_t2_path=None,
                        question=qa["question"],
                        reference_answer=qa["answer"],
                        task="vqa",
                        metadata={"source": "VRSBench", "qa_type": qa.get("type")},
                    ))
            if len(samples) >= limit:
                break
        return samples


class RSVQAAdapter:
    """
    Adapter for RSVQA — Remote Sensing Visual Question Answering.
    
    RSVQA questions include:
    - Yes/No presence questions
    - Counting questions
    - Comparison questions
    - Land-cover questions
    
    Paper: RSVQA: Visual Question Answering for Remote Sensing Data
    """
    DATASET_NAME = "RSVQA"
    TASKS = ["vqa"]
    ANSWER_TYPES = ["presence", "count", "comparison", "area"]

    def __init__(self, dataset_path: Path):
        self.path = Path(dataset_path)

    def is_available(self) -> bool:
        return (self.path / "RSVQA_LR").exists() or (self.path / "RSVQA_HR").exists()

    def load(self, split: str = "test", limit: int = 100) -> list[BenchmarkSample]:
        if not self.is_available():
            return []

        samples = []
        for variant in ["RSVQA_LR", "RSVQA_HR"]:
            base = self.path / variant
            if not base.exists():
                continue
            
            q_file = base / f"Questions_{split}_LR.json" if "LR" in variant else base / f"Questions_{split}.json"
            a_file = base / f"Answers_{split}_LR.json" if "LR" in variant else base / f"Answers_{split}.json"
            
            if not q_file.exists():
                continue

            with open(q_file) as f:
                questions = json.load(f).get("questions", [])
            
            answers = {}
            if a_file.exists():
                with open(a_file) as f:
                    for ans in json.load(f).get("answers", []):
                        answers[ans["id"]] = ans["answer"]

            for q in questions[:limit]:
                img_id = q.get("img_id", "")
                samples.append(BenchmarkSample(
                    sample_id=str(q.get("id")),
                    image_path=str(base / "Images" / f"{img_id}.tif"),
                    image_t2_path=None,
                    question=q.get("question", ""),
                    reference_answer=str(answers.get(q.get("id"), "")),
                    task="vqa",
                    metadata={
                        "source": "RSVQA",
                        "type": q.get("type", ""),
                        "variant": variant,
                    },
                ))
                if len(samples) >= limit:
                    break
        return samples

    @staticmethod
    def normalize_answer(answer: str) -> str:
        """Normalize answer for comparison (handles yes/no, numbers)."""
        ans = answer.lower().strip()
        # Normalize boolean
        if ans in {"yes", "true", "1", "correct"}:
            return "yes"
        if ans in {"no", "false", "0", "incorrect"}:
            return "no"
        # Normalize numbers
        try:
            return str(int(float(ans)))
        except ValueError:
            return ans


class CDVQAAdapter:
    """
    Adapter for CDVQA — Change Detection Visual Question Answering.
    
    CDVQA questions involve temporal reasoning about bi-temporal image pairs.
    Input: image_t1, image_t2, question
    Output: answer about changes
    
    Paper: Change Detection Meets Visual Question Answering
    """
    DATASET_NAME = "CDVQA"
    TASKS = ["change_vqa"]

    def __init__(self, dataset_path: Path):
        self.path = Path(dataset_path)

    def is_available(self) -> bool:
        return (self.path / "images").exists() and (self.path / "questions.json").exists()

    def load(self, split: str = "test", limit: int = 100) -> list[BenchmarkSample]:
        if not self.is_available():
            return []

        with open(self.path / "questions.json") as f:
            data = json.load(f)

        samples = []
        for item in data.get(split, data)[:limit]:
            img_dir = self.path / "images"
            samples.append(BenchmarkSample(
                sample_id=str(item.get("id", len(samples))),
                image_path=str(img_dir / item.get("t1_image", "")),
                image_t2_path=str(img_dir / item.get("t2_image", "")),
                question=item.get("question", ""),
                reference_answer=item.get("answer", ""),
                task="change_vqa",
                metadata={
                    "source": "CDVQA",
                    "change_type": item.get("change_type", ""),
                },
            ))
        return samples


class BenchmarkEvaluator:
    """Runs benchmark evaluation and computes metrics."""

    def __init__(self, analyzer_fn):
        """analyzer_fn: callable(image_path, t2_path, question, input_mode) -> str"""
        self.analyzer = analyzer_fn

    def evaluate(self, samples: list[BenchmarkSample]) -> dict:
        predictions = []
        correct = 0

        for sample in samples:
            try:
                input_mode = "bitemporal" if sample.image_t2_path else "single"
                pred = self.analyzer(
                    sample.image_path,
                    sample.image_t2_path,
                    sample.question,
                    input_mode,
                )
                ref = sample.reference_answer
                pred_norm = RSVQAAdapter.normalize_answer(str(pred))
                ref_norm = RSVQAAdapter.normalize_answer(str(ref))
                match = pred_norm == ref_norm
                if match:
                    correct += 1
                predictions.append({
                    "id": sample.sample_id,
                    "question": sample.question,
                    "reference": ref,
                    "prediction": pred,
                    "correct": match,
                })
            except Exception as e:
                predictions.append({
                    "id": sample.sample_id,
                    "question": sample.question,
                    "reference": sample.reference_answer,
                    "prediction": f"ERROR: {e}",
                    "correct": False,
                })

        total = len(samples)
        return {
            "total": total,
            "correct": correct,
            "accuracy": correct / total if total > 0 else 0.0,
            "predictions": predictions,
        }
