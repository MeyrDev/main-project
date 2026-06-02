import { useEffect, useState } from "react";
import { DashboardPage } from "./pages/DashboardPage";
import { OrganizationDetailPage } from "./pages/OrganizationDetailPage";
import { OrganizationsPage } from "./pages/OrganizationsPage";
import "./index.css";
import { getCurrentUser } from "./features/auth/api";
import { clearAuthCredentials, isAuthenticated } from "./features/auth/authStorage";
import { LoginPage } from "./features/auth/LoginPage";
import type { CurrentUser } from "./features/auth/types";
import { InteractionsPage } from "./features/interactions/InteractionsPage";
import { ReportsPage } from "./features/reports/ReportsPage";
import { AuditLogsPage } from "./features/audit/AuditLogsPage";
import { MLModelPage } from "./features/ml/MLModelPage";
import { RiskExplanationPage } from "./features/risk-explanation/RiskExplanationPage";

type Page =
  | "dashboard"
  | "organizations"
  | "organization-detail"
  | "interactions"
  | "reports"
  | "audit"
  | "ml-model"
  | "risk-explanation";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [selectedOrganizationId, setSelectedOrganizationId] = useState<
    string | null
  >(null);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      setIsCheckingAuth(false);
      return;
    }

    getCurrentUser()
      .then(setCurrentUser)
      .catch(() => {
        clearAuthCredentials();
        setCurrentUser(null);
      })
      .finally(() => setIsCheckingAuth(false));
  }, []);

  function openOrganization(id: string) {
    setSelectedOrganizationId(id);
    setPage("organization-detail");
  }

  function goToOrganizations() {
    setPage("organizations");
  }

  function handleLogout() {
    clearAuthCredentials();
    setCurrentUser(null);
    setSelectedOrganizationId(null);
    setPage("dashboard");
  }

  if (isCheckingAuth) {
    return (
      <main className="auth-loading">
        <span>Loading...</span>
      </main>
    );
  }

  if (!currentUser) {
    return <LoginPage onLogin={setCurrentUser} />;
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <img src="/favicon.svg" alt="EntityRIsk Analytics logo" />
          <h2>EntityRIsk Analytics</h2>
        </div>

        <div className="sidebar-user">
          <span>{currentUser.full_name}</span>
          <strong>{currentUser.role ?? "user"}</strong>
        </div>

        <button
          className={page === "dashboard" ? "active" : ""}
          onClick={() => setPage("dashboard")}
        >
          Главная
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
          Аудит
        </button>

        <button
          className={page === "ml-model" ? "active" : ""}
          onClick={() => setPage("ml-model")}
        >
          ML-модель
        </button>

        <button
          className={page === "risk-explanation" ? "active" : ""}
          onClick={() => setPage("risk-explanation")}
        >
          Объяснение рисков
        </button>

        <button className="logout-button" onClick={handleLogout}>
          Выйти
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

        {page === "risk-explanation" && <RiskExplanationPage />}
      </main>
    </div>
  );
}
