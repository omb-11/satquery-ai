import React, { useState } from 'react';
import TopBar from '../components/TopBar';
import { Sliders, Cpu, Database, Play, AlertTriangle, CheckCircle2, RefreshCw, Terminal, Layers } from 'lucide-react';

const ModelAdaptation: React.FC = () => {
  const [method, setMethod] = useState<'projection_head' | 'lora'>('projection_head');
  const [epochs, setEpochs] = useState<number>(3);
  const [learningRate, setLearningRate] = useState<string>('0.0001');
  const [batchSize, setBatchSize] = useState<number>(4);
  const [isTraining, setIsTraining] = useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([
    "[00:00:01] System Standby: BigEarthNet-S2 and BigEarthNet-S1 pairing ready.",
    "[00:00:02] Projection head architecture: Linear(512->256) -> GELU -> LayerNorm -> Linear(256->128).",
    "[00:00:03] Standby: Awaiting user training command dispatch."
  ]);
  const [adapterStatus, setAdapterStatus] = useState<'not_installed' | 'training' | 'ready'>('not_installed');

  const handleStartTraining = () => {
    setIsTraining(true);
    setAdapterStatus('training');
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Initializing training job — Method: ${method}, Epochs: ${epochs}, LR: ${learningRate}, Device: CPU`]);

    let step = 1;
    const interval = setInterval(() => {
      if (step <= epochs) {
        const loss = (0.42 - (step * 0.08) + Math.random() * 0.02).toFixed(4);
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Epoch ${step}/${epochs} — Loss: ${loss} — RS Embeddings alignment: ${(70 + step * 8)}%`]);
        step++;
      } else {
        clearInterval(interval);
        setIsTraining(false);
        setAdapterStatus('ready');
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ✓ Training complete. Adapter saved to adapters/rs_adapter_${method}.pt. Ready for inference.`]);
      }
    }, 1200);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-space-950 text-hud-text font-sans select-none overflow-hidden">
      <TopBar />
      
      <div className="flex-1 p-8 overflow-y-auto scrollbar-thin bg-command-grid">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-space-700 pb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xs bg-space-900 border border-emerald/40 flex items-center justify-center text-emerald shadow-glow-sm">
                <Sliders size={20} />
              </div>
              <div>
                <div className="text-[10px] font-mono text-emerald uppercase tracking-widest font-bold">
                  Domain Adaptation Center
                </div>
                <h1 className="text-2xl font-mono font-bold text-hud-text mt-0.5">
                  BigEarthNet.txt Remote Sensing Fine-Tuning
                </h1>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <span className={`px-2.5 py-1 text-xs font-mono font-bold border rounded-xs ${
                adapterStatus === 'ready' 
                  ? 'bg-emerald/15 text-emerald border-emerald shadow-glow-sm' 
                  : adapterStatus === 'training'
                    ? 'bg-telemetry-amber/15 text-telemetry-amber border-telemetry-amber animate-pulse'
                    : 'bg-space-850 text-hud-muted border-space-700'
              }`}>
                STATUS: {adapterStatus.toUpperCase().replace('_', ' ')}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Training Form */}
            <div className="lg:col-span-2 glass-panel-elevated p-6 rounded-xs border border-space-700 space-y-5">
              <div className="flex items-center justify-between border-b border-space-700 pb-3">
                <span className="font-mono text-xs font-bold text-emerald uppercase tracking-wider">
                  Hyperparameter Configuration
                </span>
                <span className="text-[10px] font-mono text-hud-subtle">CPU / LIGHTWEIGHT OPTIMIZED</span>
              </div>
              
              <div className="space-y-4 font-mono text-xs">
                <div>
                  <label className="block text-[10px] text-hud-muted uppercase tracking-wider mb-1.5">
                    Target Training Dataset
                  </label>
                  <select 
                    disabled={isTraining}
                    className="w-full bg-space-850 border border-space-700 p-2.5 text-xs text-hud-text rounded-xs focus:border-emerald focus:outline-none"
                  >
                    <option>BigEarthNet.txt (Sentinel-1 SAR + Sentinel-2 Optical Pairs)</option>
                    <option>SpaceNet 8 (Multi-Temporal Flood & Road Detection)</option>
                    <option>VRSBench Paired Captions & Referring Expressions</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] text-hud-muted uppercase tracking-wider mb-1.5">
                      Adaptation Architecture
                    </label>
                    <div className="flex space-x-2">
                      <button 
                        onClick={() => setMethod('projection_head')}
                        disabled={isTraining}
                        className={`flex-1 py-2 text-xs font-mono border rounded-xs transition-colors ${
                          method === 'projection_head' 
                            ? 'bg-emerald/15 border-emerald text-emerald font-bold shadow-glow-sm' 
                            : 'border-space-700 text-hud-muted hover:bg-space-800'
                        }`}
                      >
                        Projection Head
                      </button>
                      <button 
                        onClick={() => setMethod('lora')}
                        disabled={isTraining}
                        className={`flex-1 py-2 text-xs font-mono border rounded-xs transition-colors ${
                          method === 'lora' 
                            ? 'bg-emerald/15 border-emerald text-emerald font-bold shadow-glow-sm' 
                            : 'border-space-700 text-hud-muted hover:bg-space-800'
                        }`}
                      >
                        LoRA Rank-8
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-[10px] text-hud-muted uppercase tracking-wider mb-1.5">
                      Training Epochs
                    </label>
                    <input 
                      type="number" 
                      min={1} 
                      max={20}
                      value={epochs} 
                      onChange={e => setEpochs(Number(e.target.value))} 
                      disabled={isTraining}
                      className="w-full bg-space-850 border border-space-700 p-2 text-xs text-hud-text rounded-xs focus:border-emerald focus:outline-none" 
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] text-hud-muted uppercase tracking-wider mb-1.5">
                      Learning Rate
                    </label>
                    <input 
                      type="text" 
                      value={learningRate} 
                      onChange={e => setLearningRate(e.target.value)} 
                      disabled={isTraining}
                      className="w-full bg-space-850 border border-space-700 p-2 text-xs text-hud-text rounded-xs focus:border-emerald focus:outline-none" 
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] text-hud-muted uppercase tracking-wider mb-1.5">
                      Batch Size
                    </label>
                    <input 
                      type="number" 
                      min={1} 
                      max={32}
                      value={batchSize} 
                      onChange={e => setBatchSize(Number(e.target.value))} 
                      disabled={isTraining}
                      className="w-full bg-space-850 border border-space-700 p-2 text-xs text-hud-text rounded-xs focus:border-emerald focus:outline-none" 
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-space-700 flex space-x-3">
                  <button 
                    disabled={isTraining}
                    className="px-5 py-2.5 border border-space-700 hover:border-space-600 text-hud-muted hover:text-hud-text font-mono text-xs rounded-xs transition-colors"
                  >
                    PREPARE PAIRS
                  </button>
                  <button 
                    onClick={handleStartTraining}
                    disabled={isTraining}
                    className="flex-1 bg-emerald hover:bg-emerald-glow text-space-950 font-bold font-mono text-xs rounded-xs flex items-center justify-center space-x-2 transition-all shadow-glow-sm disabled:opacity-50"
                  >
                    {isTraining ? (
                      <>
                        <RefreshCw size={13} className="animate-spin text-space-950" />
                        <span>TRAINING ADAPTER IN PROGRESS...</span>
                      </>
                    ) : (
                      <>
                        <Play size={13} className="fill-space-950" />
                        <span>DISPATCH TRAINING JOB</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Model Card & Telemetry Logs */}
            <div className="space-y-6">
              {/* Architecture Card */}
              <div className="glass-panel p-5 rounded-xs border border-space-700 space-y-3 font-mono text-xs">
                <div className="flex items-center space-x-2 text-emerald font-bold uppercase text-[11px]">
                  <Layers size={14} />
                  <span>Adapter Target Specification</span>
                </div>
                <div className="bg-space-850 p-3 rounded-xs border border-space-700 space-y-1.5 text-[11px]">
                  <div className="flex justify-between"><span className="text-hud-muted">Input Features:</span><span className="text-hud-text">512-dim (CLIP/ViT)</span></div>
                  <div className="flex justify-between"><span className="text-hud-muted">Hidden Projection:</span><span className="text-hud-text">256-dim GELU</span></div>
                  <div className="flex justify-between"><span className="text-hud-muted">Output RS Space:</span><span className="text-emerald">128-dim Multi-modal</span></div>
                  <div className="flex justify-between"><span className="text-hud-muted">Parameters:</span><span className="text-hud-text">164,224 (0.16M)</span></div>
                  <div className="flex justify-between"><span className="text-hud-muted">Compute Footprint:</span><span className="text-hud-text">~45MB RAM</span></div>
                </div>
              </div>

              {/* Live Terminal Log Viewer */}
              <div className="glass-panel-elevated p-4 rounded-xs border border-space-700 space-y-2">
                <div className="flex items-center justify-between text-[10px] font-mono text-hud-muted border-b border-space-700 pb-1.5">
                  <span className="flex items-center space-x-1 text-emerald font-bold">
                    <Terminal size={11} />
                    <span>TRAINING STDOUT</span>
                  </span>
                  <span className="text-hud-subtle">{logs.length} LINES</span>
                </div>

                <div className="h-44 bg-space-950 border border-space-700 p-2.5 rounded-xs font-mono text-[10px] text-hud-muted overflow-y-auto scrollbar-thin space-y-1">
                  {logs.map((line, idx) => (
                    <div key={idx} className={line.includes('✓') ? 'text-emerald font-bold' : line.includes('Loss:') ? 'text-hud-text' : 'text-hud-muted'}>
                      {line}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelAdaptation;
