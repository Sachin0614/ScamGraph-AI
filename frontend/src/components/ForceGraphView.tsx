import React, { useRef, useEffect } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { GraphNode, GraphEdge } from "../types";

interface ForceGraphViewProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onSelectNode: (nodeId: number) => void;
  selectedNodeId?: number | null;
  highlightedPathNodeIds?: string[];
}

export const ForceGraphView: React.FC<ForceGraphViewProps> = ({
  nodes,
  edges,
  onSelectNode,
  selectedNodeId,
  highlightedPathNodeIds = [],
}) => {
  const fgRef = useRef<any>(null);

  // Format data for react-force-graph
  const graphData = {
    nodes: nodes.map((n) => ({
      ...n,
      val: n.risk_score >= 80 ? 6 : n.risk_score >= 50 ? 4 : 3,
    })),
    links: edges.map((e) => ({
      ...e,
    })),
  };

  useEffect(() => {
    if (fgRef.current) {
      fgRef.current.d3Force("charge")?.strength(-150);
      fgRef.current.d3Force("link")?.distance(60);
    }
  }, [nodes, edges]);

  return (
    <div className="relative w-full h-full bg-slate-950/80 rounded-xl border border-cyan-500/20 overflow-hidden">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        backgroundColor="#030712"
        nodeLabel={(node: any) => `${node.label} (${node.type}) - Risk: ${node.risk_score}/100`}
        nodeColor={(node: any) => {
          if (highlightedPathNodeIds.includes(node.id)) return "#ffff00";
          if (selectedNodeId === node.numeric_id) return "#ffffff";
          return node.color || "#00f0ff";
        }}
        linkColor={(link: any) => {
          const isPath =
            highlightedPathNodeIds.includes(link.source?.id || link.source) &&
            highlightedPathNodeIds.includes(link.target?.id || link.target);
          if (isPath) return "#ffff00";
          return link.color || "#38bdf8";
        }}
        linkWidth={(link: any) => {
          const isPath =
            highlightedPathNodeIds.includes(link.source?.id || link.source) &&
            highlightedPathNodeIds.includes(link.target?.id || link.target);
          return isPath ? 3 : 1.5;
        }}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.005}
        linkDirectionalParticleWidth={2}
        onNodeClick={(node: any) => onSelectNode(node.numeric_id)}
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = node.label;
          const fontSize = 11 / globalScale;
          ctx.font = `${fontSize}px monospace`;

          const isSelected = selectedNodeId === node.numeric_id;
          const isPath = highlightedPathNodeIds.includes(node.id);

          // Node Circle
          ctx.beginPath();
          const radius = (node.val || 3) * 1.5;
          ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
          ctx.fillStyle = isPath ? "#ffff00" : isSelected ? "#ffffff" : node.color || "#00f0ff";
          ctx.fill();

          if (isSelected || isPath || node.risk_score >= 80) {
            ctx.strokeStyle = isPath ? "#ffff00" : isSelected ? "#00f0ff" : "#ef4444";
            ctx.lineWidth = 2 / globalScale;
            ctx.stroke();
          }

          // Node Text Label
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillStyle = isSelected ? "#00f0ff" : "#cbd5e1";
          ctx.fillText(label, node.x, node.y + radius + fontSize);
        }}
      />
    </div>
  );
};
