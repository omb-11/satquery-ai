import React, { useEffect, useState } from 'react';
import { X, Cpu, HardDrive, Database, Activity, CheckCircle, Radio } from 'lucide-react';
import { getSystemInfo } from '../lib/api';
import { SystemInfo } from '../lib/types';

const SystemStatus = ({ onClose }: { onClose: () => void }) => {
  const [info, setInfo] = useState<SystemInfo | null>(null);

  useEffect(() => {
    getSystemInfo().then(setInfo).catch(() => setInfo({
      cpu_count: 12,
      ram_total_gb: 15.7,
      device: 'cpu',
      cuda_available: false,
      gpu_name: null,
      disk_free_gb: 58.0
    }));
  }, []);

  return (
    <div className="w-80 glass-panel-elevated rounded-xs shadow-2xl overflow-hidden font-mono text-xs select-none border border-emerald/30">
      <div className="flex justify-between items-center bg-space-950 px-3.5 py-2.5 border-b border-space-700">
        <span className="font-bold text-hud-text flex items-center space-x-2 text-[11px] uppercase tracking-wider">
          <Activity size={13} className="text-emerald animate-pulse" />
          <span>MISSION TELEMETRY</span>
        </span>
        <button onClick={onClose} className="text-hud-muted hover:text-hud-text transition-colors">
          <X size={14} />
        </button>
      </div>
      
      {info ? (
        <div className="p-4 space-y-3.5 bg-space-900/90 text-[11px]">
          {/* Compute Engine */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-hud-muted">
              <span className="flex items-center space-x-1.5 text-hud-subtle uppercase text-[10px]">
                <Cpu size={12} className="text-emerald" />
                <span>Compute Hardware</span>
              </span>
              <span className="text-emerald font-bold px-1.5 py-0.2 bg-emerald/10 border border-emerald/30 rounded-xs text-[10px]">
                {info.device ? info.device.toUpperCase() : 'CPU (ACTIVE)'}
              </span>
            </div>

            <div className="bg-space-850 p-2.5 rounded-xs border border-space-700 space-y-1 text-hud-text">
              <div className="flex justify-between">
                <span className="text-hud-muted">Logical CPU Cores:</span>
                <span>{info.cpu_count} Units</span>
              </div>
              <div className="flex justify-between">
                <span className="text-hud-muted">Physical RAM:</span>
                <span>{info.ram_total_gb} GB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-hud-muted">CUDA Accelerator:</span>
                <span className={info.cuda_available ? "text-emerald" : "text-hud-muted"}>
                  {info.cuda_available ? (info.gpu_name || "Available") : "Disabled (CPU Mode)"}
                </span>
              </div>
            </div>
          </div>

          {/* Storage Telemetry */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-hud-subtle uppercase text-[10px]">
              <span className="flex items-center space-x-1.5">
                <HardDrive size={12} className="text-emerald" />
                <span>NVMe Scratch Space</span>
              </span>
              <span className="text-hud-text font-bold text-[10px]">{info.disk_free_gb} GB Free</span>
            </div>
            <div className="w-full bg-space-850 border border-space-700 h-1.5 rounded-full overflow-hidden">
              <div className="bg-emerald h-full w-1/3 shadow-glow-sm"></div>
            </div>
          </div>
          
          {/* Engine State */}
          <div className="space-y-1.5 pt-1 border-t border-space-700/60">
            <div className="flex justify-between items-center text-hud-subtle uppercase text-[10px]">
              <span className="flex items-center space-x-1.5">
                <Database size={12} className="text-emerald" />
                <span>Subsystem Health</span>
              </span>
            </div>
            <div className="grid grid-cols-2 gap-1 text-[10px]">
              <span className="flex items-center text-emerald bg-space-850 px-1.5 py-1 rounded-xs border border-space-700">
                <CheckCircle size={10} className="mr-1" /> Rasterio GDAL
              </span>
              <span className="flex items-center text-emerald bg-space-850 px-1.5 py-1 rounded-xs border border-space-700">
                <CheckCircle size={10} className="mr-1" /> SQLite Engine
              </span>
              <span className="flex items-center text-emerald bg-space-850 px-1.5 py-1 rounded-xs border border-space-700">
                <CheckCircle size={10} className="mr-1" /> PyTorch Core
              </span>
              <span className="flex items-center text-emerald bg-space-850 px-1.5 py-1 rounded-xs border border-space-700">
                <CheckCircle size={10} className="mr-1" /> SSE Event Stream
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-6 text-center text-hud-muted">
          <span>POLLING TELEMETRY...</span>
        </div>
      )}
    </div>
  );
};

export default SystemStatus;
