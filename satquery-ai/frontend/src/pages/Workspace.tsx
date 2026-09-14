import React, { useState } from 'react';
import TopBar from '../components/TopBar';
import InputPanel from '../components/InputPanel';
import ImageViewer from '../components/ImageViewer';
import QueryPanel from '../components/QueryPanel';
import ResultPanel from '../components/ResultPanel';
import AnalyticsShelf from '../components/AnalyticsShelf';
import { UploadedFile, AnalysisResult, TraceStep } from '../lib/types';
import { analyzeStream, analyzeImages } from '../lib/api';
import { 
  ChevronLeft, ChevronRight, PanelLeftClose, PanelLeftOpen,
  PanelRightClose, PanelRightOpen, Layers, MessageSquareCode, ShieldCheck
} from 'lucide-react';

const Workspace: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [mode, setMode] = useState<string>('SINGLE IMAGE');
  const [precisionMode, setPrecisionMode] = useState<string>('balanced');
  const [externalQuery, setExternalQuery] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [traceSteps, setTraceSteps] = useState<TraceStep[]>([]);
  const [focusedRegion, setFocusedRegion] = useState<number[] | null>(null);

  // Responsive Drawer/Panel Collapse States for Hero Imagery Viewport
  const [leftCollapsed, setLeftCollapsed] = useState<boolean>(false);
  const [rightCollapsed, setRightCollapsed] = useState<boolean>(false);

  // Map human-readable mode to backend input_mode
  const getBackendInputMode = (m: string) => {
    switch (m) {
      case 'BI-TEMPORAL': return 'bitemporal';
      case 'OPTICAL + SAR': return 'optical_sar';
      default: return 'single';
    }
  };

  // Instant demo scene loader for one-click judge demonstrations
  const handleLoadDemo = (demoKey: string) => {
    setResult(null);
    setTraceSteps([]);

    if (demoKey === 'single_optical') {
      setMode('SINGLE IMAGE');
      setFiles([{
        file_id: 'demo_opt_001',
        filename: 'scene_optical.tif',
        modality: 'Optical',
        has_crs: true,
        width: 256,
        height: 256,
        preview_url: '/data/demo/single_optical/scene_optical_preview.png',
        validation: true,
      }]);
    } else if (demoKey === 'single_sar') {
      setMode('SINGLE IMAGE');
      setFiles([{
        file_id: 'demo_sar_001',
        filename: 'scene_sar.tif',
        modality: 'SAR',
        has_crs: true,
        width: 256,
        height: 256,
        preview_url: '/data/demo/single_sar/scene_sar_preview.png',
        validation: true,
      }]);
    } else if (demoKey === 'temporal') {
      setMode('BI-TEMPORAL');
      setFiles([
        {
          file_id: 'demo_t1_001',
          filename: 't1_before.tif',
          modality: 'Optical (T₁)',
          has_crs: true,
          width: 256,
          height: 256,
          preview_url: '/data/demo/temporal/t1_preview.png',
          validation: true,
        },
        {
          file_id: 'demo_t2_001',
          filename: 't2_after.tif',
          modality: 'Optical (T₂)',
          has_crs: true,
          width: 256,
          height: 256,
          preview_url: '/data/demo/temporal/t2_preview.png',
          validation: true,
        }
      ]);
    } else if (demoKey === 'optical_sar') {
      setMode('OPTICAL + SAR');
      setFiles([
        {
          file_id: 'demo_opt_002',
          filename: 'optical.tif',
          modality: 'Optical',
          has_crs: true,
          width: 256,
          height: 256,
          preview_url: '/data/demo/optical_sar/optical_preview.png',
          validation: true,
        },
        {
          file_id: 'demo_sar_002',
          filename: 'sar.tif',
          modality: 'SAR',
          has_crs: true,
          width: 256,
          height: 256,
          preview_url: '/data/demo/optical_sar/sar_preview.png',
          validation: true,
        }
      ]);
    }
  };

  const handleAnalyze = async (query: string) => {
    if (files.length === 0) {
      alert("Please upload imagery or click an ISRO demo preset first.");
      return;
    }
    
    setIsAnalyzing(true);
    setResult(null);
    setTraceSteps([]);
    setFocusedRegion(null);

    const inputMode = getBackendInputMode(mode);
    const fileIds = files.map(f => f.file_id);
    const params = { precision_mode: precisionMode };

    // Stream live execution trace via SSE
    try {
      await analyzeStream(
        query,
        fileIds,
        inputMode,
        (stepData: TraceStep) => {
          setTraceSteps(prev => {
            const exists = prev.find(s => s.step_num === stepData.step_num);
            if (exists) {
              return prev.map(s => s.step_num === stepData.step_num ? stepData : s);
            }
            return [...prev, stepData];
          });
        },
        (finalResult: AnalysisResult) => {
          setResult(finalResult);
          setIsAnalyzing(false);
        },
        async (error: any) => {
          console.warn("SSE stream interrupted, falling back to sync analyze API:", error);
          try {
            const res = await analyzeImages(query, fileIds, inputMode, params);
            setResult(res);
            if (res.trace && res.trace.length > 0) {
              setTraceSteps(res.trace);
            }
          } catch (syncErr) {
            console.error("Analysis execution failed:", syncErr);
            // Graceful error state with real metadata
            setResult({
              run_id: 'ERR-' + Date.now(),
              task_type: 'ANALYSIS_ERROR',
              answer: 'Analysis interrupted: Could not complete inference pipeline on provided files.',
              findings: String(syncErr),
              evidence: [],
              confidence: { score: 0.2, level: 'Low', factors: ['Execution error'], limitations: ['Check file format and CRS compatibility.'] },
              models_used: ['ImageValidator'],
              parameters: {},
              limitations: ['Network or compute engine timeout. Ensure backend service is running on port 8000.'],
              trace: [],
              processing_times: {}
            });
          } finally {
            setIsAnalyzing(false);
          }
        },
        params
      );
    } catch (e) {
      console.error("Dispatch error:", e);
      setIsAnalyzing(false);
    }
  };

  const handleFocusRegion = (region: number[]) => {
    setFocusedRegion(region);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-space-950 text-hud-text overflow-hidden font-sans select-none">
      {/* Premium Mission Header */}
      <TopBar />
      
      {/* Dynamic 3-Column Command Grid Layout (Visualization occupies 65-75% standard, up to 90%+ when sidebars are collapsed) */}
      <div 
        className="flex-1 grid h-[calc(100vh-3.5rem)] relative overflow-hidden transition-all duration-200"
        style={{
          gridTemplateColumns: `${leftCollapsed ? '44px' : '265px'} 1fr ${rightCollapsed ? '44px' : '340px'}`
        }}
      >
        {/* Left: Mission Input & Mode Selection (or Collapsed Dock) */}
        {leftCollapsed ? (
          <div className="h-full bg-space-950 border-r border-space-700 flex flex-col items-center py-3 space-y-4 select-none">
            <button
              onClick={() => setLeftCollapsed(false)}
              className="p-1.5 text-hud-muted hover:text-emerald hover:bg-space-850 rounded-xs transition-colors"
              title="Expand Input Dock"
            >
              <PanelLeftOpen size={16} />
            </button>
            <div className="w-6 h-px bg-space-700"></div>
            <div className="flex flex-col items-center space-y-2">
              <span className="text-[10px] font-mono text-emerald font-bold [writing-mode:vertical-lr] rotate-180 uppercase tracking-widest">
                INPUTS ({files.length})
              </span>
              <Layers size={14} className="text-hud-subtle" />
            </div>
          </div>
        ) : (
          <div className="relative h-full flex flex-col overflow-hidden">
            {/* Collapse button on left panel */}
            <button
              onClick={() => setLeftCollapsed(true)}
              className="absolute top-2 right-2 z-30 p-1 text-hud-muted hover:text-emerald hover:bg-space-850 rounded-xs transition-colors"
              title="Collapse Input Dock"
            >
              <PanelLeftClose size={14} />
            </button>
            <InputPanel 
              files={files} 
              setFiles={setFiles} 
              mode={mode} 
              setMode={setMode} 
              precisionMode={precisionMode}
              setPrecisionMode={setPrecisionMode}
              onLoadDemo={handleLoadDemo}
            />
          </div>
        )}
        
        {/* Center: Hero Imagery Viewport + Expandable Bottom Analytics Shelf */}
        <div className="relative flex flex-col h-full bg-space-950 border-r border-space-700 overflow-hidden">
          {/* Main Visualizer Canvas */}
          <div className="flex-1 relative overflow-hidden">
            <ImageViewer 
              files={files} 
              mode={mode} 
              focusedRegion={focusedRegion}
              evidenceItems={result?.evidence || []}
              onAskAboutRegion={(q) => setExternalQuery(q)}
            />
          </div>

          {/* Integrated Expandable Analytics & Trace Shelf */}
          <AnalyticsShelf
            files={files}
            mode={mode}
            result={result}
            traceSteps={traceSteps}
            onFocusRegion={handleFocusRegion}
            onAskAboutRegion={(q) => setExternalQuery(q)}
          />
        </div>
        
        {/* Right: Command Input & Intelligence Briefing Panel (or Collapsed Dock) */}
        {rightCollapsed ? (
          <div className="h-full bg-space-950 border-l border-space-700 flex flex-col items-center py-3 space-y-4 select-none">
            <button
              onClick={() => setRightCollapsed(false)}
              className="p-1.5 text-hud-muted hover:text-emerald hover:bg-space-850 rounded-xs transition-colors"
              title="Expand Intelligence Panel"
            >
              <PanelRightOpen size={16} />
            </button>
            <div className="w-6 h-px bg-space-700"></div>
            <div className="flex flex-col items-center space-y-2">
              <span className="text-[10px] font-mono text-emerald font-bold [writing-mode:vertical-lr] rotate-180 uppercase tracking-widest">
                INTEL BRIEFING
              </span>
              <ShieldCheck size={14} className="text-emerald" />
            </div>
          </div>
        ) : (
          <div className="relative h-full flex flex-col bg-space-900 overflow-hidden">
            {/* Collapse button on right panel */}
            <button
              onClick={() => setRightCollapsed(true)}
              className="absolute top-2 right-2 z-30 p-1 text-hud-muted hover:text-emerald hover:bg-space-850 rounded-xs transition-colors"
              title="Collapse Intelligence Panel"
            >
              <PanelRightClose size={14} />
            </button>
            <QueryPanel 
              mode={mode} 
              isAnalyzing={isAnalyzing} 
              onAnalyze={handleAnalyze} 
              externalQuery={externalQuery}
              followUpQuestions={result?.follow_up_questions || []}
            />
            <ResultPanel 
              result={result} 
              onFocusRegion={handleFocusRegion}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Workspace;
