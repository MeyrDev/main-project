import { useEffect, useState } from "react";
import { getOrganizations } from "../../api/client";
import type { OrganizationListItem } from "../../types";
import { createReport, getReportData, getReports } from "./api";
import { ReportDataView } from "./ReportDataView";
import { ReportForm } from "./ReportForm";
import { ReportsTable } from "./ReportsTable";
import type { ReportCreate, ReportData, ReportItem } from "./types";
import "./reports.css";

export function ReportsPage() {
  const [organizations, setOrganizations] = useState<OrganizationListItem[]>([]);
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [selectedReportData, setSelectedReportData] = useState<ReportData | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);

  function loadReports() {
    getReports()
      .then((items) => {
        setReports(items);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    getOrganizations({ limit: 200, offset: 0 })
      .then((response) => setOrganizations(response.items))
      .catch((err) => setError(err.message));

    loadReports();
  }, []);

  function handleCreateReport(payload: ReportCreate) {
    createReport(payload)
      .then((report) => {
        loadReports();
        return getReportData(report.id);
      })
      .then(setSelectedReportData)
      .catch((err) => setError(err.message));
  }

  function handleSelectReport(reportId: string) {
    getReportData(reportId)
      .then((data) => {
        setSelectedReportData(data);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }

  return (
    <div className="page">
      <h1>Отчёты</h1>

      {error && <div className="error">Ошибка: {error}</div>}

      <section className="section">
        <h2>Создание отчёта</h2>

        <ReportForm
          organizations={organizations}
          onSubmit={handleCreateReport}
        />
      </section>

      <section className="section">
        <h2>Список отчётов</h2>

        <ReportsTable
          items={reports}
          onSelectReport={handleSelectReport}
        />
      </section>

      <section className="section">
        <h2>Данные отчёта</h2>

        <ReportDataView report={selectedReportData} />
      </section>
    </div>
  );
}