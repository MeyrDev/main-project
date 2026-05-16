import { useState } from "react";
import { DashboardPage } from "./pages/DashboardPage";
import { OrganizationDetailPage } from "./pages/OrganizationDetailPage";
import { OrganizationsPage } from "./pages/OrganizationsPage";
import "./index.css";
import { InteractionsPage } from "./features/interactions/InteractionsPage";
import { ReportsPage } from "./features/reports/ReportsPage";
import { AuditLogsPage } from "./features/audit/AuditLogsPage";
import { MLModelPage } from "./features/ml/MLModelPage";

type Page =
  | "dashboard"
  | "organizations"
  | "organization-detail"
  | "interactions"
  | "reports"
  | "audit"
  | "ml-model";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [selectedOrganizationId, setSelectedOrganizationId] = useState<
    string | null
  >(null);

  function openOrganization(id: string) {
    setSelectedOrganizationId(id);
    setPage("organization-detail");
  }

  function goToOrganizations() {
    setPage("organizations");
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>Risk CRM</h2>

        <button
          className={page === "dashboard" ? "active" : ""}
          onClick={() => setPage("dashboard")}
        >
          Dashboard
        </button>

        <button
          className={page === "organizations" ? "active" : ""}
          onClick={goToOrganizations}
        >
          Организации
        </button>

        <button
          className={page === "interactions" ? "active" : ""}
          onClick={() => setPage("interactions")}
        >
          Взаимодействия
        </button>

        <button
          className={page === "reports" ? "active" : ""}
          onClick={() => setPage("reports")}
        >
          Отчёты
        </button>

        <button
          className={page === "audit" ? "active" : ""}
          onClick={() => setPage("audit")}
        >
          Аудита
        </button>

        <button
          className={page === "ml-model" ? "active" : ""}
          onClick={() => setPage("ml-model")}
        >
          ML-модель
        </button>
      </aside>

      <main className="content">
        {page === "dashboard" && <DashboardPage />}

        {page === "organizations" && (
          <OrganizationsPage onSelectOrganization={openOrganization} />
        )}

        {page === "organization-detail" && selectedOrganizationId && (
          <OrganizationDetailPage
            organizationId={selectedOrganizationId}
            onBack={goToOrganizations}
          />
        )}

        {page === "interactions" && <InteractionsPage />}

        {page === "reports" && <ReportsPage />}

        {page === "audit" && <AuditLogsPage />}

        {page === "ml-model" && <MLModelPage />}
      </main>
    </div>
  );
}
