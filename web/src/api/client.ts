import type {
  DashboardSummary,
  OrganizationDetail,
  OrganizationListResponse,
  OrganizationRiskResponse,
  RiskFeatureSnapshotCreate,
  RiskFeatureSnapshotItem,
  RiskPredictionItem,
  OrganizationCreate,
  OrganizationUpdate,
} from "../types";
import type { DealCreate, DealItem, DealUpdate } from "../types/deals";
import { clearAuthCredentials } from "../features/auth/authStorage";
import { getAuthHeaders } from "../features/auth/api";

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

export function getOrganization(id: string): Promise<OrganizationDetail> {
  return request<OrganizationDetail>(`/api/organizations/${id}`);
}

export function getOrganizationRisk(id: string): Promise<OrganizationRiskResponse> {
  return request<OrganizationRiskResponse>(`/api/organizations/${id}/risk`);
}

export function getOrganizationRiskHistory(
  id: string
): Promise<RiskPredictionItem[]> {
  return request<RiskPredictionItem[]>(`/api/organizations/${id}/risk-history`);
}

export function getOrganizationFeatureSnapshots(
  id: string
): Promise<RiskFeatureSnapshotItem[]> {
  return request<RiskFeatureSnapshotItem[]>(
    `/api/organizations/${id}/feature-snapshots`
  );
}

export function createOrganizationFeatureSnapshot(
  id: string,
  payload: RiskFeatureSnapshotCreate
): Promise<RiskFeatureSnapshotItem> {
  return request<RiskFeatureSnapshotItem>(
    `/api/organizations/${id}/feature-snapshots`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

export function predictOrganizationRisk(id: string): Promise<RiskPredictionItem> {
  return request<RiskPredictionItem>(`/api/ml/predict/${id}`, {
    method: "POST",
  });
}

export function predictRiskBySnapshot(
  snapshotId: string
): Promise<RiskPredictionItem> {
  return request<RiskPredictionItem>(`/api/ml/predict-snapshot/${snapshotId}`, {
    method: "POST",
  });
}

export function createOrganization(
  payload: OrganizationCreate
): Promise<OrganizationDetail> {
  return request<OrganizationDetail>("/api/organizations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateOrganization(
  id: string,
  payload: OrganizationUpdate
): Promise<OrganizationDetail> {
  return request<OrganizationDetail>(`/api/organizations/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function getOrganizationDeals(
  organizationId: string
): Promise<DealItem[]> {
  return request<DealItem[]>(`/api/organizations/${organizationId}/deals`);
}

export function createOrganizationDeal(
  organizationId: string,
  payload: DealCreate
): Promise<DealItem> {
  return request<DealItem>(`/api/organizations/${organizationId}/deals`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateDeal(
  dealId: string,
  payload: DealUpdate
): Promise<DealItem> {
  return request<DealItem>(`/api/deals/${dealId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
