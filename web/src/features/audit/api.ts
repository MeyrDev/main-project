import type { AuditLogFilters, AuditLogItem } from "./types";
import { clearAuthCredentials } from "../auth/authStorage";
import { getAuthHeaders } from "../auth/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...(options?.headers ?? {}),
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthCredentials();
    }

    const errorText = await response.text();
    throw new Error(`API error ${response.status}: ${errorText}`);
  }

  return response.json() as Promise<T>;
}

export function getAuditLogs(filters?: AuditLogFilters): Promise<AuditLogItem[]> {
  const searchParams = new URLSearchParams();

  if (filters?.action) {
    searchParams.set("action", filters.action);
  }

  if (filters?.entity_type) {
    searchParams.set("entity_type", filters.entity_type);
  }

  searchParams.set("limit", String(filters?.limit ?? 100));
  searchParams.set("offset", String(filters?.offset ?? 0));

  return request<AuditLogItem[]>(`/api/audit-logs?${searchParams.toString()}`);
}
