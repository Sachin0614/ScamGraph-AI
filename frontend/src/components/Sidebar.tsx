import React from "react";
import {
  LayoutDashboard,
  Globe,
  PlusCircle,
  History,
  FileSearch,
  ShieldCheck,
  Settings,
  ChevronRight,
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      subtitle: "Overview & Threat Radar",
      icon: LayoutDashboard,
      badge: "LIVE",
    },
    {
      id: "network",
      label: "Live Network",
      subtitle: "3D Globe & Syndicate Graph",
      icon: Globe,
      glow: true,
      badge: "3D",
    },
    {
      id: "new",
      label: "New Investigation",
      subtitle: "Ingest Offer & Red Flags",
      icon: PlusCircle,
    },
    {
      id: "history",
      label: "Investigation History",
      subtitle: "Case Dossiers & Archive",
      icon: History,
    },
    {
      id: "evidence",
      label: "Evidence Explorer",
      subtitle: "Artifacts & Provenance",
      icon: FileSearch,
    },
    {
      id: "safety",
      label: "Safety & Response",
      subtitle: "Victim Defense Playbook",
      icon: ShieldCheck,
      badge: "HELP",
    },
    {
      id: "settings",
      label: "Settings",
      subtitle: "TinyFish & AI Engine",
      icon: Settings,
    },
  ];

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-slate-950 flex flex-col justify-between shrink-0 select-none">
      <div className="py-4">
        <div className="px-5 mb-3 text-[11px] font-mono tracking-wider text-slate-500 uppercase">
          Tactical Operations
        </div>

        <nav className="space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full group text-left px-3.5 py-2.5 rounded-lg flex items-center justify-between transition-all duration-200 cursor-pointer ${
                  isActive
                    ? "bg-cyan-950/60 border border-cyan-500/50 text-cyan-300 shadow-[0_0_15px_rgba(0,240,255,0.15)]"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent"
                }`}
              >
                <div className="flex items-center space-x-3 truncate">
                  <div
                    className={`w-8 h-8 rounded-md flex items-center justify-center shrink-0 transition-colors ${
                      isActive
                        ? "bg-cyan-500/20 text-cyan-300 border border-cyan-400/40"
                        : "bg-slate-900 text-slate-400 group-hover:text-cyan-400 border border-slate-800"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="truncate">
                    <div className="text-sm font-medium tracking-tight truncate flex items-center gap-1.5">
                      <span>{item.label}</span>
                      {item.badge && (
                        <span
                          className={`text-[9px] px-1 py-0.2 rounded font-mono font-bold ${
                            item.badge === "3D"
                              ? "bg-violet-950 text-violet-300 border border-violet-500/40"
                              : item.badge === "LIVE"
                              ? "bg-emerald-950 text-emerald-300 border border-emerald-500/40"
                              : "bg-rose-950 text-rose-300 border border-rose-500/40"
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-slate-400 truncate font-mono">
                      {item.subtitle}
                    </div>
                  </div>
                </div>

                <ChevronRight
                  className={`w-4 h-4 transition-transform duration-200 ${
                    isActive ? "text-cyan-400 translate-x-0.5" : "text-slate-700 opacity-0 group-hover:opacity-100"
                  }`}
                />
              </button>
            );
          })}
        </nav>
      </div>

      {/* Cyber System Footer Status */}
      <div className="p-4 border-t border-slate-900 bg-slate-950/50">
        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span>CORE STATUS</span>
            <span className="text-emerald-400 font-bold">OPTIMAL</span>
          </div>
          <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
            <div className="bg-gradient-to-r from-cyan-500 to-indigo-500 h-1.5 w-full animate-pulse" />
          </div>
          <div className="mt-2 text-[10px] text-slate-400">
            Node Sync: 100% | SQLite WAL Active
          </div>
        </div>
      </div>
    </aside>
  );
};
