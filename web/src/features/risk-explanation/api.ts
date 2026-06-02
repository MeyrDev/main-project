import type { OrganizationRiskResponse } from "./types";
import { clearAuthCredentials } from "../auth/authStorage";
import { getAuthHeaders } from "../auth/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
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

export function getOrganizationRisk(
  organizationId: string
): Promise<OrganizationRiskResponse> {
  return request<OrganizationRiskResponse>(
    `/api/organizations/${organizationId}/risk`
  );
}
