import { useEffect, useState } from "react";
import { getAuditLogs } from "./api";
import { AuditFilters } from "./AuditFilters";
import { AuditLogsTable } from "./AuditLogsTable";
import type { AuditLogFilters, AuditLogItem } from "./types";
import "./audit.css";

const initialFilters: AuditLogFilters = {
  limit: 100,
  offset: 0,
};

export function AuditLogsPage() {
  const [items, setItems] = useState<AuditLogItem[]>([]);
  const [filters, setFilters] = useState<AuditLogFilters>(initialFilters);
  const [error, setError] = useState<string | null>(null);

  function loadAuditLogs(currentFilters = filters) {
    getAuditLogs(currentFilters)
      .then((data) => {
        setItems(data);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    loadAuditLogs(initialFilters);
  }, []);

  function handleReset() {
    setFilters(initialFilters);
    loadAuditLogs(initialFilters);
  }

  return (
    <div className="page">
      <h1>Журнал аудита</h1>

      {error && <div className="error">Ошибка: {error}</div>}

      <section className="section">
        <h2>Фильтры</h2>

        <AuditFilters
          filters={filters}
          onChange={setFilters}
          onApply={() => loadAuditLogs(filters)}
          onReset={handleReset}
        />
      </section>

      <section className="section">
        <h2>Действия пользователей и системы</h2>

        <AuditLogsTable items={items} />
      </section>
    </div>
  );
}