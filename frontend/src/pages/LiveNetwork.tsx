import React, { useEffect, useState } from "react";
import {
  Globe,
  Share2,
  Filter,
  Search,
  Route,
  RotateCcw,
  Layers,
  Sliders,
  CheckSquare,
  Activity,
} from "lucide-react";
import { apiClient } from "../api/client";
import { GraphData, GraphNode } from "../types";
import { Globe3D } from "../components/Globe3D";
import { ForceGraphView } from "../components/ForceGraphView";

interface LiveNetworkProps {
  onSelectNode: (nodeId: number) => void;
  selectedNodeId?: number | null;
}

export const LiveNetwork: React.FC<LiveNetworkProps> = ({
  onSelectNode,
  selectedNodeId,
}) => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"globe" | "force">("globe");

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [minConfidence, setMinConfidence] = useState(0.0);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([
    "JOB_OFFER",
    "DOMAIN",
    "EMAIL",
    "PHONE",
    "PAYMENT_ID",
    "RECRUITER",
  ]);

  // Shortest Path state
  const [pathStartId, setPathStartId] = useState<number | null>(null);
  const [pathEndId, setPathEndId] = useState<number | null>(null);
  const [pathResult, setPathResult] = useState<any>(null);
  const [highlightedPathIds, setHighlightedPathIds] = useState<string[]>([]);
  const [pathLoading, setPathLoading] = useState(false);

  const fetchGraph = () => {
    setLoading(true);
    apiClient
      .getGraph({
        entity_types: selectedTypes,
        min_confidence: minConfidence,
        search: searchQuery.trim() || undefined,
      })
      .then((data) => {
        setGraphData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading graph:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchGraph();
  }, [minConfidence, selectedTypes]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchGraph();
  };

  const handleTypeToggle = (type: string) => {
    if (selectedTypes.includes(type)) {
      setSelectedTypes(selectedTypes.filter((t) => t !== type));
    } else {
      setSelectedTypes([...selectedTypes, type]);
    }
  };

  const calculateShortestPath = () => {
    if (!pathStartId || !pathEndId) return;
    setPathLoading(true);
    apiClient
      .getShortestPath(pathStartId, pathEndId)
      .then((res) => {
        setPathResult(res);
        setPathLoading(false);
        if (res.found && res.path_nodes) {
          setHighlightedPathIds(res.path_nodes.map((n: any) => String(n.id)));
        } else {
          setHighlightedPathIds([]);
        }
      })
      .catch((err) => {
        console.error("Path error:", err);
        setPathLoading(false);
      });
  };

  const clearPath = () => {
    setPathStartId(null);
    setPathEndId(null);
    setPathResult(null);
    setHighlightedPathIds([]);
  };

  const entityTypeOptions = [
    { type: "JOB_OFFER", label: "Job Offer", color: "#00F0FF" },
    { type: "DOMAIN", label: "Domain/URL", color: "#A855F7" },
    { type: "EMAIL", label: "Email Address", color: "#F59E0B" },
    { type: "PHONE", label: "Phone/WhatsApp", color: "#10B981" },
    { type: "PAYMENT_ID", label: "Payment / UPI", color: "#EF4444" },
    { type: "RECRUITER", label: "Recruiter Alias", color: "#EC4899" },
  ];

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col p-4 space-y-4">
      {/* Top Tactical Controls Bar */}
      <div className="glass-panel p-3.5 rounded-xl flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center space-x-3">
          {/* Mode Switcher: 3D Globe vs 2D Force */}
          <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800">
            <button
              onClick={() => setViewMode("globe")}
              className={`px-3 py-1.5 rounded-md text-xs font-mono font-bold flex items-center space-x-1.5 transition cursor-pointer ${
                viewMode === "globe"
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-400/40"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Globe className="w-3.5 h-3.5" />
              <span>3D Globe Network</span>
            </button>
            <button
              onClick={() => setViewMode("force")}
              className={`px-3 py-1.5 rounded-md text-xs font-mono font-bold flex items-center space-x-1.5 transition cursor-pointer ${
                viewMode === "force"
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-400/40"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>2D Force Layout</span>
            </button>
          </div>

          {/* Search Form */}
          <form onSubmit={handleSearchSubmit} className="relative">
            <input
              type="text"
              placeholder="Search domain, email, phone, case..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-56 md:w-64 px-3 py-1.5 pl-8 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
          </form>
        </div>

        {/* Stats Summary Pills */}
        <div className="hidden lg:flex items-center space-x-4 text-xs font-mono text-slate-400">
          <div>
            Nodes: <span className="text-cyan-400 font-bold">{graphData?.stats.total_nodes || 0}</span>
          </div>
          <div>
            Edges: <span className="text-purple-400 font-bold">{graphData?.stats.total_edges || 0}</span>
          </div>
          <div>
            Clusters: <span className="text-amber-400 font-bold">{graphData?.stats.connected_clusters || 0}</span>
          </div>
        </div>
      </div>

      {/* Main Workspace: Left Controls Sidebar + Center Visualization Canvas */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* Left Filter and Path Panel */}
        <div className="w-64 glass-panel p-4 rounded-xl flex flex-col justify-between shrink-0 overflow-y-auto space-y-4">
          <div className="space-y-4">
            {/* Entity Types Multi-Select */}
            <div>
              <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5 mb-2.5">
                <Layers className="w-3.5 h-3.5 text-cyan-400" />
                <span>Entity Types</span>
              </label>
              <div className="space-y-1.5">
                {entityTypeOptions.map((opt) => (
                  <label
                    key={opt.type}
                    className="flex items-center space-x-2 text-xs font-mono text-slate-300 hover:text-slate-100 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedTypes.includes(opt.type)}
                      onChange={() => handleTypeToggle(opt.type)}
                      className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0"
                    />
                    <span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: opt.color }}
                    />
                    <span>{opt.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Confidence Slider */}
            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-slate-300 flex items-center space-x-1">
                  <Sliders className="w-3 h-3 text-cyan-400" />
                  <span>Min Confidence</span>
                </span>
                <span className="text-cyan-400 font-bold">{Math.round(minConfidence * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="0.95"
                step="0.05"
                value={minConfidence}
                onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
                className="w-full accent-cyan-400 bg-slate-800 h-1.5 rounded cursor-pointer"
              />
            </div>

            {/* Shortest Relationship Path Finder */}
            <div className="pt-3 border-t border-slate-800 space-y-2">
              <label className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider flex items-center space-x-1.5">
                <Route className="w-3.5 h-3.5" />
                <span>Shortest Path Finder</span>
              </label>

              <div className="space-y-2">
                <div>
                  <span className="text-[10px] text-slate-400 font-mono">Start Entity:</span>
                  <select
                    value={pathStartId || ""}
                    onChange={(e) => setPathStartId(Number(e.target.value) || null)}
                    className="w-full mt-1 p-1.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-slate-200"
                  >
                    <option value="">Select Origin Node...</option>
                    {graphData?.nodes.map((n) => (
                      <option key={n.numeric_id} value={n.numeric_id}>
                        {n.label} ({n.type})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <span className="text-[10px] text-slate-400 font-mono">Destination Entity:</span>
                  <select
                    value={pathEndId || ""}
                    onChange={(e) => setPathEndId(Number(e.target.value) || null)}
                    className="w-full mt-1 p-1.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-slate-200"
                  >
                    <option value="">Select Target Node...</option>
                    {graphData?.nodes.map((n) => (
                      <option key={n.numeric_id} value={n.numeric_id}>
                        {n.label} ({n.type})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={calculateShortestPath}
                    disabled={!pathStartId || !pathEndId || pathLoading}
                    className="flex-1 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-slate-950 font-bold text-xs font-mono transition cursor-pointer"
                  >
                    {pathLoading ? "Tracing..." : "Find Path"}
                  </button>
                  {highlightedPathIds.length > 0 && (
                    <button
                      onClick={clearPath}
                      className="px-2 py-1.5 rounded bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-mono"
                    >
                      Clear
                    </button>
                  )}
                </div>

                {pathResult && (
                  <div className="p-2.5 rounded bg-slate-900/90 border border-slate-800 text-[11px] font-mono">
                    {pathResult.found ? (
                      <div className="text-emerald-400 space-y-1">
                        <div>&check; Path Found: {pathResult.length} hops</div>
                        <div className="text-slate-300 text-[10px]">
                          Highlighted in yellow on graph.
                        </div>
                      </div>
                    ) : (
                      <div className="text-amber-400">{pathResult.message}</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Color Legend */}
          <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-400 space-y-1.5">
            <div className="font-bold text-slate-300 uppercase text-[10px]">
              Edge Colors
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-0.5 bg-rose-500" />
              <span>Exact Match (&ge;90%)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-0.5 bg-purple-500" />
              <span>Corroborated (&ge;70%)</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-0.5 bg-cyan-400" />
              <span>Lead / Offer Edge</span>
            </div>
          </div>
        </div>

        {/* Center Graph Canvas */}
        <div className="flex-1 min-w-0 h-full relative">
          {loading && (
            <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center font-mono text-cyan-400 space-x-3 z-10">
              <Activity className="w-6 h-6 animate-spin" />
              <span>Constructing Tactical Network Topology...</span>
            </div>
          )}

          {graphData && (
            viewMode === "globe" ? (
              <Globe3D
                nodes={graphData.nodes}
                edges={graphData.edges}
                onSelectNode={onSelectNode}
                selectedNodeId={selectedNodeId}
                highlightedPathNodeIds={highlightedPathIds}
              />
            ) : (
              <ForceGraphView
                nodes={graphData.nodes}
                edges={graphData.edges}
                onSelectNode={onSelectNode}
                selectedNodeId={selectedNodeId}
                highlightedPathNodeIds={highlightedPathIds}
              />
            )
          )}
        </div>
      </div>
    </div>
  );
};
