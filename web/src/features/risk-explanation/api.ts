import type { OrganizationRiskResponse } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
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