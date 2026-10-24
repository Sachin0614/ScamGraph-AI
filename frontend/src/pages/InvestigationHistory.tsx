import React, { useEffect, useState } from "react";
import {
  History,
  Search,
  Filter,
  ShieldAlert,
  Trash2,
  FolderOpen,
  ArrowRight,
  Activity,
  Layers,
  AlertTriangle,
} from "lucide-react";
import { apiClient } from "../api/client";
import { InvestigationSummary } from "../types";

interface InvestigationHistoryProps {
  onSelectInvestigation: (invId: number) => void;
  onNavigateToNew: () => void;
}

export const InvestigationHistory: React.FC<InvestigationHistoryProps> = ({
  onSelectInvestigation,
  onNavigateToNew,
}) => {
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const loadData = () => {
    setLoading(true);
    apiClient
      .listInvestigations(
        statusFilter === "ALL" ? undefined : statusFilter,
        searchQuery.trim() || undefined
      )
      .then((data) => {
        setInvestigations(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to permanently delete this investigation dossier and its entities?")) {
      return;
    }
    try {
      await apiClient.deleteInvestigation(id);
      setInvestigations(investigations.filter((i) => i.id !== id));
    } catch (err) {
      alert("Failed to delete investigation.");
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-100 font-mono tracking-tight flex items-center space-x-2">
            <History className="w-6 h-6 text-cyan-400" />
            <span>INVESTIGATION ARCHIVE & DOSSIERS</span>
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Browse and query historical cyber scam dossiers, threat verdicts, and extracted entities.
          </p>
        </div>

        <button
          onClick={onNavigateToNew}
          className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono transition cursor-pointer"
        >
          + New Investigation
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-3.5 rounded-xl flex flex-wrap items-center justify-between gap-3">
        {/* Status Pills */}
        <div className="flex flex-wrap gap-1.5">
          {["ALL", "CONFIRMED_SCAM", "SUSPICIOUS", "BENIGN"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition cursor-pointer ${
                statusFilter === st
                  ? "bg-cyan-500 text-slate-950"
                  : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
              }`}
            >
              {st.replace(/_/g, " ")}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative">
          <input
            type="text"
            placeholder="Search cases or text..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-60 md:w-72 px-3 py-1.5 pl-8 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400"
          />
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
        </form>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="py-20 flex flex-col items-center justify-center font-mono text-cyan-400 space-y-2">
          <Activity className="w-6 h-6 animate-spin" />
          <span className="text-xs">Accessing Case Storage...</span>
        </div>
      )}

      {/* Empty State */}
      {!loading && investigations.length === 0 && (
        <div className="p-12 text-center glass-panel rounded-2xl space-y-3 font-mono">
          <FolderOpen className="w-10 h-10 text-slate-600 mx-auto" />
          <div className="text-sm font-bold text-slate-300">No investigation records found.</div>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Try adjusting your search criteria or submit a new threat case for automated analysis.
          </p>
          <button
            onClick={onNavigateToNew}
            className="mt-2 px-4 py-2 rounded-lg bg-cyan-600 text-slate-950 font-bold text-xs hover:bg-cyan-500 cursor-pointer"
          >
            Launch Investigation
          </button>
        </div>
      )}

      {/* Investigation Cards Grid */}
      {!loading && investigations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {investigations.map((inv) => (
            <div
              key={inv.id}
              onClick={() => onSelectInvestigation(inv.id)}
              className="p-5 rounded-xl glass-panel glass-card-hover space-y-4 cursor-pointer relative group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-500/40">
                      {inv.case_number}
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold uppercase ${
                        inv.status === "CONFIRMED_SCAM"
                          ? "bg-rose-950 text-rose-300 border border-rose-500/40"
                          : inv.status === "SUSPICIOUS"
                          ? "bg-amber-950 text-amber-300 border border-amber-500/40"
                          : "bg-emerald-950 text-emerald-300 border border-emerald-500/40"
                      }`}
                    >
                      {inv.status}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-slate-100 font-mono line-clamp-1 group-hover:text-cyan-300 transition">
                    {inv.title}
                  </h3>
                </div>

                <button
                  onClick={(e) => handleDelete(e, inv.id)}
                  className="p-1.5 rounded text-slate-600 hover:text-rose-400 hover:bg-slate-900 transition"
                  title="Delete Investigation"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {inv.summary && (
                <p className="text-xs text-slate-400 font-mono line-clamp-2 leading-relaxed">
                  {inv.summary}
                </p>
              )}

              {/* Stats & Actions Footer */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                <div className="flex items-center space-x-3 text-slate-400">
                  <span>
                    Risk:{" "}
                    <span
                      className={`font-bold ${
                        inv.overall_risk_score >= 70
                          ? "text-rose-400"
                          : inv.overall_risk_score >= 40
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {inv.overall_risk_score}/100
                    </span>
                  </span>
                  <span>&bull;</span>
                  <span>{inv.entities_count} Entities</span>
                  <span>&bull;</span>
                  <span>{inv.indicators_count} Clues</span>
                </div>

                <span className="text-cyan-400 group-hover:translate-x-1 transition flex items-center space-x-1">
                  <span>Inspect</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
