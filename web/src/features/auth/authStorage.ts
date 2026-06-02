import type { AuthCredentials } from "./types";

const AUTH_STORAGE_KEY = "entity-risk-basic-auth";

function toBase64(value: string): string {
  const bytes = new TextEncoder().encode(value);
  let binary = "";

  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });

  return btoa(binary);
}

export function getAuthCredentials(): AuthCredentials | null {
  const rawValue = sessionStorage.getItem(AUTH_STORAGE_KEY);

  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as AuthCredentials;
  } catch {
    clearAuthCredentials();
    return null;
  }
}

export function setAuthCredentials(credentials: AuthCredentials) {
  sessionStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(credentials));
}

export function clearAuthCredentials() {
  sessionStorage.removeItem(AUTH_STORAGE_KEY);
}

export function isAuthenticated(): boolean {
  return getAuthCredentials() !== null;
}

export function getBasicAuthHeader(): string | null {
  const credentials = getAuthCredentials();

  if (!credentials) {
    return null;
  }

  return `Basic ${toBase64(`${credentials.email}:${credentials.password}`)}`;
}
