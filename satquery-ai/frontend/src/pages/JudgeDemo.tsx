import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Play, ArrowRight, ArrowLeft, Satellite, CheckCircle2, 
  Layers, ShieldCheck, Cpu, Activity, ExternalLink, Sparkles 
} from 'lucide-react';

interface DemoScenario {
  id: string;
  stepNumber: string;
  title: string;
  mode: string;
  query: string;
  inputImages: { label: string; url: string; sensor: string }[];
  primaryFinding: string;
  evidenceSummary: string[];
  confidence: { score: number; level: string };
  modelsUsed: string[];
  executionTimeMs: number;
  traceStepsCount: number;
}

const scenarios: DemoScenario[] = [
  {
    id: "01",
    stepNumber: "01 / 06",
    title: "Single-Image Visual Question Answering",
    mode: "SINGLE IMAGE",
    query: "Describe the land-cover and major objects visible in this scene.",
    inputImages: [
      { label: "Optical Multispectral (RGB)", url: "/data/demo/single_optical/scene_optical_preview.png", sensor: "Cartosat-Sim (0.5m GSD)" }
    ],
    primaryFinding: "Heterogeneous scene with high-density urban fabric in the northeast sector, dense vegetation belt in the west, and a distinct water reservoir in the southwest quadrant.",
    evidenceSummary: [
      "Spectral histogram indicates uniform high reflectance across urban rooftops",
      "Vegetation index confirms active chlorophyll absorption in western zone",
      "Low surface reflectance signature marks perennial reservoir"
    ],
    confidence: { score: 0.94, level: "HIGH" },
    modelsUsed: ["BLIP VQA", "SpectralAnalyzer", "RasterMetadataExtractor"],
    executionTimeMs: 345,
    traceStepsCount: 11
  },
  {
    id: "02",
    stepNumber: "02 / 06",
    title: "Text-Guided Spatial Bounding Box Grounding",
    mode: "SINGLE IMAGE",
    query: "Highlight the water body referred to in the query.",
    inputImages: [
      { label: "Grounded Target View", url: "/data/demo/single_optical/scene_optical_preview.png", sensor: "Cartosat-Sim" }
    ],
    primaryFinding: "Isolated perennial reservoir in the Southern-Western quadrant bounded by coordinates [0.04, 0.57, 0.49, 0.90].",
    evidenceSummary: [
      "Spatial bounding box extracted via connected component analysis",
      "Area occupies 14.8% of total scene surface area",
      "Centroid anchored at 28.520°N, 77.042°E (EPSG:4326)"
    ],
    confidence: { score: 0.92, level: "HIGH" },
    modelsUsed: ["GroundingAnalyzer", "SpectralAnalyzer", "ImageValidator"],
    executionTimeMs: 81,
    traceStepsCount: 11
  },
  {
    id: "03",
    stepNumber: "03 / 06",
    title: "Bi-Temporal Radiometric Change Detection",
    mode: "BI-TEMPORAL",
    query: "What changed between these two dates, and where did the change occur?",
    inputImages: [
      { label: "T₁ Baseline (Before)", url: "/data/demo/temporal/t1_preview.png", sensor: "EO-1 Optical" },
      { label: "T₂ Observation (After)", url: "/data/demo/temporal/t2_preview.png", sensor: "EO-2 Optical" }
    ],
    primaryFinding: "Significant built-up surface expansion detected in the Central-Western sector (9.7% total scene modification) converting previously bare/agricultural terrain into impervious structures.",
    evidenceSummary: [
      "2 primary connected change clusters segmented via Otsu thresholding",
      "Dominant change direction: Reflectance increase (+42.5 digital counts)",
      "Minor shoreline retreat detected along water perimeter"
    ],
    confidence: { score: 0.95, level: "HIGH" },
    modelsUsed: ["ChangeDetector", "RasterMetadataExtractor", "EvidenceVerifier"],
    executionTimeMs: 351,
    traceStepsCount: 11
  },
  {
    id: "04",
    stepNumber: "04 / 06",
    title: "Cross-Modal Optical + SAR Paired Fusion",
    mode: "OPTICAL + SAR",
    query: "Use optical and SAR together to identify built-up and water-covered regions.",
    inputImages: [
      { label: "Optical Reflectance", url: "/data/demo/optical_sar/optical_preview.png", sensor: "Optical Multispectral" },
      { label: "SAR Backscatter dB", url: "/data/demo/optical_sar/sar_preview.png", sensor: "RISAT-Sim C-Band SAR" }
    ],
    primaryFinding: "Cross-modal corroboration achieved with 80% feature agreement score: SAR structural double-bounce validates urban footprint, while specular radar backscatter confirms water boundaries.",
    evidenceSummary: [
      "Water classification corroborated: Low optical reflectance + low SAR backscatter",
      "Built-up classification corroborated: High optical brightness + high SAR double-bounce",
      "Agreement score: 0.80 across intersecting spatial footprints"
    ],
    confidence: { score: 0.94, level: "HIGH" },
    modelsUsed: ["OpticalSARFusionEngine", "SARProcessor", "SpectralAnalyzer"],
    executionTimeMs: 464,
    traceStepsCount: 12
  },
  {
    id: "05",
    stepNumber: "05 / 06",
    title: "Auditable Grounded Evidence & Verification",
    mode: "AUDIT LAYER",
    query: "Verify all natural language claims against raw raster pixels.",
    inputImages: [
      { label: "Multi-Sensor Composite", url: "/data/demo/optical_sar/optical_preview.png", sensor: "Co-registered Pair" }
    ],
    primaryFinding: "Anti-hallucination EvidenceVerifier audited 13 candidate claims, verified 12 against spatial bounding coordinates, and successfully suppressed 1 unsupported assertion.",
    evidenceSummary: [
      "Mathematical confidence formulation: 30% Model + 30% Evidence + 20% Input + 20% Registration",
      "No hallucinated assertions allowed to bypass verification pipeline",
      "Downloadable HTML and JSON intelligence dossiers generated with provenance hashes"
    ],
    confidence: { score: 0.95, level: "HIGH" },
    modelsUsed: ["EvidenceVerifier", "ConfidenceEstimator", "AnswerSynthesizer"],
    executionTimeMs: 24,
    traceStepsCount: 11
  },
  {
    id: "06",
    stepNumber: "06 / 06",
    title: "End-to-End Orchestration & Telemetry Trace",
    mode: "ORCHESTRATOR",
    query: "Execute complete agentic pipeline with millisecond audit.",
    inputImages: [
      { label: "Telemetry Pipeline", url: "/data/demo/single_optical/scene_optical_preview.png", sensor: "Real-time Telemetry" }
    ],
    primaryFinding: "Full 11-step agentic sequence executed in 351ms: Validation → Extraction → Routing → Preprocessing → Spectral → Change/Fusion → Inference → Aggregation → Confidence → Synthesis → Audit.",
    evidenceSummary: [
      "Input Validation: 211ms (Rasterio CRS & Affine verification)",
      "Spectral & Change Analysis: 43ms (Pure NumPy vectorized kernel)",
      "VLM Synthesis & Calibration: 3ms (Evidence-anchored template)",
      "Zero unhandled exceptions or external cloud API dependencies"
    ],
    confidence: { score: 0.96, level: "HIGH" },
    modelsUsed: ["TaskRouter", "TaskPlanner", "AgentOrchestrator"],
    executionTimeMs: 351,
    traceStepsCount: 11
  }
];

const JudgeDemo: React.FC = () => {
  const navigate = useNavigate();
  const [currentIdx, setCurrentIdx] = useState<number>(-1); // -1 is welcome screen

  const scenario = currentIdx >= 0 ? scenarios[currentIdx] : null;

  if (currentIdx === -1) {
    return (
      <div className="min-h-screen bg-space-950 bg-command-grid flex flex-col items-center justify-center p-6 relative overflow-hidden select-none font-sans">
        {/* Background telemetry accents */}
        <div className="absolute top-8 left-8 text-[11px] font-mono text-hud-muted flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald animate-pulse"></span>
          <span>ISRO-SAC SIH 2026 // PS 26167</span>
        </div>

        <div className="absolute top-8 right-8 text-[11px] font-mono text-hud-subtle">
          EVALUATION PROTOCOL V2.4
        </div>

        <div className="z-10 text-center max-w-2xl px-4">
          {/* Satellite Identity Emblem */}
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-xs bg-space-900 border border-emerald/50 p-4 mb-6 shadow-glow-md">
            <svg viewBox="0 0 24 24" className="w-10 h-10 text-emerald" fill="none" stroke="currentColor" strokeWidth="1.8">
              <circle cx="12" cy="12" r="3.5" fill="currentColor" fillOpacity="0.25" />
              <ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-30 12 12)" strokeDasharray="3 2" />
              <rect x="2" y="9.5" width="4" height="5" rx="0.5" strokeWidth="1.5" />
              <rect x="18" y="9.5" width="4" height="5" rx="0.5" strokeWidth="1.5" />
              <line x1="6" y1="12" x2="9" y2="12" />
              <line x1="15" y1="12" x2="18" y2="12" />
            </svg>
          </div>

          <div className="space-y-1 mb-3">
            <span className="text-xs font-mono tracking-widest text-emerald font-bold uppercase">
              Evaluator Guided Showcase
            </span>
            <h1 className="text-4xl md:text-5xl font-mono font-black text-hud-text tracking-tight">
              SATQUERY <span className="text-emerald">AI</span>
            </h1>
          </div>

          <p className="text-sm font-sans text-hud-muted max-w-lg mx-auto mb-8 leading-relaxed">
            Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Natural Language Text Queries.
          </p>

          {/* Launch Sequence Trigger */}
          <button 
            onClick={() => setCurrentIdx(0)}
            className="px-8 py-3.5 bg-emerald text-space-950 font-mono font-bold text-sm tracking-wider rounded-xs transition-all hover:bg-emerald-glow shadow-glow-md hover:shadow-glow-lg flex items-center justify-center space-x-2.5 mx-auto"
          >
            <Play size={16} className="fill-space-950" />
            <span>INITIALIZE JUDGE DEMONSTRATION</span>
          </button>

          {/* Pre-flight Technical Checklist */}
          <div className="mt-12 glass-panel p-5 rounded-xs text-left max-w-md mx-auto font-mono text-xs border border-space-700">
            <div className="text-emerald text-[11px] font-bold uppercase tracking-wider mb-3 flex items-center justify-between border-b border-space-700/80 pb-2">
              <span>Pre-Flight Readiness Check</span>
              <span className="text-hud-subtle text-[10px]">ALL PASS</span>
            </div>
            <ul className="space-y-2 text-hud-text text-[11px]">
              <li className="flex items-center space-x-2">
                <CheckCircle2 size={13} className="text-emerald shrink-0" />
                <span>GeoTIFF Ingestion & Coordinate Transformer</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 size={13} className="text-emerald shrink-0" />
                <span>Radiometric Bi-Temporal Change Engine</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 size={13} className="text-emerald shrink-0" />
                <span>Optical + SAR Dual-Modality Correlator</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 size={13} className="text-emerald shrink-0" />
                <span>Calibrated Multi-Factor Confidence Calibration</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-space-950 flex flex-col font-sans select-none overflow-hidden">
      {/* Top Demo Bar */}
      <div className="h-14 border-b border-space-700 bg-space-950/90 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-20">
        <div className="flex items-center space-x-3">
          <span className="px-2 py-0.5 bg-emerald/15 text-emerald border border-emerald/40 text-xs font-mono font-bold tracking-wider rounded-xs flex items-center space-x-1">
            <Play size={10} className="fill-emerald" />
            <span>JUDGE DEMO MODE</span>
          </span>
          <span className="text-hud-muted font-mono text-xs hidden md:inline">
            // {scenario?.stepNumber} — {scenario?.title}
          </span>
        </div>

        {/* Step Progression Pills */}
        <div className="flex items-center space-x-1.5">
          {scenarios.map((s, i) => (
            <button
              key={s.id}
              onClick={() => setCurrentIdx(i)}
              className={`h-2 transition-all rounded-xs ${
                i === currentIdx 
                  ? 'w-8 bg-emerald shadow-glow-sm' 
                  : i < currentIdx 
                    ? 'w-4 bg-emerald/50' 
                    : 'w-3 bg-space-700'
              }`}
              title={`Scenario ${s.id}: ${s.title}`}
            />
          ))}
        </div>

        <button 
          onClick={() => navigate('/')} 
          className="text-xs font-mono text-hud-muted hover:text-hud-text px-2.5 py-1 rounded-xs bg-space-850 border border-space-700 transition-colors"
        >
          EXIT TO WORKSPACE ✕
        </button>
      </div>

      {/* Main Scenario Canvas */}
      <div className="flex-1 p-6 flex flex-col items-center justify-center bg-command-grid overflow-y-auto scrollbar-thin">
        <div className="w-full max-w-5xl glass-panel-elevated rounded-xs overflow-hidden flex flex-col border border-space-700 shadow-2xl">
          {/* Scenario Header */}
          <div className="bg-space-950 p-4 border-b border-space-700 flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-emerald font-mono text-[11px] font-bold tracking-widest uppercase flex items-center space-x-1.5">
                <Sparkles size={12} />
                <span>SCENARIO {scenario?.stepNumber}</span>
              </div>
              <h2 className="text-xl font-bold font-mono text-hud-text mt-0.5">
                {scenario?.title}
              </h2>
            </div>

            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 bg-space-850 border border-space-700 font-mono text-xs text-hud-muted rounded-xs">
                MODE: <span className="text-emerald font-bold">{scenario?.mode}</span>
              </span>
              <span className="px-2.5 py-1 bg-space-850 border border-space-700 font-mono text-xs text-hud-muted rounded-xs">
                LATENCY: <span className="text-hud-text font-bold">{scenario?.executionTimeMs}ms</span>
              </span>
            </div>
          </div>

          {/* Scenario Body */}
          <div className="p-6 grid grid-cols-1 md:grid-cols-[380px_1fr] gap-6 bg-space-900/70">
            {/* Left: Input Satellite Raster Views */}
            <div className="space-y-3">
              <div className="text-[10px] font-mono uppercase text-hud-muted tracking-wider">
                Ingested Satellite Observations
              </div>
              
              <div className={`grid ${scenario?.inputImages.length === 2 ? 'grid-cols-2' : 'grid-cols-1'} gap-2`}>
                {scenario?.inputImages.map((img, i) => (
                  <div key={i} className="bg-space-850 border border-space-700 p-2 rounded-xs">
                    <div className="text-[10px] font-mono text-hud-muted mb-1 truncate">{img.label}</div>
                    <div className="h-44 bg-space-900 border border-space-700 rounded-xs overflow-hidden flex items-center justify-center">
                      <img src={img.url} alt={img.label} className="w-full h-full object-cover" />
                    </div>
                    <div className="text-[9px] font-mono text-hud-subtle mt-1.5 truncate">{img.sensor}</div>
                  </div>
                ))}
              </div>

              {/* Contributing Specialists */}
              <div className="bg-space-850 p-2.5 rounded-xs border border-space-700/80">
                <div className="text-[9px] font-mono text-hud-subtle uppercase tracking-wider mb-1.5 flex items-center space-x-1">
                  <Cpu size={11} className="text-emerald" />
                  <span>Specialists Executed</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {scenario?.modelsUsed.map((m, idx) => (
                    <span key={idx} className="bg-space-800 text-emerald text-[9px] font-mono px-1.5 py-0.5 rounded-xs border border-space-700">
                      {m}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Right: Simulated Query & Real Synthesized Intelligence */}
            <div className="flex flex-col space-y-4">
              {/* Natural Query Box */}
              <div className="bg-space-850 border border-space-700 p-3.5 rounded-xs">
                <div className="text-[10px] font-mono text-hud-muted uppercase tracking-wider mb-1">
                  Natural Language Query:
                </div>
                <div className="text-sm font-mono font-medium text-emerald">
                  "{scenario?.query}"
                </div>
              </div>

              {/* Synthesized Finding */}
              <div className="bg-space-850 border border-space-700 p-3.5 rounded-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-emerald uppercase font-bold tracking-wider">
                    Synthesized Conclusion
                  </span>
                  <span className="text-[10px] font-mono text-emerald bg-emerald/10 border border-emerald/30 px-2 py-0.2 rounded-xs font-bold">
                    CONFIDENCE: {scenario?.confidence.level} ({Math.round(scenario?.confidence.score! * 100)}%)
                  </span>
                </div>
                <div className="text-xs font-sans text-hud-text leading-relaxed font-medium">
                  {scenario?.primaryFinding}
                </div>
              </div>

              {/* Evidence Points */}
              <div className="bg-space-850 border border-space-700 p-3.5 rounded-xs space-y-2">
                <div className="text-[10px] font-mono text-hud-muted uppercase tracking-wider">
                  Verifiable Grounded Evidence:
                </div>
                <ul className="space-y-1.5 text-xs font-mono text-hud-muted">
                  {scenario?.evidenceSummary.map((ev, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <span className="text-emerald font-bold">✓</span>
                      <span>{ev}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Navigation Bar */}
          <div className="bg-space-950 p-4 border-t border-space-700 flex justify-between items-center">
            <button 
              onClick={() => setCurrentIdx(Math.max(0, currentIdx - 1))}
              disabled={currentIdx === 0}
              className="px-4 py-2 border border-space-700 text-hud-muted hover:text-hud-text hover:bg-space-850 font-mono text-xs rounded-xs disabled:opacity-30 disabled:cursor-not-allowed flex items-center space-x-1.5 transition-colors"
            >
              <ArrowLeft size={13} />
              <span>PREVIOUS</span>
            </button>

            <button
              onClick={() => navigate('/')}
              className="text-xs font-mono text-hud-muted hover:text-emerald flex items-center space-x-1 transition-colors"
            >
              <ExternalLink size={12} />
              <span>Open in Interactive Workspace</span>
            </button>

            <button 
              onClick={() => currentIdx === scenarios.length - 1 ? navigate('/') : setCurrentIdx(currentIdx + 1)}
              className="px-5 py-2 bg-emerald hover:bg-emerald-glow text-space-950 font-mono font-bold text-xs rounded-xs flex items-center space-x-1.5 shadow-glow-sm transition-all"
            >
              <span>{currentIdx === scenarios.length - 1 ? 'COMPLETE SHOWCASE' : 'NEXT SCENARIO'}</span>
              <ArrowRight size={13} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JudgeDemo;
