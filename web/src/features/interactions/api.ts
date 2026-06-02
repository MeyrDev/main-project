import type { InteractionCreate, InteractionItem, InteractionUpdate } from "./types";
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

export function getOrganizationInteractions(
  organizationId: string
): Promise<InteractionItem[]> {
  return request<InteractionItem[]>(
    `/api/organizations/${organizationId}/interactions`
  );
}

export function createOrganizationInteraction(
  organizationId: string,
  payload: InteractionCreate
): Promise<InteractionItem> {
  return request<InteractionItem>(
    `/api/organizations/${organizationId}/interactions`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

export function updateInteraction(
  interactionId: string,
  payload: InteractionUpdate
): Promise<InteractionItem> {
  return request<InteractionItem>(`/api/interactions/${interactionId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
