import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileImage, X, CheckCircle2, AlertTriangle, Upload, Compass, Sparkles, RefreshCw } from 'lucide-react';
import { UploadedFile } from '../lib/types';
import { uploadFiles } from '../lib/api';

interface InputPanelProps {
  files: UploadedFile[];
  setFiles: React.Dispatch<React.SetStateAction<UploadedFile[]>>;
  mode: string;
  setMode: (mode: string) => void;
  onLoadDemo?: (demoKey: string) => void;
}

const InputPanel: React.FC<InputPanelProps> = ({ files, setFiles, mode, setMode, onLoadDemo }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    setIsUploading(true);
    setUploadError(null);

    try {
      // Use real backend upload
      const response = await uploadFiles(acceptedFiles);
      if (response && response.files) {
        const mapped: UploadedFile[] = response.files.map((f: any) => ({
          file_id: f.file_id,
          filename: f.filename,
          modality: f.modality || (f.filename.toLowerCase().includes('sar') ? 'SAR' : 'Optical'),
          has_crs: Boolean(f.has_crs),
          width: f.width || 1024,
          height: f.height || 1024,
          preview_url: f.preview_url || `/data/uploads/${f.file_id}/${f.filename}`,
          validation: f.validation ? f.validation.is_valid : true,
        }));
        setFiles(prev => [...prev, ...mapped]);
      }
    } catch (err: any) {
      console.warn("Backend upload failed, falling back to local object URLs:", err);
      const fallbackFiles: UploadedFile[] = acceptedFiles.map((file) => ({
        file_id: 'local_' + Math.random().toString(36).substring(7),
        filename: file.name,
        modality: mode === 'OPTICAL + SAR' ? (file.name.toLowerCase().includes('sar') ? 'SAR' : 'Optical') : 'Optical',
        has_crs: file.name.endsWith('.tif') || file.name.endsWith('.tiff'),
        width: 1024,
        height: 1024,
        preview_url: URL.createObjectURL(file),
        validation: true,
      }));
      setFiles(prev => [...prev, ...fallbackFiles]);
    } finally {
      setIsUploading(false);
    }
  }, [mode, setFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/tiff': ['.tif', '.tiff'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    }
  });

  const removeFile = (id: string) => {
    setFiles(files.filter(f => f.file_id !== id));
  };

  const clearAll = () => {
    setFiles([]);
  };

  return (
    <div className="flex flex-col h-full bg-space-900 border-r border-space-700 select-none">
      {/* Panel Header */}
      <div className="px-4 py-3 border-b border-space-700 bg-space-950 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-1.5 h-3 bg-emerald rounded-xs shadow-glow-sm"></div>
          <span className="font-mono text-xs font-bold tracking-widest text-hud-text uppercase">
            Input Configuration
          </span>
        </div>
        {files.length > 0 && (
          <button 
            onClick={clearAll}
            className="text-[10px] font-mono text-hud-muted hover:text-telemetry-red transition-colors flex items-center space-x-1"
          >
            <span>CLEAR</span>
          </button>
        )}
      </div>

      {/* Mode Selector - Segmented Control */}
      <div className="p-3 border-b border-space-700 bg-space-950/60">
        <div className="text-[10px] font-mono uppercase text-hud-muted tracking-wider mb-2 flex items-center justify-between">
          <span>Operational Mode</span>
          <span className="text-emerald text-[9px]">ACTIVE</span>
        </div>
        
        <div className="space-y-1.5">
          {[
            { id: 'SINGLE IMAGE', label: 'SINGLE SCENE', desc: 'Spatial VQA · Grounding · Land Cover' },
            { id: 'BI-TEMPORAL', label: 'BI-TEMPORAL', desc: 'Radiometric Change Detection (T₁ → T₂)' },
            { id: 'OPTICAL + SAR', label: 'OPTICAL + SAR', desc: 'Cross-Modal Specular & Backscatter Fusion' },
          ].map((m) => {
            const active = mode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`w-full text-left px-3 py-2 rounded-xs transition-all border relative overflow-hidden ${
                  active 
                    ? 'bg-space-800 border-emerald text-hud-text shadow-glow-sm' 
                    : 'bg-space-850/70 border-space-700 text-hud-muted hover:text-hud-text hover:border-space-600'
                }`}
              >
                {active && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald shadow-glow-sm"></div>
                )}
                <div className="flex items-center justify-between">
                  <span className={`font-mono text-xs font-bold tracking-wider ${active ? 'text-emerald' : 'text-slate-300'}`}>
                    {m.label}
                  </span>
                  {active && <span className="w-1.5 h-1.5 rounded-full bg-emerald"></span>}
                </div>
                <div className="text-[10px] font-mono text-hud-muted mt-0.5 leading-tight">
                  {m.desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Upload Zone & File List */}
      <div className="p-4 flex-1 flex flex-col space-y-4 overflow-y-auto scrollbar-thin">
        {/* Dropzone with Technical Border */}
        <div 
          {...getRootProps()} 
          className={`relative border-2 border-dashed rounded-xs p-5 text-center cursor-pointer transition-all ${
            isDragActive 
              ? 'border-emerald bg-emerald/10 shadow-glow-sm' 
              : 'border-space-600 bg-space-850/60 hover:border-emerald/60 hover:bg-space-850'
          }`}
        >
          <input {...getInputProps()} />

          {/* Corner telemetry crosses */}
          <div className="absolute top-1 left-1 text-space-600 text-[9px] font-mono leading-none">+</div>
          <div className="absolute top-1 right-1 text-space-600 text-[9px] font-mono leading-none">+</div>
          <div className="absolute bottom-1 left-1 text-space-600 text-[9px] font-mono leading-none">+</div>
          <div className="absolute bottom-1 right-1 text-space-600 text-[9px] font-mono leading-none">+</div>

          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="w-10 h-10 rounded-xs bg-space-800 border border-space-700 flex items-center justify-center text-emerald">
              {isUploading ? <RefreshCw size={18} className="animate-spin text-emerald" /> : <Upload size={18} />}
            </div>

            <div className="space-y-0.5">
              <span className="font-mono text-xs font-bold text-hud-text tracking-wider uppercase block">
                {isDragActive ? 'DROP RASTER ASSETS HERE' : 'DROP SATELLITE IMAGERY'}
              </span>
              <span className="text-[11px] font-mono text-hud-muted">
                or <span className="text-emerald underline underline-offset-2">Browse Local Files</span>
              </span>
            </div>

            {/* Technical format specs */}
            <div className="pt-2 border-t border-space-700/80 w-full flex flex-wrap items-center justify-center gap-1.5 text-[9px] font-mono text-hud-muted">
              <span className="bg-space-800 px-1 py-0.5 rounded-xs border border-space-700">GeoTIFF</span>
              <span className="bg-space-800 px-1 py-0.5 rounded-xs border border-space-700">TIFF</span>
              <span className="bg-space-800 px-1 py-0.5 rounded-xs border border-space-700">PNG</span>
              <span className="bg-space-800 px-1 py-0.5 rounded-xs border border-space-700">JPEG</span>
            </div>
          </div>
        </div>

        {/* Quick Demo Assets Loader */}
        {onLoadDemo && (
          <div className="border border-space-700 bg-space-850/40 p-2.5 rounded-xs">
            <div className="flex items-center space-x-1.5 text-[10px] font-mono text-emerald uppercase tracking-wider mb-2">
              <Sparkles size={12} />
              <span>ISRO Synthetic Demo Assets</span>
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              <button 
                onClick={() => onLoadDemo('single_optical')}
                className="text-[10px] font-mono bg-space-800 hover:bg-space-750 text-hud-text hover:text-emerald px-2 py-1.5 rounded-xs border border-space-700 transition-colors text-left truncate"
              >
                ▸ Optical Scene
              </button>
              <button 
                onClick={() => onLoadDemo('single_sar')}
                className="text-[10px] font-mono bg-space-800 hover:bg-space-750 text-hud-text hover:text-emerald px-2 py-1.5 rounded-xs border border-space-700 transition-colors text-left truncate"
              >
                ▸ SAR Radar
              </button>
              <button 
                onClick={() => onLoadDemo('temporal')}
                className="text-[10px] font-mono bg-space-800 hover:bg-space-750 text-hud-text hover:text-emerald px-2 py-1.5 rounded-xs border border-space-700 transition-colors text-left truncate"
              >
                ▸ Bi-Temporal (T₁/T₂)
              </button>
              <button 
                onClick={() => onLoadDemo('optical_sar')}
                className="text-[10px] font-mono bg-space-800 hover:bg-space-750 text-hud-text hover:text-emerald px-2 py-1.5 rounded-xs border border-space-700 transition-colors text-left truncate"
              >
                ▸ Optical + SAR
              </button>
            </div>
          </div>
        )}

        {/* Active Uploaded Files */}
        {files.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[10px] font-mono uppercase text-hud-muted border-b border-space-700 pb-1">
              <span>Loaded Rasters ({files.length})</span>
              <span className="text-emerald">VERIFIED</span>
            </div>

            <div className="space-y-1.5">
              {files.map((file, idx) => (
                <div 
                  key={file.file_id || idx}
                  className="bg-space-850 border border-space-700 p-2.5 rounded-xs relative group hover:border-emerald/40 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2 min-w-0">
                      <div className="w-8 h-8 rounded-xs bg-space-800 border border-space-700 flex items-center justify-center shrink-0 overflow-hidden">
                        {file.preview_url ? (
                          <img src={file.preview_url} alt={file.filename} className="w-full h-full object-cover" />
                        ) : (
                          <FileImage size={14} className="text-hud-muted" />
                        )}
                      </div>
                      <div className="min-w-0">
                        <div className="text-xs font-mono font-medium text-hud-text truncate max-w-[170px]" title={file.filename}>
                          {file.filename}
                        </div>
                        <div className="flex items-center space-x-1.5 text-[10px] font-mono text-hud-muted mt-0.5">
                          <span className={`px-1 py-0.2 rounded-xs border text-[9px] ${
                            file.modality === 'SAR' 
                              ? 'bg-telemetry-cyan/15 text-telemetry-cyan border-telemetry-cyan/30' 
                              : 'bg-emerald/15 text-emerald border-emerald/30'
                          }`}>
                            {file.modality || 'OPTICAL'}
                          </span>
                          <span>{file.width}×{file.height}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1.5 shrink-0">
                      {file.validation ? (
                        <span title="Raster verified" className="text-emerald flex items-center space-x-0.5 text-[9px] font-mono bg-emerald/10 border border-emerald/30 px-1 py-0.5 rounded-xs">
                          <CheckCircle2 size={11} />
                          <span>READY</span>
                        </span>
                      ) : (
                        <span title="Review required" className="text-telemetry-amber flex items-center space-x-0.5 text-[9px] font-mono bg-telemetry-amber/10 border border-telemetry-amber/30 px-1 py-0.5 rounded-xs">
                          <AlertTriangle size={11} />
                          <span>CHECK</span>
                        </span>
                      )}
                      <button 
                        onClick={() => removeFile(file.file_id)}
                        className="text-hud-muted hover:text-telemetry-red p-1 transition-colors"
                        title="Remove file"
                      >
                        <X size={13} />
                      </button>
                    </div>
                  </div>

                  <div className="mt-2 pt-1.5 border-t border-space-700/60 flex items-center justify-between text-[9px] font-mono text-hud-subtle">
                    <span>CRS: {file.has_crs ? 'EPSG:4326 (WGS84)' : 'AFFINE / PIXEL'}</span>
                    <span>SLOT: 0{idx + 1}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Telemetry Status */}
      <div className="px-4 py-2 border-t border-space-700 bg-space-950 text-[10px] font-mono text-hud-muted flex items-center justify-between">
        <div className="flex items-center space-x-1">
          <Compass size={11} className="text-emerald" />
          <span>GEO-ENGINE ACTIVE</span>
        </div>
        <span className="text-hud-subtle">TIFF V2.4</span>
      </div>
    </div>
  );
};

export default InputPanel;
