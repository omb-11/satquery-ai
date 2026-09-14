import React, { useEffect, useRef } from 'react';
import { TraceStep } from '../lib/types';
import { Check, Loader2, XCircle, Terminal, ChevronDown, ChevronUp, Clock, Activity } from 'lucide-react';

interface ExecutionTraceProps {
  steps: TraceStep[];
  isExpanded: boolean;
  setIsExpanded: (val: boolean) => void;
}

const ExecutionTrace: React.FC<ExecutionTraceProps> = ({ steps, isExpanded, setIsExpanded }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && isExpanded) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [steps, isExpanded]);

  if (steps.length === 0) return null;

  const totalElapsed = steps.reduce((acc, s) => acc + (s.elapsed_ms || 0), 0);

  return (
    <div className="absolute bottom-0 left-0 right-0 glass-panel-elevated border-t border-space-700 select-none z-30">
      {/* Trace Drawer Header */}
      <div 
        className="flex items-center justify-between px-4 py-2 border-b border-space-700/80 cursor-pointer hover:bg-space-850/60 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3 text-xs font-mono text-hud-text">
          <div className="flex items-center space-x-1.5 text-emerald font-bold uppercase tracking-wider">
            <Activity size={13} className="animate-pulse text-emerald" />
            <span>AGENT ORCHESTRATION TRACE</span>
          </div>

          <div className="h-3 w-px bg-space-700"></div>

          <span className="bg-space-800 border border-space-700 px-2 py-0.5 rounded-xs text-[10px] text-emerald font-mono">
            {steps.length} STEPS
          </span>

          <div className="hidden sm:flex items-center space-x-1 text-[10px] text-hud-muted">
            <Clock size={11} className="text-hud-subtle" />
            <span>LATENCY: {Math.round(totalElapsed)}ms</span>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-hud-muted">
          <span className="text-[10px] font-mono text-hud-subtle hidden sm:inline">
            {isExpanded ? 'COLLAPSE' : 'EXPAND TIMELINE'}
          </span>
          <button className="text-hud-muted hover:text-hud-text">
            {isExpanded ? <ChevronDown size={15} /> : <ChevronUp size={15} />}
          </button>
        </div>
      </div>

      {/* Vertical Timeline Drawer */}
      {isExpanded && (
        <div 
          ref={containerRef} 
          className="max-h-56 overflow-y-auto scrollbar-thin p-4 font-mono text-xs space-y-3 bg-space-950/90"
        >
          <div className="relative pl-6 space-y-3 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-px before:bg-space-700">
            {steps.map((step, idx) => {
              const isRunning = step.status === 'running';
              const isDone = step.status === 'success' || (step.status as string) === 'done';
              const isError = step.status === 'error';

              return (
                <div key={idx} className="relative flex items-start space-x-3 group">
                  {/* Timeline Dot */}
                  <div className={`absolute -left-6 mt-1 w-4 h-4 rounded-full flex items-center justify-center border text-[9px] ${
                    isRunning 
                      ? 'bg-space-900 border-emerald text-emerald animate-pulse shadow-glow-sm' 
                      : isDone 
                        ? 'bg-space-900 border-emerald/80 text-emerald' 
                        : isError 
                          ? 'bg-space-900 border-telemetry-red text-telemetry-red' 
                          : 'bg-space-900 border-space-700 text-hud-subtle'
                  }`}>
                    {isRunning && <Loader2 size={10} className="animate-spin" />}
                    {isDone && <Check size={10} strokeWidth={3} />}
                    {isError && <XCircle size={10} />}
                  </div>

                  {/* Step Content */}
                  <div className="flex-1 bg-space-850/60 border border-space-700/80 hover:border-space-600 p-2 rounded-xs transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-baseline space-x-2">
                        <span className="text-hud-subtle text-[10px]">
                          #{step.step_num.toString().padStart(2, '0')}
                        </span>
                        <span className="text-emerald font-bold text-xs tracking-wider">
                          {step.tool}
                        </span>
                        <span className="text-hud-muted text-[11px]">
                          — {step.name}
                        </span>
                      </div>

                      <span className="text-[10px] text-hud-subtle">
                        {step.elapsed_ms ? `${Math.round(step.elapsed_ms)}ms` : '0ms'}
                      </span>
                    </div>

                    {step.output && (
                      <div className="mt-1 text-[11px] text-hud-muted font-sans border-l-2 border-space-700 pl-2 py-0.5 leading-relaxed">
                        {step.output}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExecutionTrace;
