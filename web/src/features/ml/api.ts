import type {
  MLModelInfo,
  MLTrainingReport,
  MLValidationEvaluation,
} from "./types";
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

export function getMLModelInfo(): Promise<MLModelInfo> {
  return request<MLModelInfo>("/api/ml/model-info");
}

export function getTrainingReport(): Promise<MLTrainingReport> {
  return request<MLTrainingReport>("/api/ml/training-report");
}

export function evaluateValidationDataset(): Promise<MLValidationEvaluation> {
  return request<MLValidationEvaluation>("/api/ml/evaluate-validation", {
    method: "POST",
  });
}
