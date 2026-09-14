import React, { useState, useEffect } from 'react';
import { Send, Terminal, Sparkles, ArrowRight, Loader2 } from 'lucide-react';

interface QueryPanelProps {
  mode: string;
  isAnalyzing: boolean;
  onAnalyze: (query: string) => void;
  externalQuery?: string;
  followUpQuestions?: string[];
}

const QueryPanel: React.FC<QueryPanelProps> = ({ 
  mode, 
  isAnalyzing, 
  onAnalyze,
  externalQuery,
  followUpQuestions = []
}) => {
  const [query, setQuery] = useState('');

  useEffect(() => {
    if (externalQuery) {
      setQuery(externalQuery);
    }
  }, [externalQuery]);

  const suggestions = {
    'SINGLE IMAGE': [
      'Describe the land-cover and major objects visible in this scene.',
      'Highlight the water body referred to in the query.',
      'Is there a water body in this image?',
      'Identify built-up areas and road structures.'
    ],
    'BI-TEMPORAL': [
      'What changed between these two dates, and where did the change occur?',
      'Did the built-up area increase, decrease, or remain unchanged?',
      'Highlight the regions responsible for your change conclusion.',
      'Quantify the percentage of scene surface modified.'
    ],
    'OPTICAL + SAR': [
      'Use optical and SAR together to identify built-up and water-covered regions.',
      'What information is visible in SAR but less clear optically?',
      'Do optical and SAR backscatter agree on water body boundaries?',
      'Find structural built-up double-bounce signatures.'
    ]
  }[mode] || [];

  // Set default query placeholder when mode changes
  useEffect(() => {
    if (suggestions.length > 0 && !query) {
      // Keep empty for natural user typing
    }
  }, [mode]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isAnalyzing) return;
    onAnalyze(query);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="p-4 border-b border-space-700 bg-space-950/80 flex flex-col space-y-3 shrink-0 select-none">
      {/* Query Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2 text-hud-muted">
          <Terminal size={13} className="text-emerald" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-hud-text font-bold">
            Natural Language Command
          </span>
        </div>
        <span className="text-[9px] font-mono text-hud-subtle">Ctrl+Enter to Execute</span>
      </div>

      {/* Main Command Input Box */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative border border-space-700 focus-within:border-emerald bg-space-900 rounded-xs transition-colors overflow-hidden">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isAnalyzing}
            placeholder="Ask SatQuery anything about this Earth observation scene..."
            rows={3}
            className="w-full bg-transparent px-3 py-2.5 text-xs font-mono text-hud-text placeholder-hud-subtle focus:outline-none resize-none"
          />

          <div className="px-3 py-1.5 bg-space-850/70 border-t border-space-700/60 flex items-center justify-between text-[10px] font-mono text-hud-subtle">
            <span className="text-emerald/80">{query.length} chars</span>
            <span>ROUTER: AUTOMATIC</span>
          </div>
        </div>

        {/* Powerful Emerald Analyze Button */}
        <button
          type="submit"
          disabled={!query.trim() || isAnalyzing}
          className={`mt-2.5 w-full py-2.5 px-4 rounded-xs font-mono text-xs font-bold tracking-widest uppercase transition-all flex items-center justify-center space-x-2 ${
            isAnalyzing
              ? 'bg-space-800 text-emerald border border-emerald/50 animate-pulse cursor-wait'
              : !query.trim()
                ? 'bg-space-850 text-hud-subtle border border-space-700 cursor-not-allowed'
                : 'bg-emerald text-space-950 hover:bg-emerald-glow shadow-glow-sm hover:shadow-glow-md cursor-pointer'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 size={14} className="animate-spin text-emerald" />
              <span>ORCHESTRATING SPECIALIST PIPELINE...</span>
            </>
          ) : (
            <>
              <span>ANALYZE SCENE</span>
              <ArrowRight size={14} />
            </>
          )}
        </button>
      </form>

      {/* Follow-up Exploration Chips */}
      {followUpQuestions && followUpQuestions.length > 0 && (
        <div className="space-y-1.5 pt-1 border-t border-space-700/80">
          <div className="flex items-center space-x-1.5 text-[10px] font-mono text-emerald font-bold">
            <Sparkles size={11} className="text-emerald animate-pulse" />
            <span>Recommended Follow-up Investigations:</span>
          </div>
          <div className="flex flex-col space-y-1">
            {followUpQuestions.map((fq, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setQuery(fq)}
                className="text-left text-[11px] font-mono px-2 py-1.5 rounded-xs bg-emerald/10 hover:bg-emerald/20 border border-emerald/40 hover:border-emerald text-emerald hover:text-emerald-glow transition-all"
                title={fq}
              >
                <span className="font-bold mr-1.5">⚡</span>
                {fq}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Suggested Query Chips */}
      <div className="space-y-1.5 pt-1">
        <div className="flex items-center space-x-1.5 text-[10px] font-mono text-hud-muted">
          <Sparkles size={11} className="text-hud-subtle" />
          <span>Preset Domain Queries:</span>
        </div>
        <div className="flex flex-col space-y-1">
          {suggestions.map((item, i) => (
            <button
              key={i}
              onClick={() => setQuery(item)}
              className="text-left text-[11px] font-mono px-2 py-1.5 rounded-xs bg-space-850 hover:bg-space-800 border border-space-700 hover:border-emerald/40 text-hud-muted hover:text-hud-text transition-all truncate"
              title={item}
            >
              <span className="text-emerald mr-1.5">›</span>
              {item}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QueryPanel;
