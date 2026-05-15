import type { ReportCreate, ReportData, ReportItem } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error ${response.status}: ${errorText}`);
  }

  return response.json() as Promise<T>;
}

export function getReports(): Promise<ReportItem[]> {
  return request<ReportItem[]>("/api/reports");
}

export function createReport(payload: ReportCreate): Promise<ReportItem> {
  return request<ReportItem>("/api/reports", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getReportData(reportId: string): Promise<ReportData> {
  return request<ReportData>(`/api/reports/${reportId}/data`);
}