import React, { useState, useEffect } from 'react';
import { 
  Sparkles, CheckCircle2, AlertTriangle, Eye, EyeOff, 
  RefreshCw, ShieldCheck, X, Zap, Cpu, Key 
} from 'lucide-react';
import { getGeminiSettings, updateGeminiSettings, testGeminiConnection } from '../lib/api';

interface GeminiConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSettingsUpdated?: () => void;
}

export const GeminiConfigModal: React.FC<GeminiConfigModalProps> = ({ 
  isOpen, 
  onClose,
  onSettingsUpdated 
}) => {
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gemini-1.5-flash');
  const [isConfigured, setIsConfigured] = useState(false);
  const [maskedKey, setMaskedKey] = useState('');
  
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
    latency_ms?: number;
    model?: string;
  } | null>(null);

  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
      setTestResult(null);
      setSaveSuccess(false);
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      const data = await getGeminiSettings();
      setIsConfigured(Boolean(data.configured));
      setMaskedKey(data.masked_key || '');
      setSelectedModel(data.model || 'gemini-1.5-flash');
    } catch (err) {
      console.warn('Could not fetch Gemini settings from backend:', err);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await testGeminiConnection(apiKey ? apiKey : undefined, selectedModel);
      setTestResult(res);
    } catch (err: any) {
      setTestResult({
        success: false,
        message: err?.response?.data?.detail || err?.message || 'Connection test failed'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      await updateGeminiSettings(apiKey, selectedModel);
      setSaveSuccess(true);
      setIsConfigured(Boolean(apiKey) || isConfigured);
      if (onSettingsUpdated) onSettingsUpdated();
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (err: any) {
      alert(`Failed to save settings: ${err?.response?.data?.detail || err?.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-space-950/80 backdrop-blur-sm select-none">
      <div 
        className="w-full max-w-lg bg-space-900 border border-space-700 shadow-2xl rounded-xs flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-5 py-4 border-b border-space-700 bg-space-950 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-xs bg-emerald/15 border border-emerald/40 flex items-center justify-center text-emerald shadow-glow-sm">
              <Sparkles size={16} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-mono text-sm font-bold text-hud-text tracking-wide">
                  GEMINI AI ANALYST
                </span>
                <span className={`px-1.5 py-0.5 text-[9px] font-mono font-bold rounded-xs border uppercase ${
                  isConfigured 
                    ? 'text-emerald bg-emerald/10 border-emerald/40' 
                    : 'text-telemetry-amber bg-telemetry-amber/10 border-telemetry-amber/40'
                }`}>
                  {isConfigured ? 'READY' : 'OFFLINE (LOCAL RS)'}
                </span>
              </div>
              <p className="text-[10px] font-mono text-hud-muted">
                Multimodal Vision-Language Reasoning & Structured Intelligence
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-hud-muted hover:text-hud-text hover:bg-space-850 rounded-xs transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSave} className="p-5 space-y-4 font-mono text-xs">
          {/* Grounding & Zero-Hallucination Notice */}
          <div className="p-3 bg-space-950/80 border border-space-700/80 rounded-xs flex items-start space-x-2.5">
            <ShieldCheck size={16} className="text-emerald shrink-0 mt-0.5" />
            <div className="text-[11px] text-hud-muted leading-relaxed">
              <span className="text-hud-text font-bold">Zero-Hallucination Grounding: </span>
              Gemini operates as a strict multimodal analyst, consuming deterministic tool outputs (spectral indices, Otsu change masks, SAR backscatter dB, spatial boxes). It never invents raster statistics or geodetic coordinates.
            </div>
          </div>

          {/* API Key Input */}
          <div className="space-y-1.5">
            <label className="text-[11px] uppercase tracking-wider text-hud-muted font-bold flex items-center justify-between">
              <span className="flex items-center space-x-1.5">
                <Key size={12} className="text-emerald" />
                <span>Google AI / Gemini API Key</span>
              </span>
              {maskedKey && (
                <span className="text-[10px] text-hud-subtle font-normal">
                  Current: <code className="text-emerald">{maskedKey}</code>
                </span>
              )}
            </label>
            <div className="relative border border-space-700 focus-within:border-emerald bg-space-950 rounded-xs transition-colors">
              <input
                type={showApiKey ? "text" : "password"}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={maskedKey ? "Enter new key to update, or leave blank to keep current" : "AIzaSy..."}
                className="w-full bg-transparent px-3 py-2 pr-10 text-xs text-hud-text placeholder-hud-subtle focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-2 top-2 p-1 text-hud-subtle hover:text-hud-text transition-colors"
                title={showApiKey ? "Hide Key" : "Show Key"}
              >
                {showApiKey ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
            <p className="text-[10px] text-hud-subtle">
              Keys are kept exclusively in server memory / environment. Never exposed in frontend builds.
            </p>
          </div>

          {/* Model Selection */}
          <div className="space-y-1.5">
            <label className="text-[11px] uppercase tracking-wider text-hud-muted font-bold flex items-center space-x-1.5">
              <Cpu size={12} className="text-emerald" />
              <span>Analyst Model Architecture</span>
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'gemini-1.5-flash', name: '1.5 Flash', desc: 'Fast & responsive' },
                { id: 'gemini-1.5-pro', name: '1.5 Pro', desc: 'Deep RS reasoning' },
                { id: 'gemini-2.0-flash', name: '2.0 Flash', desc: 'Frontier speed' },
              ].map((m) => (
                <button
                  type="button"
                  key={m.id}
                  onClick={() => setSelectedModel(m.id)}
                  className={`p-2.5 rounded-xs border text-left transition-all ${
                    selectedModel === m.id
                      ? 'bg-space-800 border-emerald text-emerald shadow-glow-sm'
                      : 'bg-space-950 border-space-700 text-hud-muted hover:border-space-600'
                  }`}
                >
                  <div className="font-bold text-[11px]">{m.name}</div>
                  <div className="text-[9px] text-hud-subtle mt-0.5">{m.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Test Status Display */}
          {testResult && (
            <div className={`p-2.5 rounded-xs border text-[11px] flex items-center space-x-2 ${
              testResult.success 
                ? 'bg-emerald/10 border-emerald/40 text-emerald' 
                : 'bg-telemetry-red/10 border-telemetry-red/40 text-telemetry-red'
            }`}>
              {testResult.success ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
              <span className="flex-1">
                {testResult.message}
                {testResult.latency_ms ? ` (${testResult.latency_ms} ms)` : ''}
              </span>
            </div>
          )}

          {saveSuccess && (
            <div className="p-2.5 bg-emerald/10 border border-emerald/40 text-emerald rounded-xs text-[11px] flex items-center space-x-2">
              <CheckCircle2 size={14} />
              <span>Gemini configuration saved successfully!</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="pt-2 flex items-center justify-between border-t border-space-700/80">
            <button
              type="button"
              onClick={handleTest}
              disabled={testing}
              className="px-3 py-2 bg-space-850 hover:bg-space-800 border border-space-700 hover:border-emerald/40 text-hud-text rounded-xs transition-colors flex items-center space-x-1.5"
            >
              {testing ? <RefreshCw size={13} className="animate-spin text-emerald" /> : <Zap size={13} className="text-telemetry-amber" />}
              <span>{testing ? 'Testing...' : 'Test Connection'}</span>
            </button>

            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-2 bg-space-950 hover:bg-space-850 border border-space-700 text-hud-muted rounded-xs transition-colors"
              >
                Close
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-emerald hover:bg-emerald-glow text-space-950 font-bold tracking-wider rounded-xs shadow-glow-sm hover:shadow-glow-md transition-all flex items-center space-x-1.5"
              >
                {saving && <RefreshCw size={13} className="animate-spin" />}
                <span>Save Configuration</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default GeminiConfigModal;
