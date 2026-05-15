export type ReportType =
  | "organization_card"
  | "risk_summary"
  | "portfolio_analytics"
  | "model_quality";

export type ReportStatus = "pending" | "ready" | "failed";

export type ReportItem = {
  id: string;
  organization_id: string | null;
  created_by_id: string | null;
  title: string;
  report_type: ReportType;
  status: ReportStatus;
  parameters: Record<string, unknown> | null;
  file_path: string | null;
  created_at: string;
};

export type ReportCreate = {
  organization_id: string | null;
  created_by_id: string | null;
  title: string;
  report_type: ReportType;
  parameters: Record<string, unknown> | null;
};

export type ReportData = {
  id: string;
  title: string;
  report_type: ReportType;
  status: ReportStatus;
  generated_at: string;
  parameters: Record<string, unknown> | null;
  content: Record<string, unknown>;
};