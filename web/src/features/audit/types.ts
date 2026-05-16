export type AuditLogItem = {
  id: string;
  user_id: string | null;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  details: Record<string, unknown> | null;
  created_at: string;
};

export type AuditLogFilters = {
  action?: string;
  entity_type?: string;
  limit?: number;
  offset?: number;
};