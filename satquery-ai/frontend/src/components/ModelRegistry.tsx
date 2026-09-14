import React, { useEffect, useState } from 'react';
import { Database, AlertTriangle, CheckCircle2, Cpu, Server, Layers, ChevronRight } from 'lucide-react';
import { ModelInfo } from '../lib/types';
import { getModels } from '../lib/api';

const fallbackSpecialists: ModelInfo[] = [
  { name: 'BLIP Remote Sensing VQA', version: '1.0', status: 'Ready', task_types: ['Visual Question Answering', 'Referring Expressions'], device: 'CPU', checkpoint: 'Salesforce/blip-vqa-base', fallback: 'Spectral Heuristics' },
  { name: 'Classical Change Detector', version: '1.0', status: 'Ready', task_types: ['Bi-temporal Difference', 'Otsu Cluster'], device: 'CPU', checkpoint: 'Classical CV (Connected Components)', fallback: 'None' },
  { name: 'Optical-SAR Fusion Engine', version: '1.0', status: 'Ready', task_types: ['Cross-Modal Agreement', 'Specular Corroboration'], device: 'CPU', checkpoint: 'Multi-Sensor Correlator', fallback: 'Single Sensor' },
  { name: 'SAR Backscatter Processor', version: '1.0', status: 'Ready', task_types: ['Backscatter Normalization', 'Water Specular'], device: 'CPU', checkpoint: 'Logarithmic dB Normalizer', fallback: 'Grayscale Thresh' },
  { name: 'Spectral Index Analyzer', version: '1.0', status: 'Ready', task_types: ['NDVI', 'NDWI', 'NDBI Biophysical Extent'], device: 'CPU', checkpoint: 'NumPy Vectorized Kernel', fallback: 'RGB Color Space' },
  { name: 'Spatial Grounding Analyzer', version: '1.0', status: 'Ready', task_types: ['Bounding Box Localization', 'Referring Segmentation'], device: 'CPU', checkpoint: 'Spectral Bounding Engine', fallback: 'Scene Extent' },
  { name: 'BigEarthNet RS Adapter', version: '0.0', status: 'Not installed', task_types: ['Domain Adaptation', 'Projection Head LoRA'], device: 'CPU', checkpoint: 'adapters/rs_adapter_projection_head.pt', fallback: 'Base VLM' },
];

const ModelRegistry = () => {
  const [models, setModels] = useState<ModelInfo[]>(fallbackSpecialists);

  useEffect(() => {
    getModels()
      .then((data) => {
        if (data && data.length > 0) {
          const mapped: ModelInfo[] = data.map((m: any) => ({
            name: m.name || m.id,
            version: m.version || '1.0',
            status: m.status === 'ready' || m.status === 'loaded' ? 'Ready' : m.status === 'not_installed' ? 'Not installed' : 'Fallback',
            task_types: m.task_types || ['Analysis'],
            device: m.device ? m.device.toUpperCase() : 'CPU',
            checkpoint: m.checkpoint || 'Dynamic',
            fallback: m.fallback || 'Classical',
          }));
          setModels(mapped);
        }
      })
      .catch(() => {});
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Ready':
        return (
          <span className="flex items-center space-x-1 text-emerald bg-emerald/10 border border-emerald/40 px-2 py-0.5 rounded-xs text-[10px] font-mono font-bold shadow-glow-sm">
            <CheckCircle2 size={11} />
            <span>ONLINE</span>
          </span>
        );
      case 'Fallback':
        return (
          <span className="flex items-center space-x-1 text-telemetry-amber bg-telemetry-amber/10 border border-telemetry-amber/40 px-2 py-0.5 rounded-xs text-[10px] font-mono font-bold">
            <AlertTriangle size={11} />
            <span>FALLBACK</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center space-x-1 text-hud-muted bg-space-850 border border-space-700 px-2 py-0.5 rounded-xs text-[10px] font-mono">
            <Server size={11} />
            <span>STANDBY</span>
          </span>
        );
    }
  };

  return (
    <div className="glass-panel-elevated rounded-xs overflow-hidden select-none border border-space-700">
      <div className="bg-space-950 px-4 py-3 border-b border-space-700 flex items-center justify-between">
        <h3 className="font-mono text-xs font-bold text-hud-text tracking-wider uppercase flex items-center space-x-2">
          <Database size={15} className="text-emerald" />
          <span>Specialist Engine Registry</span>
        </h3>
        <span className="text-[10px] font-mono text-emerald bg-emerald/10 border border-emerald/30 px-2 py-0.5 rounded-xs">
          {models.filter(m => m.status === 'Ready').length} / {models.length} ACTIVE
        </span>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse font-mono text-xs">
          <thead>
            <tr className="bg-space-950/80 border-b border-space-700 text-[10px] text-hud-muted uppercase tracking-wider">
              <th className="px-4 py-2.5">Specialist Engine</th>
              <th className="px-4 py-2.5">Status</th>
              <th className="px-4 py-2.5">Compute Device</th>
              <th className="px-4 py-2.5">Core Capabilities</th>
              <th className="px-4 py-2.5">Fallback Architecture</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-space-700/60 bg-space-900/60">
            {models.map((m, i) => (
              <tr key={i} className="hover:bg-space-850/50 transition-colors">
                <td className="px-4 py-3">
                  <div className="font-bold text-hud-text flex items-center space-x-2">
                    <span className="text-emerald text-[11px]">›</span>
                    <span>{m.name}</span>
                  </div>
                  <div className="text-[10px] text-hud-subtle mt-0.5">v{m.version} · {m.checkpoint}</div>
                </td>

                <td className="px-4 py-3 whitespace-nowrap">
                  {getStatusBadge(m.status)}
                </td>

                <td className="px-4 py-3 text-hud-muted whitespace-nowrap">
                  <span className="bg-space-850 px-2 py-0.5 rounded-xs border border-space-700 text-[10px] text-hud-text">
                    {m.device}
                  </span>
                </td>

                <td className="px-4 py-3 text-hud-muted">
                  <div className="flex flex-wrap gap-1">
                    {m.task_types.map((t, idx) => (
                      <span key={idx} className="bg-space-850 text-emerald/80 border border-space-700 px-1.5 py-0.5 text-[9px] rounded-xs">
                        {t}
                      </span>
                    ))}
                  </div>
                </td>

                <td className="px-4 py-3 text-[11px] text-hud-subtle font-sans">
                  {m.fallback}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ModelRegistry;
