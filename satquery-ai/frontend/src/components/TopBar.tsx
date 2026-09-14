import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Cpu, Database, Server, Play, ChevronRight, Sliders, Shield } from 'lucide-react';
import SystemStatus from './SystemStatus';

const TopBar: React.FC = () => {
  const [showStatus, setShowStatus] = useState(false);

  return (
    <header className="h-14 border-b border-space-700 bg-space-950/95 backdrop-blur-md flex items-center justify-between px-4 text-sm shrink-0 z-30 select-none relative">
      {/* Brand & Mission identity */}
      <div className="flex items-center space-x-4">
        <Link to="/" className="flex items-center space-x-2.5 group">
          {/* Geometric satellite / orbit icon */}
          <div className="relative w-7 h-7 flex items-center justify-center bg-space-850 border border-emerald/40 rounded-sm group-hover:border-emerald group-hover:shadow-glow-sm transition-all">
            <svg viewBox="0 0 24 24" className="w-4 h-4 text-emerald" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" fill="currentColor" fillOpacity="0.3" />
              <ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(-30 12 12)" strokeDasharray="2 2" />
              <rect x="3" y="10" width="3" height="4" rx="0.5" strokeWidth="1.5" />
              <rect x="18" y="10" width="3" height="4" rx="0.5" strokeWidth="1.5" />
              <line x1="6" y1="12" x2="9" y2="12" />
              <line x1="15" y1="12" x2="18" y2="12" />
            </svg>
            <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-emerald shadow-glow-sm"></span>
          </div>

          <div className="flex flex-col">
            <div className="flex items-center space-x-1.5">
              <span className="font-mono font-extrabold tracking-wider text-base text-hud-text">SATQUERY</span>
              <span className="font-mono text-xs px-1 py-0.2 bg-emerald/15 text-emerald border border-emerald/30 rounded-xs font-semibold">AI</span>
            </div>
            <span className="text-[9px] font-mono text-hud-muted tracking-widest uppercase">
              Earth Observation Intelligence
            </span>
          </div>
        </Link>

        <div className="hidden sm:block h-5 w-px bg-space-700"></div>

        <div className="hidden xl:flex items-center space-x-2 text-[11px] font-mono text-hud-muted">
          <span className="text-hud-subtle">NODE:</span>
          <span className="text-hud-text bg-space-850 px-1.5 py-0.5 border border-space-700 rounded-xs">ISRO-SAC / PRIMARY</span>
        </div>
      </div>

      {/* Center Mission Tag */}
      <div className="hidden lg:flex items-center space-x-2 border border-space-700/80 bg-space-900/60 px-3 py-1 rounded-xs backdrop-blur-sm">
        <Shield size={12} className="text-emerald" />
        <span className="text-hud-muted font-mono text-[11px] tracking-wider uppercase">
          ISRO SIH 2026 <span className="text-hud-subtle mx-1">/</span> PS 26167
        </span>
      </div>

      {/* Right Navigation & Telemetry */}
      <div className="flex items-center space-x-4">
        <nav className="flex space-x-1 font-mono text-xs">
          {[
            { path: '/', label: 'WORKSPACE' },
            { path: '/benchmark', label: 'BENCHMARKS' },
            { path: '/training', label: 'ADAPTATION' },
          ].map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `px-2.5 py-1 text-[11px] font-semibold tracking-wider transition-all rounded-xs ${
                  isActive 
                    ? 'bg-space-800 text-emerald border-b-2 border-emerald shadow-glow-sm' 
                    : 'text-hud-muted hover:text-hud-text hover:bg-space-850'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Prominent JUDGE MODE button */}
        <Link
          to="/demo"
          className="flex items-center space-x-1.5 px-3 py-1 bg-emerald/10 hover:bg-emerald/20 text-emerald border border-emerald/50 hover:border-emerald text-xs font-mono font-bold tracking-wider rounded-xs transition-all shadow-glow-sm"
          title="Open Guided Presentation for Judges"
        >
          <Play size={11} className="fill-emerald" />
          <span>JUDGE MODE</span>
        </Link>

        <div className="h-4 w-px bg-space-700"></div>

        {/* Telemetry Status Pill */}
        <div className="relative">
          <button 
            className="flex items-center space-x-3 text-hud-muted hover:text-hud-text transition-colors bg-space-850 hover:bg-space-800 px-2.5 py-1 rounded-xs border border-space-700 text-xs font-mono"
            onClick={() => setShowStatus(!showStatus)}
            title="Inspect Telemetry & Engine Status"
          >
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald animate-pulse"></span>
              <span className="text-[11px] font-medium text-emerald hidden md:inline">SYSTEM ONLINE</span>
            </div>
            <div className="h-3 w-px bg-space-700 hidden md:block"></div>
            <div className="hidden md:flex items-center space-x-1 text-hud-muted text-[10px]">
              <Cpu size={12} className="text-hud-muted" />
              <span>CPU COMPUTE</span>
            </div>
            <div className="hidden md:flex items-center space-x-1 text-hud-muted text-[10px]">
              <Database size={12} className="text-emerald" />
              <span>8 SPECIALISTS</span>
            </div>
            <Sliders size={12} className="text-hud-subtle" />
          </button>

          {showStatus && (
            <div className="absolute top-full right-0 mt-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <SystemStatus onClose={() => setShowStatus(false)} />
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default TopBar;
