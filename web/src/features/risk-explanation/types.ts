export type RiskFactor = {
  factor: string;
  value: number | string;
  impact: "low" | "medium" | "high" | string;
  description: string;
};

export type RiskExplanation = {
  method?: string;
  model_name?: string;
  version?: string;
  algorithm?: string;
  metrics?: Record<string, number | string>;
  scores?: {
    model_probability?: string;
    domain_score?: string;
    final_score?: string;
  };
  features?: Record<string, unknown>;
  main_factors?: RiskFactor[];
};

export type RiskPrediction = {
  id: string;
  organization_id: string;
  feature_snapshot_id: string | null;
  model_id: string | null;
  risk_score: string;
  risk_level: "low" | "medium" | "high" | "critical";
  explanation: RiskExplanation | null;
  recommendations: {
    actions?: string[];
  } | null;
  predicted_at: string;
};

export type OrganizationRiskResponse = {
  organization_id: string;
  organization_name: string;
  risk_prediction: RiskPrediction | null;
};