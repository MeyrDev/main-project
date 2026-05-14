export type RiskLevel = "low" | "medium" | "high" | "critical";

export type OrganizationListItem = {
  id: string;
  bin: string | null;
  name: string;
  industry: string | null;
  region: string | null;
  segment: string | null;
  status: string;
  annual_revenue: string | null;
  employees_count: number | null;
};

export type OrganizationListResponse = {
  items: OrganizationListItem[];
  total: number;
  limit: number;
  offset: number;
};

export type RiskLevelCount = {
  risk_level: string;
  count: number;
};

export type DashboardHighRiskOrganization = {
  organization_id: string;
  organization_name: string;
  industry: string | null;
  region: string | null;
  risk_score: string;
  risk_level: RiskLevel;
  predicted_at: string;
};

export type DashboardRecentPrediction = {
  prediction_id: string;
  organization_id: string;
  organization_name: string;
  risk_score: string;
  risk_level: RiskLevel;
  predicted_at: string;
};

export type DashboardRecentAuditLog = {
  id: string;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  details: Record<string, unknown> | null;
  created_at: string;
};

export type DashboardSummary = {
  organizations_count: number;
  users_count: number;
  deals_count: number;
  predictions_count: number;
  risk_distribution: RiskLevelCount[];
  high_risk_organizations: DashboardHighRiskOrganization[];
  recent_predictions: DashboardRecentPrediction[];
  recent_audit_logs: DashboardRecentAuditLog[];
};