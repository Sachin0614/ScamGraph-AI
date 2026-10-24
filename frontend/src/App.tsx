import React, { useState } from "react";
import { Navbar } from "./components/Navbar";
import { Sidebar } from "./components/Sidebar";
import { NodeDetailsModal } from "./components/NodeDetailsModal";
import { Dashboard } from "./pages/Dashboard";
import { LiveNetwork } from "./pages/LiveNetwork";
import { NewInvestigation } from "./pages/NewInvestigation";
import { InvestigationHistory } from "./pages/InvestigationHistory";
import { EvidenceExplorer } from "./pages/EvidenceExplorer";
import { SafetyResponse } from "./pages/SafetyResponse";
import { Settings } from "./pages/Settings";
import { InvestigationDetail } from "./types";

export function App() {
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [selectedEntityId, setSelectedEntityId] = useState<number | null>(null);
  const [activeInvestigationId, setActiveInvestigationId] = useState<number | null>(null);

  const handleSelectInvestigation = (invId: number) => {
    setActiveInvestigationId(invId);
    setActiveTab("history");
  };

  const handleInvestigationComplete = (inv: InvestigationDetail) => {
    // Optionally open the 3D globe or detail
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Cyber Command Header */}
      <Navbar currentTab={activeTab} />

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Tactical Navigation Sidebar */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Content Page Canvas */}
        <main className="flex-1 overflow-y-auto bg-gradient-to-b from-slate-950 via-slate-900/60 to-slate-950 cyber-grid relative">
          {activeTab === "dashboard" && (
            <Dashboard
              onNavigate={(tab) => setActiveTab(tab)}
              onSelectEntity={(entId) => setSelectedEntityId(entId)}
              onSelectInvestigation={handleSelectInvestigation}
            />
          )}

          {activeTab === "network" && (
            <LiveNetwork
              onSelectNode={(nodeId) => setSelectedEntityId(nodeId)}
              selectedNodeId={selectedEntityId}
            />
          )}

          {activeTab === "new" && (
            <NewInvestigation
              onInvestigationComplete={handleInvestigationComplete}
              onNavigateToGraph={() => setActiveTab("network")}
            />
          )}

          {activeTab === "history" && (
            <InvestigationHistory
              onSelectInvestigation={(invId) => {
                // If a specific case is clicked, open graph or details
                setActiveInvestigationId(invId);
              }}
              onNavigateToNew={() => setActiveTab("new")}
            />
          )}

          {activeTab === "evidence" && (
            <EvidenceExplorer
              onSelectInvestigation={handleSelectInvestigation}
            />
          )}

          {activeTab === "safety" && <SafetyResponse />}

          {activeTab === "settings" && <Settings />}
        </main>
      </div>

      {/* Global Entity Inspection Modal Drawer */}
      <NodeDetailsModal
        entityId={selectedEntityId}
        onClose={() => setSelectedEntityId(null)}
        onSelectInvestigation={handleSelectInvestigation}
        onSelectEntity={(entId) => setSelectedEntityId(entId)}
      />
    </div>
  );
}

export default App;
