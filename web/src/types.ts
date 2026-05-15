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

export type OrganizationDetail = {
  id: string;
  bin: string | null;
  name: string;
  industry: string | null;
  region: string | null;
  segment: string | null;
  status: string;
  annual_revenue: string | null;
  employees_count: number | null;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type RiskPredictionItem = {
  id: string;
  organization_id: string;
  feature_snapshot_id: string | null;
  model_id: string | null;
  risk_score: string;
  risk_level: RiskLevel;
  explanation: Record<string, unknown> | null;
  recommendations: Record<string, unknown> | null;
  predicted_at: string;
};

export type OrganizationRiskResponse = {
  organization_id: string;
  organization_name: string;
  risk_prediction: RiskPredictionItem | null;
};

export type RiskFeatureSnapshotItem = {
  id: string;
  organization_id: string;
  import_batch_id: string | null;
  period_date: string;
  revenue: string | null;
  debt_amount: string | null;
  overdue_days_30: number;
  overdue_days_90: number;
  disputes_count: number;
  transactions_count: number;
  employees_count: number | null;
  raw_features: Record<string, unknown> | null;
  created_at: string;
};

export type RiskFeatureSnapshotCreate = {
  period_date: string;
  revenue: number | null;
  debt_amount: number | null;
  overdue_days_30: number;
  overdue_days_90: number;
  disputes_count: number;
  transactions_count: number;
  employees_count: number | null;
  raw_features: Record<string, unknown> | null;
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

export type OrganizationCreate = {
  bin: string | null;
  name: string;
  industry: string | null;
  region: string | null;
  segment: string | null;
  status: string;
  annual_revenue: number | null;
  employees_count: number | null;
  description: string | null;
};

export type OrganizationUpdate = Partial<OrganizationCreate>;