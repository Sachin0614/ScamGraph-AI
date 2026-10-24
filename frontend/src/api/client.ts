import axios from "axios";
import {
  DashboardMetrics,
  InvestigationSummary,
  InvestigationDetail,
  GraphData,
  EntityInspectionDetails,
  SafetyResponseData,
  SettingsData,
} from "../types";

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const apiClient = {
  // Dashboard
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const { data } = await api.get<DashboardMetrics>("/dashboard/stats");
    return data;
  },

  // Investigations
  async listInvestigations(status?: string, search?: string): Promise<InvestigationSummary[]> {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    if (search) params.search = search;
    const { data } = await api.get<InvestigationSummary[]>("/investigations", { params });
    return data;
  },

  async getInvestigation(id: number): Promise<InvestigationDetail> {
    const { data } = await api.get<InvestigationDetail>(`/investigations/${id}`);
    return data;
  },

  async createInvestigation(payload: {
    title?: string;
    raw_text?: string;
    website_url?: string;
    recruiter_name?: string;
    email?: string;
    phone?: string;
    payment_id?: string;
    notes?: string;
  }): Promise<InvestigationDetail> {
    const { data } = await api.post<InvestigationDetail>("/investigations", payload);
    return data;
  },

  async deleteInvestigation(id: number): Promise<void> {
    await api.delete(`/investigations/${id}`);
  },

  // Graph
  async getGraph(filters?: {
    entity_types?: string[];
    min_confidence?: number;
    investigation_id?: number;
    search?: string;
  }): Promise<GraphData> {
    const params: any = {};
    if (filters?.min_confidence !== undefined) params.min_confidence = filters.min_confidence;
    if (filters?.investigation_id) params.investigation_id = filters.investigation_id;
    if (filters?.search) params.search = filters.search;
    if (filters?.entity_types && filters.entity_types.length > 0) {
      params.entity_types = filters.entity_types;
    }
    const { data } = await api.get<GraphData>("/graph", { params });
    return data;
  },

  async getEntityInspection(entityId: number): Promise<EntityInspectionDetails> {
    const { data } = await api.get<EntityInspectionDetails>(`/graph/entity/${entityId}/details`);
    return data;
  },

  async getShortestPath(startEntityId: number, endEntityId: number): Promise<any> {
    const { data } = await api.post("/graph/shortest-path", {
      start_entity_id: startEntityId,
      end_entity_id: endEntityId,
    });
    return data;
  },

  async expandCluster(entityId: number, radius = 1): Promise<any> {
    const { data } = await api.get(`/graph/cluster/${entityId}`, { params: { radius } });
    return data;
  },

  // Evidence Explorer
  async listEvidence(sourceType?: string, investigationId?: number): Promise<any[]> {
    const params: Record<string, any> = {};
    if (sourceType) params.source_type = sourceType;
    if (investigationId) params.investigation_id = investigationId;
    const { data } = await api.get("/evidence", { params });
    return data;
  },

  async listIndicators(severity?: string, category?: string, investigationId?: number): Promise<any[]> {
    const params: Record<string, any> = {};
    if (severity) params.severity = severity;
    if (category) params.category = category;
    if (investigationId) params.investigation_id = investigationId;
    const { data } = await api.get("/evidence/indicators", { params });
    return data;
  },

  // Safety
  async assessSafety(answers: {
    has_paid: boolean;
    shared_otp: boolean;
    shared_id: boolean;
    clicked_link: boolean;
    amount_lost?: number;
    payment_reference?: string;
  }): Promise<SafetyResponseData> {
    const { data } = await api.post<SafetyResponseData>("/safety/assess", answers);
    return data;
  },

  async getOfficialPortals(): Promise<{ portals: any[]; disclaimer: string }> {
    const { data } = await api.get("/safety/portals");
    return data;
  },

  // Settings
  async getSettings(): Promise<SettingsData> {
    const { data } = await api.get<SettingsData>("/settings");
    return data;
  },

  async updateSettings(settings: Partial<SettingsData> & { tinyfish_api_key?: string }): Promise<any> {
    const { data } = await api.post("/settings", settings);
    return data;
  },

  async testTinyFish(): Promise<any> {
    const { data } = await api.post("/settings/test-tinyfish");
    return data;
  },
};
