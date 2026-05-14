import { useState } from "react";
import { DashboardPage } from "./pages/DashboardPage";
import { OrganizationsPage } from "./pages/OrganizationsPage";
import "./index.css";

type Page = "dashboard" | "organizations";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");

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
          onClick={() => setPage("organizations")}
        >
          Организации
        </button>
      </aside>

      <main className="content">
        {page === "dashboard" && <DashboardPage />}
        {page === "organizations" && <OrganizationsPage />}
      </main>
    </div>
  );
}