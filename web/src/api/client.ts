import type { DashboardSummary, OrganizationListResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error ${response.status}: ${errorText}`);
  }

  return response.json() as Promise<T>;
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/api/dashboard/summary");
}

export function getOrganizations(params?: {
  search?: string;
  industry?: string;
  region?: string;
  segment?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<OrganizationListResponse> {
  const searchParams = new URLSearchParams();

  if (params?.search) searchParams.set("search", params.search);
  if (params?.industry) searchParams.set("industry", params.industry);
  if (params?.region) searchParams.set("region", params.region);
  if (params?.segment) searchParams.set("segment", params.segment);
  if (params?.status) searchParams.set("status", params.status);

  searchParams.set("limit", String(params?.limit ?? 10));
  searchParams.set("offset", String(params?.offset ?? 0));

  return request<OrganizationListResponse>(
    `/api/organizations?${searchParams.toString()}`
  );
}