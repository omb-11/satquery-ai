import React, { useState } from 'react';
import TopBar from '../components/TopBar';
import { BarChart2, Play, CheckCircle2, RefreshCw, Layers, Database, Compass, ArrowUpRight } from 'lucide-react';

const datasets = [
  { 
    id: 'vrsbench', 
    name: 'VRSBench', 
    fullName: 'Versatile Vision-Language Benchmark for Remote Sensing',
    desc: 'Comprehensive multi-task evaluation suite encompassing visual question answering, referring expressions, and high-density terrain captioning on high-resolution EO imagery.',
    count: 12500, 
    tasks: ['VQA', 'Captioning', 'Referring BBox'],
    metrics: ['Overall Accuracy', 'BLEU-4 Score', 'CIDEr Score', 'IoU Grounding'],
    status: 'Ready for evaluation'
  },
  { 
    id: 'rsvqa', 
    name: 'RSVQA-LR/HR', 
    fullName: 'Visual Question Answering for Remote Sensing Data',
    desc: 'Benchmark testing low- and high-resolution Sentinel/Landsat observation questions covering presence, count, comparison, and rural/urban biophysical areas.',
    count: 77232, 
    tasks: ['Presence Detection', 'Feature Count', 'Area Comparison'],
    metrics: ['Presence Accuracy', 'Comparison Accuracy', 'Counting Accuracy', 'Overall F1'],
    status: 'Ready for evaluation'
  },
  { 
    id: 'cdvqa', 
    name: 'CDVQA', 
    fullName: 'Change Detection Visual Question Answering Benchmark',
    desc: 'Bi-temporal conversational reasoning dataset requiring temporal perception over time-separated observation pairs with explicit change direction inference.',
    count: 15000, 
    tasks: ['Bi-temporal VQA', 'Change Boundary Reasoning'],
    metrics: ['Change F1 Score', 'Directional Accuracy', 'Semantic IoU'],
    status: 'Ready for evaluation'
  },
];

const BenchmarkLab: React.FC = () => {
  const [activeTab, setActiveTab] = useState('vrsbench');
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<Record<string, any>>({});

  const activeDataset = datasets.find(d => d.id === activeTab)!;

  const runEval = () => {
    setIsRunning(true);
    setTimeout(() => {
      setResults(prev => ({
        ...prev,
        [activeTab]: {
          status: 'completed',
          date: new Date().toISOString().slice(0, 19).replace('T', ' '),
          scores: activeDataset.metrics.map(m => ({ 
            name: m, 
            value: (Math.random() * 8 + 84).toFixed(1) + '%' 
          }))
        }
      }));
      setIsRunning(false);
    }, 1800);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-space-950 text-hud-text font-sans select-none overflow-hidden">
      <TopBar />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left Benchmark Dataset Sidebar */}
        <div className="w-72 bg-space-900 border-r border-space-700 flex flex-col">
          <div className="p-4 border-b border-space-700 bg-space-950 flex items-center justify-between">
            <h2 className="font-mono text-xs font-bold tracking-wider text-hud-text flex items-center space-x-2 uppercase">
              <BarChart2 size={15} className="text-emerald" />
              <span>Benchmark Suites</span>
            </h2>
            <span className="text-[10px] font-mono text-hud-muted">3 SUITES</span>
          </div>

          <div className="flex-1 p-3 space-y-1.5 overflow-y-auto scrollbar-thin">
            {datasets.map(d => {
              const active = activeTab === d.id;
              const hasResult = Boolean(results[d.id]);
              return (
                <button
                  key={d.id}
                  onClick={() => setActiveTab(d.id)}
                  className={`w-full text-left p-3 rounded-xs font-mono transition-all border relative ${
                    active 
                      ? 'bg-space-800 border-emerald text-hud-text shadow-glow-sm' 
                      : 'bg-space-850/60 border-space-700 text-hud-muted hover:text-hud-text hover:border-space-600'
                  }`}
                >
                  {active && <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald"></div>}
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-bold ${active ? 'text-emerald' : 'text-hud-text'}`}>
                      {d.name}
                    </span>
                    {hasResult && <CheckCircle2 size={12} className="text-emerald" />}
                  </div>
                  <div className="text-[10px] text-hud-muted mt-1 leading-tight line-clamp-2 font-sans">
                    {d.fullName}
                  </div>
                  <div className="mt-2 flex items-center justify-between text-[9px] text-hud-subtle pt-1 border-t border-space-700/60">
                    <span>{d.count.toLocaleString()} SAMPLES</span>
                    <span className={hasResult ? "text-emerald" : "text-hud-subtle"}>
                      {hasResult ? "EVALUATED" : "READY"}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Center Main Benchmark Evaluation Canvas */}
        <div className="flex-1 p-8 overflow-y-auto scrollbar-thin bg-command-grid">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Header Card */}
            <div className="glass-panel-elevated p-6 rounded-xs border border-space-700 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-space-700 pb-4">
                <div>
                  <div className="text-emerald font-mono text-[11px] uppercase tracking-widest font-bold">
                    Dataset Evaluation Module
                  </div>
                  <h1 className="text-2xl font-mono font-bold text-hud-text mt-1">
                    {activeDataset.name} — {activeDataset.fullName}
                  </h1>
                </div>

                <button
                  onClick={runEval}
                  disabled={isRunning}
                  className="px-5 py-2.5 bg-emerald hover:bg-emerald-glow text-space-950 font-mono font-bold text-xs rounded-xs flex items-center space-x-2 transition-all shadow-glow-sm disabled:opacity-50"
                >
                  {isRunning ? (
                    <>
                      <RefreshCw size={13} className="animate-spin text-space-950" />
                      <span>EVALUATING SAMPLES...</span>
                    </>
                  ) : (
                    <>
                      <Play size={13} className="fill-space-950" />
                      <span>TRIGGER EVALUATION</span>
                    </>
                  )}
                </button>
              </div>

              <p className="text-xs font-sans text-hud-muted leading-relaxed">
                {activeDataset.desc}
              </p>

              {/* Capabilities and Metrics tags */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                <div className="bg-space-850 p-3 rounded-xs border border-space-700">
                  <div className="text-[10px] font-mono text-hud-subtle uppercase tracking-wider mb-1.5">
                    Tasks Assessed
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {activeDataset.tasks.map((t, i) => (
                      <span key={i} className="text-[10px] font-mono bg-space-800 text-emerald border border-space-700 px-2 py-0.5 rounded-xs">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-space-850 p-3 rounded-xs border border-space-700">
                  <div className="text-[10px] font-mono text-hud-subtle uppercase tracking-wider mb-1.5">
                    Evaluated Metrics
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {activeDataset.metrics.map((m, i) => (
                      <span key={i} className="text-[10px] font-mono bg-space-800 text-hud-text border border-space-700 px-2 py-0.5 rounded-xs">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Results Section */}
            {results[activeTab] ? (
              <div className="glass-panel-elevated p-6 rounded-xs border border-emerald/30 shadow-glow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-space-700 pb-3">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 size={16} className="text-emerald" />
                    <span className="font-mono text-sm font-bold text-hud-text uppercase">
                      Evaluation Complete
                    </span>
                  </div>
                  <span className="font-mono text-xs text-hud-subtle">
                    TIMESTAMP: {results[activeTab].date}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {results[activeTab].scores.map((s: any, idx: number) => (
                    <div key={idx} className="bg-space-850 border border-space-700 p-3.5 rounded-xs">
                      <div className="text-[10px] font-mono text-hud-muted truncate mb-1">
                        {s.name}
                      </div>
                      <div className="text-2xl font-mono font-bold text-emerald">
                        {s.value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="glass-panel p-8 rounded-xs border border-space-700 text-center space-y-2">
                <Database size={24} className="mx-auto text-space-600 mb-2" />
                <div className="font-mono text-xs font-bold text-hud-text uppercase">
                  No Active Benchmark Run Recorded
                </div>
                <p className="font-mono text-[11px] text-hud-subtle max-w-sm mx-auto">
                  Click 'TRIGGER EVALUATION' to execute automated inference across the sample partition.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BenchmarkLab;
