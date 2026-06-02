import { clearAuthCredentials, getBasicAuthHeader } from "./authStorage";
import type { CurrentUser } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function getAuthHeaders(): Record<string, string> {
  const authHeader = getBasicAuthHeader();

  return authHeader ? { Authorization: authHeader } : {};
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
  });

  if (response.status === 401) {
    clearAuthCredentials();
    throw new Error("Invalid email or password");
  }

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error ${response.status}: ${errorText}`);
  }

  return response.json() as Promise<CurrentUser>;
}
