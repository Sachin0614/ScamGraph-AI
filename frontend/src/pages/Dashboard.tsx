import React, { useEffect, useState } from "react";
import {
  ShieldAlert,
  AlertTriangle,
  Network,
  Fingerprint,
  TrendingUp,
  Activity,
  PlusCircle,
  Globe,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { apiClient } from "../api/client";
import { DashboardMetrics } from "../types";

interface DashboardProps {
  onNavigate: (tab: string) => void;
  onSelectEntity: (entityId: number) => void;
  onSelectInvestigation: (invId: number) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  onNavigate,
  onSelectEntity,
  onSelectInvestigation,
}) => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .getDashboardMetrics()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Dashboard fetch error:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center font-mono text-cyan-400 space-x-3">
        <Activity className="w-6 h-6 animate-spin" />
        <span>Loading Cyber Threat Intelligence...</span>
      </div>
    );
  }

  const metrics = data?.metrics;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Top Banner / Welcome Action */}
      <div className="p-6 rounded-2xl glass-panel relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1 relative z-10">
          <div className="flex items-center space-x-2 text-cyan-400 font-mono text-xs tracking-wider">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>REAL-TIME THREAT MONITORING OPERATIONAL</span>
          </div>
          <h1 className="text-2xl font-black text-slate-100 tracking-tight">
            ScamGraph AI — Investigation Command Center
          </h1>
          <p className="text-sm text-slate-400 max-w-2xl font-mono">
            Autonomous threat correlation platform detecting fake employment syndicates, lookalike recruitment domains, and correlated payment indicators.
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0 relative z-10">
          <button
            onClick={() => onNavigate("new")}
            className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs font-mono flex items-center space-x-2 shadow-lg shadow-cyan-500/20 transition cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Investigation</span>
          </button>
          <button
            onClick={() => onNavigate("network")}
            className="px-4 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-cyan-500/30 text-cyan-300 font-bold text-xs font-mono flex items-center space-x-2 transition cursor-pointer"
          >
            <Globe className="w-4 h-4" />
            <span>Explore 3D Globe</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total Investigations */}
        <div className="p-4 rounded-xl glass-panel space-y-2 border-l-4 border-l-cyan-400">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>TOTAL CASES</span>
            <ShieldAlert className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono">
            {metrics?.total_investigations || 0}
          </div>
          <div className="text-[11px] font-mono text-slate-400">
            {metrics?.confirmed_scams || 0} Confirmed Scams ({Math.round(((metrics?.confirmed_scams || 0) / (metrics?.total_investigations || 1)) * 100)}%)
          </div>
        </div>

        {/* Linked Relationships */}
        <div className="p-4 rounded-xl glass-panel space-y-2 border-l-4 border-l-purple-400">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>LINKED EDGES</span>
            <Network className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-black text-purple-300 font-mono">
            {metrics?.total_relationships || 0}
          </div>
          <div className="text-[11px] font-mono text-purple-300/80">
            Evidence-backed links across syndicates
          </div>
        </div>

        {/* Digital Indicators Extracted */}
        <div className="p-4 rounded-xl glass-panel space-y-2 border-l-4 border-l-amber-400">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>INDICATORS</span>
            <Fingerprint className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-300 font-mono">
            {metrics?.total_indicators || 0}
          </div>
          <div className="text-[11px] font-mono text-amber-300/80">
            Domains, emails, UPI & phone handles
          </div>
        </div>

        {/* Average Threat Score */}
        <div className="p-4 rounded-xl glass-panel space-y-2 border-l-4 border-l-rose-500">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>AVG RISK SCORE</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-black text-rose-400 font-mono">
            {metrics?.average_risk_score || 0}
            <span className="text-sm font-normal text-slate-500">/100</span>
          </div>
          <div className="text-[11px] font-mono text-rose-300/80">
            Weighted heuristic threat index
          </div>
        </div>
      </div>

      {/* Two Column Grid: Top Threats & Category Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top High-Risk Entities */}
        <div className="p-5 rounded-xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 font-mono flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>HIGH-RISK DIGITAL INDICATORS</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-500">
              Score &ge; 80.0
            </span>
          </div>

          <div className="space-y-2">
            {data?.top_threats.map((threat) => (
              <div
                key={threat.id}
                onClick={() => onSelectEntity(threat.id)}
                className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 flex items-center justify-between transition cursor-pointer"
              >
                <div className="flex items-center space-x-3 truncate mr-2">
                  <span
                    className={`text-[9px] px-2 py-0.5 rounded font-mono font-bold uppercase ${
                      threat.type === "PAYMENT_ID"
                        ? "bg-rose-950 text-rose-400 border border-rose-500/40"
                        : threat.type === "DOMAIN"
                        ? "bg-purple-950 text-purple-400 border border-purple-500/40"
                        : "bg-cyan-950 text-cyan-400 border border-cyan-500/40"
                    }`}
                  >
                    {threat.type}
                  </span>
                  <span className="text-xs font-mono text-slate-200 truncate font-semibold">
                    {threat.label}
                  </span>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <span className="text-xs font-mono font-bold text-rose-400">
                    {threat.risk_score}
                  </span>
                  <ExternalLink className="w-3.5 h-3.5 text-slate-500 hover:text-cyan-400" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Threat Vector Distribution */}
        <div className="p-5 rounded-xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 font-mono flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              <span>TOP SCAM THREAT PATTERNS</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-500">
              Detected Behaviors
            </span>
          </div>

          <div className="space-y-3">
            {data?.category_distribution.map((cat, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-300">{cat.category.replace(/_/g, " ")}</span>
                  <span className="text-cyan-400 font-bold">{cat.count} occurrences</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div
                    className="bg-gradient-to-r from-cyan-500 to-indigo-500 h-2 rounded-full"
                    style={{
                      width: `${Math.min(100, (cat.count / (data?.category_distribution[0]?.count || 1)) * 100)}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Investigations Table */}
      <div className="p-5 rounded-xl glass-panel space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-200 font-mono flex items-center space-x-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>RECENT INVESTIGATION DOSSIERS</span>
          </h3>
          <button
            onClick={() => onNavigate("history")}
            className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer"
          >
            <span>View All Archives</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase">
                <th className="pb-3 px-3">Case ID</th>
                <th className="pb-3 px-3">Title</th>
                <th className="pb-3 px-3">Status</th>
                <th className="pb-3 px-3">Risk Index</th>
                <th className="pb-3 px-3">Confidence</th>
                <th className="pb-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {data?.recent_activity.map((inv) => (
                <tr
                  key={inv.id}
                  className="hover:bg-slate-900/50 transition cursor-pointer"
                  onClick={() => onSelectInvestigation(inv.id)}
                >
                  <td className="py-3 px-3 font-bold text-cyan-400">{inv.case_number}</td>
                  <td className="py-3 px-3 font-medium text-slate-200 truncate max-w-xs">
                    {inv.title}
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        inv.status === "CONFIRMED_SCAM"
                          ? "bg-rose-950 text-rose-300 border border-rose-500/40"
                          : inv.status === "SUSPICIOUS"
                          ? "bg-amber-950 text-amber-300 border border-amber-500/40"
                          : "bg-emerald-950 text-emerald-300 border border-emerald-500/40"
                      }`}
                    >
                      {inv.status}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-bold">
                    <span
                      className={
                        inv.risk_score >= 70
                          ? "text-rose-400"
                          : inv.risk_score >= 40
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }
                    >
                      {inv.risk_score}/100
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-400">{inv.confidence}</td>
                  <td className="py-3 px-3 text-right text-cyan-400 hover:text-cyan-300">
                    Inspect &rarr;
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
