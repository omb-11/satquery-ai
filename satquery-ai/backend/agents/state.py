from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any

@dataclass
class TraceStep:
    step_num: int
    name: str
    status: str
    tool: str
    output: str
    elapsed_ms: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass 
class EvidenceItem:
    source: str
    claim: str
    region: List[float]
    score: float
    image_key: str
    category: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ConfidenceReport:
    score: float
    level: str
    factors: List[Dict[str, Any]]
    limitations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AgentState:
    run_id: str
    query: str
    input_mode: str
    input_paths: List[str]
    input_metadata: List[Dict[str, Any]]
    task_type: str
    selected_tools: List[str]
    tool_results: Dict[str, Any]
    evidence: List[EvidenceItem]
    confidence: ConfidenceReport
    final_answer: str
    findings: List[Dict[str, Any]]
    models_used: List[str]
    parameters: Dict[str, Any]
    limitations: List[str]
    trace: List[TraceStep]
    status: str
    error: str
    created_at: str
    completed_at: str
    processing_times: Dict[str, float]
    # Enhanced structured fields
    intent: str = ""
    summary: str = ""
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    spatial_focus: List[Dict[str, Any]] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    precision_mode: str = "balanced"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["answer"] = self.final_answer
        d["task"] = self.task_type
        if not d.get("summary"):
            d["summary"] = self.final_answer.split("\n")[0] if self.final_answer else ""
        if not d.get("tools_used"):
            d["tools_used"] = self.selected_tools
        return d

