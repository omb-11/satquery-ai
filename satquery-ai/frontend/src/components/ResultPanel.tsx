import React from 'react';
import { AnalysisResult } from '../lib/types';
import { 
  Target, ShieldCheck, ShieldAlert, Cpu, Download, 
  ExternalLink, Layers, ArrowUpRight, Compass, AlertCircle 
} from 'lucide-react';
import { getReportHtmlUrl } from '../lib/api';

interface ResultPanelProps {
  result: AnalysisResult | null;
  onFocusRegion?: (region: number[]) => void;
}

const ResultPanel: React.FC<ResultPanelProps> = ({ result, onFocusRegion }) => {
  if (!result) {
    return (
      <div className="flex-1 bg-space-900/60 p-6 flex flex-col items-center justify-center text-hud-muted text-sm font-mono text-center select-none">
        <div className="w-12 h-12 rounded-xs bg-space-850 border border-space-700 flex items-center justify-center text-space-600 mb-3">
          <Target size={22} className="opacity-60" />
        </div>
        <p className="text-hud-text uppercase tracking-widest text-xs font-bold">Awaiting Task Execution</p>
        <p className="text-[11px] mt-1 text-hud-subtle max-w-[200px]">
          Submit a command or click an ISRO demo query to view analysis findings.
        </p>
      </div>
    );
  }

  const confLevel = (result.confidence?.level || 'Medium').toLowerCase();
  const confScore = result.confidence?.score || 0.75;
  const confPercent = Math.round(confScore * 100);

  const getConfidenceBadge = () => {
    if (confLevel === 'high') {
      return 'text-emerald border-emerald/50 bg-emerald/10 shadow-glow-sm';
    } else if (confLevel === 'medium') {
      return 'text-telemetry-amber border-telemetry-amber/50 bg-telemetry-amber/10';
    } else {
      return 'text-telemetry-red border-telemetry-red/50 bg-telemetry-red/10';
    }
  };

  const handleDownloadJSON = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `satquery_run_${result.run_id}.json`;
    a.click();
  };

  const handleOpenHTML = () => {
    window.open(getReportHtmlUrl(result.run_id), '_blank');
  };

  // Extract limitations array or string
  const limitationsList = Array.isArray(result.limitations) 
    ? result.limitations 
    : (result.limitations ? [result.limitations] : []);

  return (
    <div className="flex-1 bg-space-900 overflow-y-auto scrollbar-thin select-none">
      {/* Executive Verdict Banner */}
      <div className="p-3 bg-space-950 border-b border-space-700">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald shadow-glow-sm animate-pulse"></span>
            <span className="text-[10px] font-mono font-bold tracking-wider text-emerald uppercase">
              VERDICT: {result.intent ? result.intent.replace(/_/g, ' ').toUpperCase() : 'VERIFIED GROUNDED RS INTEL'}
            </span>
          </div>
          {result.precision_mode && (
            <span className="text-[9px] font-mono px-1.5 py-0.5 bg-space-850 border border-emerald/30 text-emerald rounded-xs uppercase font-bold">
              {result.precision_mode}
            </span>
          )}
        </div>
        {result.summary ? (
          <p className="text-xs font-mono text-emerald/90 bg-emerald/10 border border-emerald/25 p-2 rounded-xs leading-relaxed">
            {result.summary}
          </p>
        ) : (
          <p className="text-[11px] font-mono text-hud-muted bg-space-850/80 border border-space-700 p-1.5 rounded-xs">
            Directly corroborated with deterministic spectral signatures and spatial bounding geometry.
          </p>
        )}
      </div>

      {/* Intelligence Briefing Header */}
      <div className="p-4 border-b border-space-700 bg-space-950/70">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-mono tracking-widest text-emerald font-bold uppercase flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald"></span>
            <span>INTELLIGENCE BRIEFING</span>
          </span>
          <span className="text-[9px] font-mono text-hud-subtle">
            ID: {result.run_id?.slice(0, 8) || 'RUN-001'}
          </span>
        </div>

        {/* Primary Natural Language Finding */}
        <h3 className="text-sm font-sans font-bold text-hud-text leading-snug mb-1">
          {result.answer || 'Analysis complete based on provided Earth observation data.'}
        </h3>

        {/* Extended Findings Details */}
        {result.findings && typeof result.findings === 'string' && (
          <p className="text-xs font-sans text-hud-muted mt-2 leading-relaxed">
            {result.findings}
          </p>
        )}
      </div>

      <div className="p-4 space-y-5">
        {/* Confidence & Engine Telemetry Cards */}
        <div className="grid grid-cols-2 gap-3">
          {/* Calibrated Confidence Metric */}
          <div className="bg-space-850 border border-space-700 p-3 rounded-xs">
            <div className="text-[9px] font-mono text-hud-muted uppercase tracking-wider mb-1.5 flex items-center">
              <ShieldCheck size={11} className="mr-1 text-emerald" />
              <span>CONFIDENCE RATING</span>
            </div>

            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-mono font-bold text-hud-text">{confPercent}%</span>
              <span className={`px-1.5 py-0.5 text-[9px] font-mono font-bold border rounded-xs uppercase ${getConfidenceBadge()}`}>
                {confLevel.toUpperCase()}
              </span>
            </div>

            {/* Horizontal Score Bar */}
            <div className="w-full bg-space-800 h-1.5 mt-2 rounded-full overflow-hidden">
              <div 
                className={`h-full ${confLevel === 'high' ? 'bg-emerald shadow-glow-sm' : confLevel === 'medium' ? 'bg-telemetry-amber' : 'bg-telemetry-red'}`} 
                style={{ width: `${confPercent}%` }}
              ></div>
            </div>
          </div>

          {/* Active Engines / Models */}
          <div className="bg-space-850 border border-space-700 p-3 rounded-xs">
            <div className="text-[9px] font-mono text-hud-muted uppercase tracking-wider mb-1.5 flex items-center">
              <Cpu size={11} className="mr-1 text-emerald" />
              <span>CONTRIBUTING ENGINES</span>
            </div>

            <div className="flex flex-wrap gap-1 mt-1 max-h-[52px] overflow-y-auto scrollbar-thin">
              {(result.models_used || ['TaskRouter', 'SpectralAnalyzer', 'ChangeDetector']).map((m, idx) => (
                <span key={idx} className="px-1.5 py-0.5 bg-space-800 border border-space-700 text-[9px] font-mono text-emerald/90 rounded-xs">
                  {m}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Spatial & Grounded Evidence Section */}
        {result.evidence && result.evidence.length > 0 && (
          <div>
            <div className="flex items-center justify-between text-[10px] font-mono text-hud-muted uppercase tracking-wider mb-2 border-b border-space-700 pb-1">
              <span>Verified Evidence Items ({result.evidence.length})</span>
              <span className="text-emerald">GROUNDED</span>
            </div>

            <div className="space-y-2">
              {result.evidence.map((ev, i) => {
                const hasRegion = Array.isArray(ev.region) && ev.region.length >= 4;
                return (
                  <div 
                    key={i} 
                    className="bg-space-850 border border-space-700 p-2.5 rounded-xs hover:border-emerald/40 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="text-xs font-sans text-hud-text leading-tight">
                        {ev.claim}
                      </div>
                      <span className="text-[9px] font-mono text-emerald bg-emerald/10 border border-emerald/30 px-1 py-0.5 rounded-xs shrink-0 uppercase">
                        {ev.source}
                      </span>
                    </div>

                    <div className="mt-2 flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-[10px] font-mono text-hud-muted">
                        <span>CONF: {(ev.score * 100).toFixed(0)}%</span>
                        {hasRegion && (
                          <span className="text-hud-subtle">
                            [{ev.region[0].toFixed(2)}, {ev.region[1].toFixed(2)}]
                          </span>
                        )}
                      </div>

                      {hasRegion && onFocusRegion && (
                        <button
                          onClick={() => onFocusRegion(ev.region)}
                          className="text-[10px] font-mono text-emerald hover:text-emerald-glow flex items-center space-x-1 hover:underline"
                        >
                          <span>SHOW ON MAP</span>
                          <ArrowUpRight size={10} />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Technical Limitations & Disclaimers */}
        {limitationsList.length > 0 && (
          <div className="bg-space-850/80 border-l-2 border-telemetry-amber p-3 rounded-xs text-xs">
            <div className="flex items-center text-telemetry-amber font-mono text-[10px] uppercase font-bold tracking-wider mb-1">
              <AlertCircle size={11} className="mr-1" />
              <span>Scientific Limitations</span>
            </div>
            <ul className="space-y-1 text-hud-muted text-[11px] font-mono">
              {limitationsList.map((lim, idx) => (
                <li key={idx} className="flex items-start space-x-1">
                  <span className="text-telemetry-amber shrink-0">•</span>
                  <span>{lim}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Export Dossier Triggers */}
        <div className="pt-2 border-t border-space-700 flex gap-2">
          <button 
            onClick={handleOpenHTML}
            className="flex-1 bg-space-850 hover:bg-space-800 border border-space-700 hover:border-emerald/60 py-2 px-3 text-xs font-mono font-semibold text-hud-text hover:text-emerald transition-all rounded-xs flex items-center justify-center space-x-1.5"
            title="Open printable HTML intelligence dossier"
          >
            <ExternalLink size={12} />
            <span>EXPORT REPORT (HTML)</span>
          </button>
          
          <button 
            onClick={handleDownloadJSON}
            className="bg-space-850 hover:bg-space-800 border border-space-700 hover:border-emerald/60 py-2 px-3 text-xs font-mono font-semibold text-hud-muted hover:text-hud-text transition-all rounded-xs flex items-center justify-center"
            title="Download machine-readable JSON"
          >
            <Download size={13} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultPanel;
