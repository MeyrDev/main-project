import { useEffect, useState } from "react";
import { getDashboardSummary } from "../api/client";
import type { DashboardSummary } from "../types";
import { mapRisk } from "../features/risk-explanation/RiskScoresBlock";

export function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboardSummary()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div className="error">Ошибка загрузки dashboard: {error}</div>;
  }

  if (!data) {
    return <div>Загрузка dashboard...</div>;
  }

  return (
    <div className="page">
      <h1>Dashboard</h1>

      <div className="cards">
        <div className="card">
          <span>Организации</span>
          <strong>{data.organizations_count}</strong>
        </div>

        <div className="card">
          <span>Пользователи</span>
          <strong>{data.users_count}</strong>
        </div>

        <div className="card">
          <span>Сделки</span>
          <strong>{data.deals_count}</strong>
        </div>

        <div className="card">
          <span>Прогнозы риска</span>
          <strong>{data.predictions_count}</strong>
        </div>
      </div>

      <section className="section">
        <h2>Распределение по уровням риска</h2>

        <table>
          <thead>
            <tr>
              <th>Уровень риска</th>
              <th>Количество</th>
            </tr>
          </thead>
          <tbody>
            {data.risk_distribution.map((item) => (
              <tr key={item.risk_level}>
                <td>{mapRisk[item.risk_level as keyof typeof mapRisk] || item.risk_level}</td>
                <td>{item.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="section">
        <h2>Топ организаций с высоким риском</h2>

        <table>
          <thead>
            <tr>
              <th>Организация</th>
              <th>Отрасль</th>
              <th>Регион</th>
              <th>Риск</th>
              <th>Уровень</th>
            </tr>
          </thead>
          <tbody>
            {data.high_risk_organizations.map((item) => (
              <tr key={item.organization_id}>
                <td>{item.organization_name}</td>
                <td>{item.industry ?? "-"}</td>
                <td>{item.region ?? "-"}</td>
                <td>{item.risk_score}</td>
                <td>{mapRisk[item.risk_level as keyof typeof mapRisk] || item.risk_level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="section">
        <h2>Последние действия</h2>

        <table>
          <thead>
            <tr>
              <th>Действие</th>
              <th>Сущность</th>
              <th>Дата</th>
            </tr>
          </thead>
          <tbody>
            {data.recent_audit_logs.map((item) => (
              <tr key={item.id}>
                <td>{item.action}</td>
                <td>{item.entity_type ?? "-"}</td>
                <td>{new Date(item.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}