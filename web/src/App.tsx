import { useState } from "react";
import { DashboardPage } from "./pages/DashboardPage";
import { OrganizationDetailPage } from "./pages/OrganizationDetailPage";
import { OrganizationsPage } from "./pages/OrganizationsPage";
import "./index.css";
import { InteractionsPage } from "./features/interactions/InteractionsPage";

type Page = "dashboard" | "organizations" | "organization-detail" | "interactions";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [selectedOrganizationId, setSelectedOrganizationId] = useState<string | null>(
    null
  );

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
      </main>
    </div>
  );
}