import React, { useEffect, useState } from "react";
import {
  X,
  ShieldAlert,
  Link as LinkIcon,
  ExternalLink,
  Clock,
  ArrowRight,
  Compass,
  AlertTriangle,
  FolderOpen,
} from "lucide-react";
import { apiClient } from "../api/client";
import { EntityInspectionDetails } from "../types";

interface NodeDetailsModalProps {
  entityId: number | null;
  onClose: () => void;
  onSelectInvestigation?: (invId: number) => void;
  onSelectEntity?: (entId: number) => void;
}

export const NodeDetailsModal: React.FC<NodeDetailsModalProps> = ({
  entityId,
  onClose,
  onSelectInvestigation,
  onSelectEntity,
}) => {
  const [details, setDetails] = useState<EntityInspectionDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!entityId) return;
    setLoading(true);
    setError(null);
    apiClient
      .getEntityInspection(entityId)
      .then((data) => {
        setDetails(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to load entity inspection dossier.");
        setLoading(false);
      });
  }, [entityId]);

  if (!entityId) return null;

  const getTypeColor = (type: string) => {
    switch (type) {
      case "JOB_OFFER":
        return "text-cyan-400 border-cyan-500/40 bg-cyan-950/60";
      case "DOMAIN":
        return "text-purple-400 border-purple-500/40 bg-purple-950/60";
      case "EMAIL":
        return "text-amber-400 border-amber-500/40 bg-amber-950/60";
      case "PHONE":
        return "text-emerald-400 border-emerald-500/40 bg-emerald-950/60";
      case "PAYMENT_ID":
        return "text-rose-400 border-rose-500/40 bg-rose-950/60";
      case "RECRUITER":
        return "text-pink-400 border-pink-500/40 bg-pink-950/60";
      default:
        return "text-blue-400 border-blue-500/40 bg-blue-950/60";
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[480px] bg-slate-950/95 backdrop-blur-xl border-l border-cyan-500/30 z-50 shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-500/50 flex items-center justify-center text-cyan-400">
            <Compass className="w-4 h-4 animate-spin" />
          </div>
          <div>
            <h3 className="text-sm font-bold tracking-wider text-slate-100 font-mono">
              ENTITY DOSSIER INSPECTOR
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">
              NODE ID #{entityId}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Body Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {loading && (
          <div className="py-20 flex flex-col items-center justify-center text-cyan-400 space-y-3 font-mono">
            <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs">Querying Tactical Graph DB...</span>
          </div>
        )}

        {error && (
          <div className="p-4 rounded-lg bg-rose-950/50 border border-rose-500/40 text-rose-300 text-xs font-mono">
            {error}
          </div>
        )}

        {details && !loading && (
          <>
            {/* Entity Badge and Value */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span
                  className={`text-[10px] px-2.5 py-1 rounded font-mono font-bold border ${getTypeColor(
                    details.type
                  )}`}
                >
                  {details.type}
                </span>
                <div className="flex items-center space-x-1 text-xs font-mono">
                  <ShieldAlert
                    className={`w-4 h-4 ${
                      details.risk_score >= 70
                        ? "text-rose-400"
                        : details.risk_score >= 40
                        ? "text-amber-400"
                        : "text-emerald-400"
                    }`}
                  />
                  <span className="text-slate-300 font-bold">
                    Risk: {details.risk_score}/100
                  </span>
                </div>
              </div>

              <div>
                <label className="text-[11px] text-slate-400 font-mono uppercase tracking-wider block">
                  Normalized Identifier
                </label>
                <div className="text-base font-bold text-slate-100 font-mono break-all mt-0.5">
                  {details.normalized_value}
                </div>
              </div>

              {details.raw_value !== details.normalized_value && (
                <div>
                  <label className="text-[11px] text-slate-400 font-mono uppercase tracking-wider block">
                    Original Submitted Form
                  </label>
                  <div className="text-xs text-slate-300 font-mono break-all mt-0.5 bg-slate-950/60 p-2 rounded border border-slate-800">
                    {details.raw_value}
                  </div>
                </div>
              )}

              {/* Geocoding Info (if evidence-backed) */}
              {details.has_geocoding && (
                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs font-mono text-cyan-300">
                  <span>Geographic Evidence:</span>
                  <span>
                    {details.city ? `${details.city}, ` : ""}
                    {details.country || "Documented Locale"} ({details.lat?.toFixed(2)}, {details.lng?.toFixed(2)})
                  </span>
                </div>
              )}
            </div>

            {/* Parent Investigation Context */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-2">
              <label className="text-[11px] text-slate-400 font-mono uppercase tracking-wider flex items-center justify-between">
                <span>Associated Case Dossier</span>
                <span className="text-cyan-400">{details.parent_investigation.case_number}</span>
              </label>
              <div className="text-sm font-semibold text-slate-200">
                {details.parent_investigation.title}
              </div>
              {details.parent_investigation.id && onSelectInvestigation && (
                <button
                  onClick={() => onSelectInvestigation(details.parent_investigation.id!)}
                  className="mt-2 text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 font-mono transition cursor-pointer"
                >
                  <FolderOpen className="w-3.5 h-3.5" />
                  <span>Open Full Investigation Case</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              )}
            </div>

            {/* Relationship Connections */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                  <LinkIcon className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Connected Graph Edges ({details.connections_count})</span>
                </label>
              </div>

              {details.connections.length === 0 ? (
                <div className="p-4 rounded-lg bg-slate-900/40 border border-slate-800 text-xs text-slate-400 font-mono text-center">
                  No direct connections detected. This entity remains an isolated node.
                </div>
              ) : (
                <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                  {details.connections.map((conn) => (
                    <div
                      key={conn.relationship_id}
                      onClick={() => onSelectEntity && onSelectEntity(conn.connected_entity_id)}
                      className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-cyan-500/50 transition cursor-pointer space-y-1.5"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-bold">
                          {conn.relationship_type}
                        </span>
                        <span className="text-[11px] font-mono text-slate-400">
                          Confidence: {Math.round(conn.confidence * 100)}%
                        </span>
                      </div>
                      <div className="text-xs font-mono text-slate-200 font-semibold truncate">
                        {conn.connected_label}
                      </div>
                      <p className="text-[11px] text-slate-400 font-mono leading-tight">
                        {conn.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Confidence Explanation */}
            <div className="p-3.5 rounded-lg bg-cyan-950/30 border border-cyan-500/20 text-xs font-mono text-cyan-200/90 leading-relaxed">
              <span className="font-bold text-cyan-300 block mb-1">
                EVIDENCE-BASED SCORING:
              </span>
              {details.confidence_explanation}
            </div>

            {/* Related Investigations (Cross-Syndicate Corroboration) */}
            {details.related_investigations.length > 1 && (
              <div className="space-y-2">
                <label className="text-xs font-mono font-bold text-purple-400 uppercase tracking-wider flex items-center space-x-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>
                    Linked Syndicate Cases ({details.related_investigations.length})
                  </span>
                </label>
                <div className="space-y-1.5">
                  {details.related_investigations.map((relInv) => (
                    <div
                      key={relInv.id}
                      onClick={() => onSelectInvestigation && onSelectInvestigation(relInv.id)}
                      className="p-2.5 rounded-lg bg-purple-950/20 border border-purple-500/30 flex items-center justify-between text-xs font-mono hover:bg-purple-950/40 transition cursor-pointer"
                    >
                      <div className="truncate mr-2">
                        <span className="text-purple-300 font-bold mr-2">
                          {relInv.case_number}
                        </span>
                        <span className="text-slate-300 truncate">
                          {relInv.title}
                        </span>
                      </div>
                      <span className="text-rose-400 font-bold shrink-0">
                        Risk: {relInv.risk_score}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Next Recommended Tactical Actions */}
            <div className="space-y-2">
              <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
                Recommended Actions
              </label>
              <ul className="space-y-1.5">
                {details.recommended_next_actions.map((act, idx) => (
                  <li
                    key={idx}
                    className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 flex items-start space-x-2"
                  >
                    <span className="text-cyan-400 font-bold shrink-0">#{idx + 1}</span>
                    <span>{act}</span>
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
