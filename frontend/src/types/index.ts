export interface Entity {
  id: number;
  entity_type: string;
  raw_value: string;
  normalized_value: string;
  display_label: string;
  risk_score: number;
  has_geocoding: boolean;
  latitude?: number | null;
  longitude?: number | null;
  country?: string | null;
  city?: string | null;
  created_at: string;
}

export interface Indicator {
  id?: number;
  category: string;
  title: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  matched_snippet?: string | null;
  explanation: string;
  weight?: number;
}

export interface EvidenceSource {
  id: number;
  source_type: string;
  source_url?: string | null;
  page_title?: string | null;
  retrieval_timestamp: string;
  raw_content_preview?: string | null;
  claims_supported?: string | null;
  is_verified: boolean;
}

export interface AnalysisResult {
  risk_verdict: string;
  overall_risk_score: number;
  detected_indicators: Indicator[];
  exact_snippets: Record<string, string>;
  missing_inconsistencies: string[];
  recommended_verification_steps: string[];
  confidence_explanation?: string;
  limitations_and_uncertainty?: string;
  ai_engine_used: string;
}

export interface ProgressEvent {
  stage: string;
  message: string;
  details?: any;
  timestamp: string;
}

export interface InvestigationDetail {
  id: number;
  case_number: string;
  title: string;
  raw_text?: string | null;
  submitter_notes?: string | null;
  status: string;
  overall_risk_score: number;
  confidence_level: string;
  summary?: string | null;
  created_at: string;
  updated_at: string;
  entities: Entity[];
  indicators: Indicator[];
  evidence_sources: EvidenceSource[];
  analysis_results?: AnalysisResult | null;
  events: ProgressEvent[];
}

export interface InvestigationSummary {
  id: number;
  case_number: string;
  title: string;
  status: string;
  overall_risk_score: number;
  confidence_level: string;
  summary?: string | null;
  created_at: string;
  entities_count: number;
  indicators_count: number;
}

export interface GraphNode {
  id: string;
  numeric_id: number;
  label: string;
  type: string;
  value: string;
  raw_value?: string;
  investigation_id: number;
  risk_score: number;
  color: string;
  has_geocoding: boolean;
  lat?: number | null;
  lng?: number | null;
  x?: number;
  y?: number;
  z?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  confidence: number;
  matching_indicator: string;
  evidence_reason: string;
  color: string;
}

export interface GraphStats {
  total_nodes: number;
  total_edges: number;
  connected_clusters: number;
  network_density: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: GraphStats;
}

export interface EntityInspectionDetails {
  entity_id: number;
  type: string;
  raw_value: string;
  normalized_value: string;
  display_label: string;
  risk_score: number;
  has_geocoding: boolean;
  lat?: number | null;
  lng?: number | null;
  country?: string | null;
  city?: string | null;
  created_at: string;
  parent_investigation: {
    id: number | null;
    case_number: string;
    title: string;
    status: string;
  };
  related_investigations: Array<{
    id: number;
    case_number: string;
    title: string;
    status: string;
    risk_score: number;
  }>;
  connections_count: number;
  connections: Array<{
    direction: "INCOMING" | "OUTGOING";
    relationship_id: number;
    connected_entity_id: number;
    connected_label: string;
    connected_type: string;
    relationship_type: string;
    confidence: number;
    matching_indicator: string;
    reason: string;
    investigation_id: number;
  }>;
  confidence_explanation: string;
  evidence_sources: Array<{
    id: number;
    type: string;
    url?: string | null;
    page_title?: string | null;
    retrieved_at: string;
    claims?: string | null;
  }>;
  recommended_next_actions: string[];
}

export interface DashboardMetrics {
  metrics: {
    total_investigations: number;
    confirmed_scams: number;
    suspicious_cases: number;
    benign_cases: number;
    total_entities: number;
    total_indicators: number;
    total_relationships: number;
    total_evidence_sources: number;
    average_risk_score: number;
  };
  category_distribution: Array<{ category: string; count: number }>;
  entity_distribution: Array<{ type: string; count: number }>;
  top_threats: Array<{
    id: number;
    type: string;
    label: string;
    value: string;
    risk_score: number;
    investigation_id: number;
  }>;
  recent_activity: Array<{
    id: number;
    case_number: string;
    title: string;
    status: string;
    risk_score: number;
    confidence: string;
    created_at: string;
  }>;
}

export interface OfficialPortal {
  name: string;
  url: string;
  helpline?: string | null;
  jurisdiction: string;
  description: string;
  type: string;
}

export interface ActionItem {
  priority: string;
  title: string;
  description: string;
  portal_name?: string | null;
  portal_url?: string | null;
  helpline?: string | null;
}

export interface SafetyResponseData {
  compromise_summary: {
    has_paid: boolean;
    shared_otp: boolean;
    shared_id: boolean;
    clicked_link: boolean;
    amount_lost?: number | null;
    payment_reference?: string | null;
  };
  actions: ActionItem[];
  official_portals: OfficialPortal[];
  disclaimer: string;
}

export interface SettingsData {
  tinyfish_enabled: boolean;
  tinyfish_configured: boolean;
  tinyfish_base_url: string;
  ai_model_name: string;
  openai_configured: boolean;
  gemini_configured: boolean;
  anthropic_configured: boolean;
}
