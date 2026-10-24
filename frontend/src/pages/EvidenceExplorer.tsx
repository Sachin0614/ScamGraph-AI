import React, { useEffect, useState } from "react";
import {
  FileSearch,
  Fingerprint,
  Link as LinkIcon,
  ExternalLink,
  ShieldAlert,
  AlertTriangle,
  Clock,
  Layers,
} from "lucide-react";
import { apiClient } from "../api/client";

interface EvidenceExplorerProps {
  onSelectInvestigation: (invId: number) => void;
}

export const EvidenceExplorer: React.FC<EvidenceExplorerProps> = ({
  onSelectInvestigation,
}) => {
  const [activeTab, setActiveTab] = useState<"indicators" | "sources">("indicators");
  const [indicators, setIndicators] = useState<any[]>([]);
  const [evidenceSources, setEvidenceSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");

  useEffect(() => {
    setLoading(true);
    Promise.all([
      apiClient.listIndicators(severityFilter === "ALL" ? undefined : severityFilter),
      apiClient.listEvidence(),
    ])
      .then(([inds, evs]) => {
        setIndicators(inds);
        setEvidenceSources(evs);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [severityFilter]);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-100 font-mono tracking-tight flex items-center space-x-2">
          <FileSearch className="w-6 h-6 text-cyan-400" />
          <span>EVIDENCE FORENSICS EXPLORER</span>
        </h1>
        <p className="text-xs text-slate-400 font-mono mt-1">
          Inspect extracted threat indicators, matched text quotes, and preserved external intelligence provenance.
        </p>
      </div>

      {/* View Switcher Tabs & Severity Filter */}
      <div className="glass-panel p-3.5 rounded-xl flex flex-wrap items-center justify-between gap-3">
        <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800">
          <button
            onClick={() => setActiveTab("indicators")}
            className={`px-3.5 py-1.5 rounded-md text-xs font-mono font-bold flex items-center space-x-2 transition cursor-pointer ${
              activeTab === "indicators"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-400/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Fingerprint className="w-3.5 h-3.5" />
            <span>Extracted Threat Indicators ({indicators.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("sources")}
            className={`px-3.5 py-1.5 rounded-md text-xs font-mono font-bold flex items-center space-x-2 transition cursor-pointer ${
              activeTab === "sources"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-400/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <LinkIcon className="w-3.5 h-3.5" />
            <span>Preserved External Evidence ({evidenceSources.length})</span>
          </button>
        </div>

        {activeTab === "indicators" && (
          <div className="flex items-center space-x-1.5">
            {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-2.5 py-1 rounded text-[10px] font-mono font-bold transition cursor-pointer ${
                  severityFilter === sev
                    ? "bg-cyan-500 text-slate-950"
                    : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Tab 1: Extracted Indicators Table */}
      {activeTab === "indicators" && (
        <div className="glass-panel rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 uppercase">
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Threat Indicator Category</th>
                  <th className="py-3 px-4">Matched Evidentiary Snippet</th>
                  <th className="py-3 px-4">Rationale</th>
                  <th className="py-3 px-4 text-right">Origin Dossier</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {indicators.map((ind) => (
                  <tr key={ind.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 px-4 align-top">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          ind.severity === "CRITICAL"
                            ? "bg-rose-950 text-rose-300 border border-rose-500/40"
                            : ind.severity === "HIGH"
                            ? "bg-amber-950 text-amber-300 border border-amber-500/40"
                            : "bg-blue-950 text-blue-300 border border-blue-500/40"
                        }`}
                      >
                        {ind.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 align-top font-bold text-slate-200">
                      {ind.title}
                      <span className="block text-[10px] text-slate-400 font-normal mt-0.5">
                        {ind.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 align-top">
                      {ind.matched_snippet ? (
                        <span className="text-[11px] text-cyan-300 bg-slate-950 p-1.5 rounded border border-slate-800 block max-w-sm">
                          &ldquo;{ind.matched_snippet}&rdquo;
                        </span>
                      ) : (
                        <span className="text-slate-400 italic">No direct quotation</span>
                      )}
                    </td>
                    <td className="py-3 px-4 align-top text-slate-400 max-w-xs leading-relaxed">
                      {ind.explanation}
                    </td>
                    <td className="py-3 px-4 align-top text-right">
                      <button
                        onClick={() => onSelectInvestigation(ind.investigation_id)}
                        className="text-cyan-400 hover:text-cyan-300 font-bold underline cursor-pointer"
                      >
                        {ind.case_number}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Preserved Evidence Sources Table */}
      {activeTab === "sources" && (
        <div className="glass-panel rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 uppercase">
                  <th className="py-3 px-4">Source Type</th>
                  <th className="py-3 px-4">Artifact / URL</th>
                  <th className="py-3 px-4">Supported Claim</th>
                  <th className="py-3 px-4">Retrieved Timestamp</th>
                  <th className="py-3 px-4 text-right">Case ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {evidenceSources.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-slate-400">
                      No external web artifacts captured yet. External recon via TinyFish will populate here.
                    </td>
                  </tr>
                ) : (
                  evidenceSources.map((ev) => (
                    <tr key={ev.id} className="hover:bg-slate-900/40 transition">
                      <td className="py-3 px-4 align-top">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-300 border border-cyan-500/40">
                          {ev.source_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 align-top max-w-xs">
                        <div className="font-bold text-slate-200 truncate">
                          {ev.page_title || "Untitled Artifact"}
                        </div>
                        {ev.source_url && (
                          <a
                            href={ev.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-cyan-400 hover:underline flex items-center space-x-1 text-[11px] truncate mt-0.5"
                          >
                            <span className="truncate">{ev.source_url}</span>
                            <ExternalLink className="w-3 h-3 shrink-0" />
                          </a>
                        )}
                      </td>
                      <td className="py-3 px-4 align-top text-slate-400 max-w-sm">
                        {ev.claims_supported || "Public domain OSINT"}
                      </td>
                      <td className="py-3 px-4 align-top text-slate-400">
                        {new Date(ev.retrieval_timestamp).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 align-top text-right">
                        <button
                          onClick={() => onSelectInvestigation(ev.investigation_id)}
                          className="text-cyan-400 hover:text-cyan-300 font-bold underline cursor-pointer"
                        >
                          {ev.case_number}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
