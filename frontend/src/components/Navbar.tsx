import React from "react";
import { ShieldAlert, Activity, Wifi, Terminal } from "lucide-react";

interface NavbarProps {
  currentTab: string;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab }) => {
  return (
    <header className="h-16 border-b border-cyan-500/20 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand */}
      <div className="flex items-center space-x-3">
        <div className="relative">
          <div className="w-9 h-9 rounded-lg bg-cyan-950 border border-cyan-400 flex items-center justify-center text-cyan-400 cyber-glow-blue">
            <ShieldAlert className="w-5 h-5 animate-pulse" />
          </div>
          <span className="absolute -bottom-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
          <span className="absolute -bottom-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-500" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-extrabold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 text-lg">
              SCAMGRAPH AI
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-500/30 font-mono">
              v2.0 PRO
            </span>
          </div>
          <p className="text-[11px] text-slate-400 tracking-tight font-mono">
            CYBER INTELLIGENCE & SYNDICATE CORRELATION
          </p>
        </div>
      </div>

      {/* Cyber Intelligence Status Pills */}
      <div className="hidden md:flex items-center space-x-4">
        {/* DEFCON / Threat Status */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-950/40 border border-rose-500/30 text-rose-400 text-xs font-mono">
          <Activity className="w-3.5 h-3.5 animate-spin" />
          <span>THREAT DEFCON: ELEVATED</span>
        </div>

        {/* Engine Status */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
          <Wifi className="w-3.5 h-3.5 text-cyan-400" />
          <span>NETWORK ONLINE</span>
        </div>

        {/* Active Node View */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-700 text-slate-300 text-xs font-mono">
          <Terminal className="w-3.5 h-3.5 text-indigo-400" />
          <span>VIEW: {currentTab.toUpperCase().replace("-", " ")}</span>
        </div>
      </div>
    </header>
  );
};
