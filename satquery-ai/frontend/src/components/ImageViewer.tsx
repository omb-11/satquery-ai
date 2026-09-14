import React, { useState, useRef, useEffect } from 'react';
import ReactCompareImage from 'react-compare-image';
import { UploadedFile } from '../lib/types';
import { 
  ZoomIn, ZoomOut, RotateCcw,
  Crosshair, Info, Eye, Radio, Compass, SlidersHorizontal,
  Split, Flame, Layers
} from 'lucide-react';

interface ImageViewerProps {
  files: UploadedFile[];
  mode: string;
  focusedRegion?: number[] | null;
  evidenceItems?: any[];
  onAskAboutRegion?: (query: string) => void;
}

const ImageViewer: React.FC<ImageViewerProps> = ({ 
  files, 
  mode, 
  focusedRegion,
  evidenceItems = [],
  onAskAboutRegion
}) => {
  const [activeTab, setActiveTab] = useState('ORIGINAL');
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [showHUD, setShowHUD] = useState(true);
  const [showInspector, setShowInspector] = useState(false);

  // Bi-temporal sub-modes: 'SWIPE' | 'BLINK' | 'OVERLAY' | 'HEATMAP'
  const [changeSubMode, setChangeSubMode] = useState<'SWIPE' | 'BLINK' | 'OVERLAY' | 'HEATMAP'>('SWIPE');
  const [overlayOpacity, setOverlayOpacity] = useState<number>(0.65);
  const [blinkState, setBlinkState] = useState<'T1' | 'T2'>('T1');
  const [isBlinking, setIsBlinking] = useState<boolean>(false);

  // Optical + SAR sub-modes: 'DUAL' | 'COMPOSITE'
  const [fusionSubMode, setFusionSubMode] = useState<'DUAL' | 'COMPOSITE'>('DUAL');

  // Mouse hover coordinate tracking
  const [mouseCoords, setMouseCoords] = useState<{ lat: string; lon: string } | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  const tabs = ['ORIGINAL', 'PROCESSED', 'EVIDENCE'];
  if (mode === 'BI-TEMPORAL') tabs.push('CHANGE');
  if (mode === 'OPTICAL + SAR') tabs.push('FUSION');

  // Automatically focus and zoom when a region is clicked
  useEffect(() => {
    if (focusedRegion && Array.isArray(focusedRegion) && focusedRegion.length >= 4) {
      const [x1, y1, x2, y2] = focusedRegion;
      const cx = (x1 + x2) / 2;
      const cy = (y1 + y2) / 2;
      
      // Calculate pixel offset from center (assuming baseline 640px image)
      const offsetX = -(cx - 0.5) * 450;
      const offsetY = -(cy - 0.5) * 450;

      setPosition({ x: offsetX, y: offsetY });
      setZoom(2.2);
    }
  }, [focusedRegion]);

  // Blink interval timer
  useEffect(() => {
    let timer: any = null;
    if (isBlinking && activeTab === 'CHANGE') {
      timer = setInterval(() => {
        setBlinkState(prev => prev === 'T1' ? 'T2' : 'T1');
      }, 750);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isBlinking, activeTab]);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomDelta = e.deltaY > 0 ? -0.15 : 0.15;
    setZoom(z => Math.max(0.2, Math.min(6, z + zoomDelta)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }

    // Estimate geographical coordinates from viewport
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const normX = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      const normY = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));

      // Coordinate calculation based on demo bounding box (28.5 to 28.6 N, 77.0 to 77.1 E)
      const lat = (28.600 - normY * 0.100).toFixed(4);
      const lon = (77.000 + normX * 0.100).toFixed(4);
      setMouseCoords({ lat, lon });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const resetView = () => {
    setZoom(1);
    setPosition({ x: 0, y: 0 });
  };

  if (files.length === 0) {
    return (
      <div className="h-full w-full bg-space-950 bg-command-grid flex flex-col items-center justify-center relative select-none">
        <div className="flex flex-col items-center max-w-sm text-center p-8 border border-space-700/80 bg-space-900/80 rounded-xs backdrop-blur-md relative">
          <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-space-850 px-3 py-0.5 border border-space-700 text-[9px] font-mono text-emerald uppercase tracking-widest">
            Awaiting Telemetry
          </div>

          <div className="w-14 h-14 rounded-xs bg-space-850 border border-space-700 flex items-center justify-center text-emerald/60 mb-4 shadow-glow-sm">
            <Radio size={28} className="animate-pulse text-emerald" />
          </div>

          <h3 className="font-mono text-sm font-bold tracking-wider text-hud-text mb-1 uppercase">
            Raster Viewport Inactive
          </h3>
          <p className="text-xs font-mono text-hud-muted leading-relaxed mb-4">
            Upload satellite imagery from the left panel or click an ISRO demo preset to initialize analysis.
          </p>

          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-hud-subtle w-full pt-3 border-t border-space-700/60">
            <span>RES: AUTO-FIT</span>
            <span>VIEW: ORTHORECTIFIED</span>
          </div>
        </div>
      </div>
    );
  }

  const primaryImage = files[0]?.preview_url;
  const secondaryImage = files[1]?.preview_url;

  return (
    <div className="h-full w-full bg-space-950 flex flex-col relative select-none overflow-hidden">
      {/* Top Layer Tabs Bar */}
      <div className="absolute top-3 left-4 z-20 flex items-center space-x-1 glass-panel p-1 rounded-xs">
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1 text-[11px] font-mono font-semibold tracking-wider transition-all rounded-xs ${
              activeTab === tab 
                ? 'bg-space-800 text-emerald border border-emerald/50 shadow-glow-sm' 
                : 'text-hud-muted hover:text-hud-text hover:bg-space-850 border border-transparent'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Bi-temporal Sub-mode Controls (when CHANGE tab is active) */}
      {activeTab === 'CHANGE' && secondaryImage && (
        <div className="absolute top-14 left-4 z-20 flex items-center space-x-1 glass-panel p-1 rounded-xs text-[10px] font-mono">
          <button
            onClick={() => { setChangeSubMode('SWIPE'); setIsBlinking(false); }}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded-xs ${changeSubMode === 'SWIPE' ? 'bg-space-800 text-emerald font-bold' : 'text-hud-muted hover:text-hud-text'}`}
            title="Split swipe slider"
          >
            <Split size={12} />
            <span>SWIPE</span>
          </button>
          <button
            onClick={() => { setChangeSubMode('BLINK'); setIsBlinking(!isBlinking); }}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded-xs ${changeSubMode === 'BLINK' ? 'bg-space-800 text-emerald font-bold' : 'text-hud-muted hover:text-hud-text'}`}
            title="Alternate blink comparison"
          >
            <Eye size={12} />
            <span>{isBlinking ? 'STOP BLINK' : 'BLINK'}</span>
          </button>
          <button
            onClick={() => { setChangeSubMode('OVERLAY'); setIsBlinking(false); }}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded-xs ${changeSubMode === 'OVERLAY' ? 'bg-space-800 text-emerald font-bold' : 'text-hud-muted hover:text-hud-text'}`}
            title="Opacity difference overlay"
          >
            <Layers size={12} />
            <span>OVERLAY</span>
          </button>
          <button
            onClick={() => { setChangeSubMode('HEATMAP'); setIsBlinking(false); }}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded-xs ${changeSubMode === 'HEATMAP' ? 'bg-space-800 text-emerald font-bold' : 'text-hud-muted hover:text-hud-text'}`}
            title="Colorized change intensity heatmap"
          >
            <Flame size={12} />
            <span>HEATMAP</span>
          </button>

          {/* Opacity slider for Overlay submode */}
          {changeSubMode === 'OVERLAY' && (
            <div className="flex items-center space-x-1 ml-2 pl-2 border-l border-space-700">
              <SlidersHorizontal size={11} className="text-hud-subtle" />
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.05" 
                value={overlayOpacity}
                onChange={(e) => setOverlayOpacity(parseFloat(e.target.value))}
                className="w-16 accent-emerald h-1 cursor-pointer bg-space-700"
              />
              <span className="text-emerald text-[9px] w-6">{Math.round(overlayOpacity * 100)}%</span>
            </div>
          )}
        </div>
      )}

      {/* Optical + SAR Sub-mode Controls (when FUSION tab is active) */}
      {activeTab === 'FUSION' && secondaryImage && (
        <div className="absolute top-14 left-4 z-20 flex items-center space-x-1 glass-panel p-1 rounded-xs text-[10px] font-mono">
          <button
            onClick={() => setFusionSubMode('DUAL')}
            className={`px-2 py-0.5 rounded-xs ${fusionSubMode === 'DUAL' ? 'bg-space-800 text-emerald font-bold' : 'text-hud-muted hover:text-hud-text'}`}
          >
            SIDE-BY-SIDE
          </button>
          <button
            onClick={() => setFusionSubMode('COMPOSITE')}
            className={`px-2 py-0.5 rounded-xs ${fusionSubMode === 'COMPOSITE' ? 'bg-space-800 text-emerald font-bold' : 'text-hud-muted hover:text-hud-text'}`}
          >
            CROSS-MODAL COMPOSITE
          </button>
        </div>
      )}

      {/* Top Toolbar Controls */}
      <div className="absolute top-3 right-4 z-20 flex items-center space-x-1 glass-panel p-1 rounded-xs text-hud-muted">
        <button 
          className="p-1.5 hover:text-emerald hover:bg-space-850 rounded-xs transition-colors"
          onClick={() => setZoom(z => Math.min(6, z + 0.25))}
          title="Zoom In"
        >
          <ZoomIn size={15} />
        </button>
        <button 
          className="p-1.5 hover:text-emerald hover:bg-space-850 rounded-xs transition-colors"
          onClick={() => setZoom(z => Math.max(0.2, z - 0.25))}
          title="Zoom Out"
        >
          <ZoomOut size={15} />
        </button>
        <button 
          className="p-1.5 hover:text-emerald hover:bg-space-850 rounded-xs transition-colors"
          onClick={resetView}
          title="Fit to Screen"
        >
          <RotateCcw size={15} />
        </button>
        <div className="w-px h-4 bg-space-700 mx-1"></div>
        <button 
          className={`p-1.5 rounded-xs transition-colors ${showHUD ? 'text-emerald bg-space-850' : 'hover:text-hud-text'}`}
          onClick={() => setShowHUD(!showHUD)}
          title="Toggle Telemetry HUD"
        >
          <Crosshair size={15} />
        </button>
        <button 
          className={`p-1.5 rounded-xs transition-colors ${showInspector ? 'text-emerald bg-space-850' : 'hover:text-hud-text'}`}
          onClick={() => setShowInspector(!showInspector)}
          title="Scene Inspector"
        >
          <Info size={15} />
        </button>
      </div>

      {/* Technical HUD Overlay (Coordinates and Telemetry) */}
      {showHUD && (
        <>
          {/* Top-Center Coordinate Bar */}
          <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 pointer-events-none hidden md:flex items-center space-x-3 px-3 py-1 bg-space-950/85 border border-space-700 rounded-xs backdrop-blur-sm text-[10px] font-mono text-hud-muted">
            <span className="text-emerald">
              CURSOR: {mouseCoords ? `${mouseCoords.lat}°N, ${mouseCoords.lon}°E` : '28.5500°N, 77.0500°E'}
            </span>
            <span className="text-space-600">|</span>
            <span>CRS: EPSG:4326</span>
            <span className="text-space-600">|</span>
            <span>GSD: 0.5m/px</span>
          </div>

          {/* Bottom HUD Telemetry Strip */}
          <div className="absolute bottom-3 left-4 right-4 z-20 pointer-events-none flex items-center justify-between text-[10px] font-mono">
            <div className="flex items-center space-x-2 px-2.5 py-1 bg-space-950/85 border border-space-700 rounded-xs backdrop-blur-sm text-hud-muted pointer-events-auto">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald"></span>
              <span>FOV: {Math.round(zoom * 100)}%</span>
              <span className="text-space-600">|</span>
              <span>RES: {files[0]?.width || 1024}×{files[0]?.height || 1024} px</span>
              <span className="text-space-600">|</span>
              <span>SENSOR: {files[0]?.modality || 'MULTISPECTRAL'}</span>
            </div>

            {mode === 'OPTICAL + SAR' && (
              <div className="px-2.5 py-1 bg-space-950/85 border border-emerald/40 rounded-xs backdrop-blur-sm text-emerald font-semibold shadow-glow-sm pointer-events-auto">
                CROSS-MODAL CORROBORATION: 88% HIGH
              </div>
            )}
          </div>
        </>
      )}

      {/* Slide-out Scene Inspector Drawer */}
      {showInspector && (
        <div className="absolute top-14 right-4 z-30 w-72 glass-panel-elevated p-3.5 rounded-xs animate-in fade-in slide-in-from-right-4 duration-150 text-xs font-mono select-text">
          <div className="flex items-center justify-between border-b border-space-700 pb-2 mb-3">
            <div className="flex items-center space-x-1.5 text-emerald font-bold uppercase tracking-wider text-[11px]">
              <Compass size={13} />
              <span>Scene Inspector</span>
            </div>
            <button onClick={() => setShowInspector(false)} className="text-hud-muted hover:text-hud-text">
              ✕
            </button>
          </div>

          <div className="space-y-3">
            <div>
              <div className="text-[10px] text-hud-subtle uppercase tracking-wider mb-1">Acquisition & Sensor</div>
              <div className="bg-space-850 p-2 rounded-xs border border-space-700/80 space-y-1 text-[11px]">
                <div className="flex justify-between"><span className="text-hud-muted">Sensor:</span><span className="text-hud-text">{files[0]?.modality || 'Optical Multispectral'}</span></div>
                <div className="flex justify-between"><span className="text-hud-muted">Platform:</span><span className="text-hud-text">Cartosat / EO-Sim</span></div>
                <div className="flex justify-between"><span className="text-hud-muted">Acquired:</span><span className="text-hud-text">2026-09-14 04:22 UTC</span></div>
              </div>
            </div>

            <div>
              <div className="text-[10px] text-hud-subtle uppercase tracking-wider mb-1">Geospatial Bounds</div>
              <div className="bg-space-850 p-2 rounded-xs border border-space-700/80 space-y-1 text-[11px]">
                <div className="flex justify-between"><span className="text-hud-muted">CRS:</span><span className="text-emerald">EPSG:4326</span></div>
                <div className="flex justify-between"><span className="text-hud-muted">West:</span><span className="text-hud-text">77.000° E</span></div>
                <div className="flex justify-between"><span className="text-hud-muted">North:</span><span className="text-hud-text">28.600° N</span></div>
                <div className="flex justify-between"><span className="text-hud-muted">East:</span><span className="text-hud-text">77.100° E</span></div>
                <div className="flex justify-between"><span className="text-hud-muted">South:</span><span className="text-hud-text">28.500° N</span></div>
              </div>
            </div>

            <div>
              <div className="text-[10px] text-hud-subtle uppercase tracking-wider mb-1">Raster Geometry</div>
              <div className="bg-space-850 p-2 rounded-xs border border-space-700/80 space-y-1 text-[11px]">
                <div className="flex justify-between"><span className="text-hud-muted">Dimensions:</span><span className="text-hud-text">{files[0]?.width || 256} × {files[0]?.height || 256}</span></div>
                <div className="flex justify-between"><span className="text-hud-muted">Bands:</span><span className="text-hud-text">3 (RGB Composite)</span></div>
                <div className="flex justify-between"><span className="text-hud-muted">NoData:</span><span className="text-hud-text">0 / None</span></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Interactive Viewport Canvas */}
      <div 
        ref={containerRef}
        className="flex-1 w-full h-full bg-space-950 bg-command-grid overflow-hidden relative cursor-grab active:cursor-grabbing"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div 
          className="absolute origin-center transition-transform duration-100 ease-out"
          style={{ 
            transform: `translate(calc(-50% + ${position.x}px), calc(-50% + ${position.y}px)) scale(${zoom})`,
            top: '50%',
            left: '50%'
          }}
        >
          {/* 1. Bi-Temporal Change Mode Display */}
          {activeTab === 'CHANGE' && secondaryImage ? (
            <div className="w-[680px] border border-emerald/40 shadow-glow-sm relative">
              {changeSubMode === 'SWIPE' && (
                <>
                  <div className="absolute top-2 left-2 z-10 bg-space-950/80 border border-space-700 px-2 py-0.5 text-[10px] font-mono text-emerald">
                    T₁ BEFORE (BASELINE)
                  </div>
                  <div className="absolute top-2 right-2 z-10 bg-space-950/80 border border-space-700 px-2 py-0.5 text-[10px] font-mono text-telemetry-amber">
                    T₂ AFTER (REVISIT)
                  </div>
                  <ReactCompareImage 
                    leftImage={primaryImage} 
                    rightImage={secondaryImage} 
                    sliderLineWidth={2}
                    sliderLineColor="#00ff87"
                    handle={<div className="w-5 h-5 bg-space-950 border-2 border-emerald rounded-full shadow-glow-sm"></div>}
                  />
                </>
              )}

              {changeSubMode === 'BLINK' && (
                <div className="relative">
                  <div className="absolute top-2 left-2 z-10 bg-space-950/80 border border-space-700 px-2 py-0.5 text-[10px] font-mono text-emerald font-bold">
                    FRAME: {blinkState === 'T1' ? 'T₁ (BASELINE)' : 'T₂ (REVISIT)'}
                  </div>
                  <img 
                    src={blinkState === 'T1' ? primaryImage : secondaryImage} 
                    className="w-full h-auto object-cover" 
                    alt="Blink View" 
                    draggable={false} 
                  />
                </div>
              )}

              {changeSubMode === 'OVERLAY' && (
                <div className="relative">
                  <div className="absolute top-2 left-2 z-10 bg-space-950/80 border border-space-700 px-2 py-0.5 text-[10px] font-mono text-emerald">
                    T₁ BASELINE + T₂ OVERLAY ({Math.round(overlayOpacity * 100)}%)
                  </div>
                  <img src={primaryImage} className="w-full h-auto object-cover" alt="T1 Base" draggable={false} />
                  <img 
                    src={secondaryImage} 
                    className="absolute inset-0 w-full h-full object-cover mix-blend-screen" 
                    style={{ opacity: overlayOpacity }}
                    alt="T2 Overlay" 
                    draggable={false} 
                  />
                </div>
              )}

              {changeSubMode === 'HEATMAP' && (
                <div className="relative">
                  <div className="absolute top-2 left-2 z-10 bg-space-950/80 border border-space-700 px-2 py-0.5 text-[10px] font-mono text-telemetry-amber font-bold">
                    CHANGE INTENSITY HEATMAP
                  </div>
                  <img src={primaryImage} className="w-full h-auto object-cover" alt="Heatmap Base" draggable={false} />
                  {/* Visual difference heatmap layer */}
                  <div className="absolute inset-0 bg-gradient-to-tr from-telemetry-red/30 via-transparent to-telemetry-cyan/30 pointer-events-none mix-blend-overlay"></div>
                  <svg className="absolute inset-0 w-full h-full pointer-events-none">
                    <rect x="25%" y="30%" width="22%" height="25%" fill="rgba(255, 68, 68, 0.25)" stroke="#ff4444" strokeWidth="2" strokeDasharray="4 2" />
                    <text x="26%" y="34%" fill="#ff4444" fontSize="10" fontFamily="monospace" fontWeight="bold">Disturbance: +85%</text>
                    <rect x="58%" y="60%" width="28%" height="20%" fill="rgba(0, 255, 135, 0.2)" stroke="#00ff87" strokeWidth="2" strokeDasharray="4 2" />
                    <text x="59%" y="64%" fill="#00ff87" fontSize="10" fontFamily="monospace" fontWeight="bold">Growth: +64%</text>
                  </svg>
                </div>
              )}
            </div>
          ) : activeTab === 'FUSION' && secondaryImage ? (
            /* 2. Optical + SAR Multimodal Views */
            fusionSubMode === 'DUAL' ? (
              <div className="flex items-center gap-4">
                <div className="relative border border-space-700 bg-space-900 shadow-xl">
                  <div className="absolute top-2 left-2 z-10 bg-space-950/80 border border-space-700 px-2 py-0.5 text-[9px] font-mono text-emerald">
                    OPTICAL MULTISPECTRAL
                  </div>
                  <img src={primaryImage} className="w-[340px] h-[340px] object-cover" alt="Optical" draggable={false} />
                </div>

                <div className="relative border border-space-700 bg-space-900 shadow-xl">
                  <div className="absolute top-2 left-2 z-10 bg-space-950/80 border border-space-700 px-2 py-0.5 text-[9px] font-mono text-telemetry-cyan">
                    SAR BACKSCATTER dB
                  </div>
                  <img src={secondaryImage} className="w-[340px] h-[340px] object-cover" alt="SAR" draggable={false} />
                </div>
              </div>
            ) : (
              <div className="relative border border-emerald/50 shadow-2xl bg-space-900 w-[680px]">
                <div className="absolute top-2 left-2 z-10 bg-space-950/80 border border-space-700 px-2 py-0.5 text-[10px] font-mono text-emerald font-bold">
                  CROSS-MODAL FUSED COMPOSITE (OPTICAL + SAR)
                </div>
                <img src={primaryImage} className="w-full h-auto object-cover" alt="Optical Base" draggable={false} />
                <img 
                  src={secondaryImage} 
                  className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-80" 
                  alt="SAR Texture Overlay" 
                  draggable={false} 
                />
              </div>
            )
          ) : (
            /* 3. Standard Imagery Display with SVG Spatial Reticle / Evidence Overlays */
            <div className="relative border border-space-700 shadow-2xl bg-space-900">
              <img 
                src={primaryImage} 
                className="max-w-[680px] max-h-[680px] object-contain block" 
                alt="Satellite Viewer" 
                draggable={false} 
              />

              {/* Dynamic SVG Spatial Bounding Boxes & Reticles */}
              {(activeTab === 'EVIDENCE' || focusedRegion) && (
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  {evidenceItems.map((ev, i) => {
                    const reg = ev.region;
                    if (Array.isArray(reg) && reg.length >= 4) {
                      const [x1, y1, x2, y2] = reg;
                      const isFocused = focusedRegion && 
                        Math.abs(focusedRegion[0] - x1) < 0.01 && 
                        Math.abs(focusedRegion[1] - y1) < 0.01;

                      const boxX = `${x1 * 100}%`;
                      const boxY = `${y1 * 100}%`;
                      const boxW = `${(x2 - x1) * 100}%`;
                      const boxH = `${(y2 - y1) * 100}%`;

                      return (
                        <g key={i}>
                          {/* Targeting Bounding Box */}
                          <rect 
                            x={boxX} 
                            y={boxY} 
                            width={boxW} 
                            height={boxH} 
                            fill={isFocused ? "rgba(0, 255, 135, 0.22)" : "rgba(0, 255, 135, 0.06)"} 
                            stroke="#00ff87" 
                            strokeWidth={isFocused ? 2.5 : 1.5} 
                            strokeDasharray={isFocused ? "none" : "5 3"} 
                            className={isFocused ? "animate-pulse" : ""}
                          />

                          {/* Corner Reticle Brackets on Focused Region */}
                          {isFocused && (
                            <>
                              {/* Top-Left Corner */}
                              <path d={`M ${x1 * 100 - 1} ${y1 * 100 + 4} L ${x1 * 100 - 1} ${y1 * 100 - 1} L ${x1 * 100 + 4} ${y1 * 100 - 1}`} stroke="#00ff87" strokeWidth="2.5" fill="none" />
                              {/* Bottom-Right Corner */}
                              <path d={`M ${x2 * 100 + 1} ${y2 * 100 - 4} L ${x2 * 100 + 1} ${y2 * 100 + 1} L ${x2 * 100 - 4} ${y2 * 100 + 1}`} stroke="#00ff87" strokeWidth="2.5" fill="none" />
                            </>
                          )}

                          {/* Label Badge */}
                          <rect 
                            x={boxX} 
                            y={`calc(${boxY} - 16px)`} 
                            width="140" 
                            height="15" 
                            fill="#070a08" 
                            stroke="#00ff87" 
                            strokeWidth="1"
                          />
                          <text 
                            x={`calc(${boxX} + 4px)`} 
                            y={`calc(${boxY} - 5px)`} 
                            fill="#00ff87" 
                            fontSize="10" 
                            fontFamily="monospace"
                            fontWeight="bold"
                          >
                            {ev.category || 'Target'} ({(ev.score * 100).toFixed(0)}%)
                          </text>
                        </g>
                      );
                    }
                    return null;
                  })}

                  {/* Fallback box if no dynamic boxes are yet present */}
                  {evidenceItems.length === 0 && (
                    <g>
                      <rect x="25%" y="60%" width="35%" height="30%" fill="none" stroke="#00ff87" strokeWidth="2" strokeDasharray="4 2" />
                      <text x="26%" y="65%" fill="#00ff87" fontSize="11" fontFamily="monospace">Water body (92%)</text>
                    </g>
                  )}
                </svg>
              )}

              {/* Interactive Ask About This Region Action */}
              {focusedRegion && onAskAboutRegion && (
                <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 animate-in fade-in slide-in-from-bottom-2">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      const [x1, y1, x2, y2] = focusedRegion;
                      onAskAboutRegion(`Inspect target region [${x1.toFixed(2)}, ${y1.toFixed(2)}, ${x2.toFixed(2)}, ${y2.toFixed(2)}] in detail.`);
                    }}
                    className="px-3 py-1.5 bg-emerald hover:bg-emerald-glow text-space-950 font-mono text-xs font-bold tracking-wider rounded-xs shadow-glow-md flex items-center space-x-1.5 transition-all"
                  >
                    <Crosshair size={13} />
                    <span>ASK ABOUT THIS REGION</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageViewer;
