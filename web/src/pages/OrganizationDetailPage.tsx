import { FormEvent, useEffect, useState } from "react";
import {
  createOrganizationFeatureSnapshot,
  getOrganization,
  getOrganizationFeatureSnapshots,
  getOrganizationRisk,
  getOrganizationRiskHistory,
  predictOrganizationRisk,
  predictRiskBySnapshot,
} from "../api/client";
import type {
  OrganizationDetail,
  OrganizationRiskResponse,
  RiskFeatureSnapshotItem,
  RiskPredictionItem,
} from "../types";

type Props = {
  organizationId: string;
  onBack: () => void;
};

type FeatureFormState = {
  period_date: string;
  revenue: string;
  debt_amount: string;
  overdue_days_30: string;
  overdue_days_90: string;
  disputes_count: string;
  transactions_count: string;
  employees_count: string;
};

const initialForm: FeatureFormState = {
  period_date: "2026-06-01",
  revenue: "80000000",
  debt_amount: "35000000",
  overdue_days_30: "18",
  overdue_days_90: "5",
  disputes_count: "3",
  transactions_count: "72",
  employees_count: "40",
};

export function OrganizationDetailPage({ organizationId, onBack }: Props) {
  const [organization, setOrganization] = useState<OrganizationDetail | null>(null);
  const [risk, setRisk] = useState<OrganizationRiskResponse | null>(null);
  const [riskHistory, setRiskHistory] = useState<RiskPredictionItem[]>([]);
  const [snapshots, setSnapshots] = useState<RiskFeatureSnapshotItem[]>([]);
  const [form, setForm] = useState<FeatureFormState>(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function loadData() {
    setLoading(true);
    setError(null);

    Promise.all([
      getOrganization(organizationId),
      getOrganizationRisk(organizationId),
      getOrganizationRiskHistory(organizationId),
      getOrganizationFeatureSnapshots(organizationId),
    ])
      .then(([organizationData, riskData, historyData, snapshotsData]) => {
        setOrganization(organizationData);
        setRisk(riskData);
        setRiskHistory(historyData);
        setSnapshots(snapshotsData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadData();
  }, [organizationId]);

  function updateFormField(field: keyof FeatureFormState, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function toNumber(value: string): number {
    return Number(value || 0);
  }

  function handleCreateSnapshot(event: FormEvent) {
    event.preventDefault();

    createOrganizationFeatureSnapshot(organizationId, {
      period_date: form.period_date,
      revenue: toNumber(form.revenue),
      debt_amount: toNumber(form.debt_amount),
      overdue_days_30: toNumber(form.overdue_days_30),
      overdue_days_90: toNumber(form.overdue_days_90),
      disputes_count: toNumber(form.disputes_count),
      transactions_count: toNumber(form.transactions_count),
      employees_count: toNumber(form.employees_count),
      raw_features: {
        source: "frontend_manual_input",
        comment: "Признаки добавлены через frontend",
      },
    })
      .then(() => loadData())
      .catch((err) => setError(err.message));
  }

  function handlePredictRisk() {
    predictOrganizationRisk(organizationId)
      .then(() => loadData())
      .catch((err) => setError(err.message));
  }

  function handlePredictSnapshot(snapshotId: string) {
    predictRiskBySnapshot(snapshotId)
      .then(() => loadData())
      .catch((err) => setError(err.message));
  }
  if (loading && !organization) {
    return <div>Загрузка карточки организации...</div>;
  }

  if (!organization) {
    return (
      <div className="page">
        <button className="secondary-button" onClick={onBack}>
          ← Назад
        </button>
        <div className="error">Организация не найдена</div>
      </div>
    );
  }

  const latestRisk = risk?.risk_prediction;

  return (
    <div className="page">
      <button className="secondary-button" onClick={onBack}>
        ← Назад к списку
      </button>

      <h1>{organization.name}</h1>

      {error && <div className="error">Ошибка: {error}</div>}

      <section className="section">
        <h2>Карточка организации</h2>

        <div className="details-grid">
          <div>
            <span>БИН</span>
            <strong>{organization.bin ?? "-"}</strong>
          </div>

          <div>
            <span>Отрасль</span>
            <strong>{organization.industry ?? "-"}</strong>
          </div>

          <div>
            <span>Регион</span>
            <strong>{organization.region ?? "-"}</strong>
          </div>

          <div>
            <span>Сегмент</span>
            <strong>{organization.segment ?? "-"}</strong>
          </div>

          <div>
            <span>Годовая выручка</span>
            <strong>{organization.annual_revenue ?? "-"}</strong>
          </div>

          <div>
            <span>Сотрудники</span>
            <strong>{organization.employees_count ?? "-"}</strong>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <h2>Текущий риск</h2>

          <button className="button" onClick={handlePredictRisk}>
            Запустить прогноз
          </button>
        </div>

        {latestRisk ? (
          <div className="risk-box">
            <div>
              <span>Risk score</span>
              <strong>{latestRisk.risk_score}</strong>
            </div>

            <div>
              <span>Risk level</span>
              <strong>{latestRisk.risk_level}</strong>
            </div>

            <div>
              <span>Дата прогноза</span>
              <strong>{new Date(latestRisk.predicted_at).toLocaleString()}</strong>
            </div>
          </div>
        ) : (
          <p>По организации ещё нет рассчитанного риска.</p>
        )}
      </section>

      <section className="section">
        <h2>Добавить признаки риска</h2>

        <form className="feature-form" onSubmit={handleCreateSnapshot}>
          <label>
            Период
            <input
              type="date"
              value={form.period_date}
              onChange={(event) => updateFormField("period_date", event.target.value)}
            />
          </label>

          <label>
            Выручка
            <input
              value={form.revenue}
              onChange={(event) => updateFormField("revenue", event.target.value)}
            />
          </label>

          <label>
            Задолженность
            <input
              value={form.debt_amount}
              onChange={(event) => updateFormField("debt_amount", event.target.value)}
            />
          </label>

          <label>
            Просрочка 30 дней
            <input
              value={form.overdue_days_30}
              onChange={(event) =>
                updateFormField("overdue_days_30", event.target.value)
              }
            />
          </label>

          <label>
            Просрочка 90 дней
            <input
              value={form.overdue_days_90}
              onChange={(event) =>
                updateFormField("overdue_days_90", event.target.value)
              }
            />
          </label>

          <label>
            Споры
            <input
              value={form.disputes_count}
              onChange={(event) =>
                updateFormField("disputes_count", event.target.value)
              }
            />
          </label>

          <label>
            Транзакции
            <input
              value={form.transactions_count}
              onChange={(event) =>
                updateFormField("transactions_count", event.target.value)
              }
            />
          </label>

          <label>
            Сотрудники
            <input
              value={form.employees_count}
              onChange={(event) =>
                updateFormField("employees_count", event.target.value)
              }
            />
          </label>

          <button type="submit">Сохранить признаки</button>
        </form>
      </section>

      <section className="section">
        <h2>Снимки признаков риска</h2>

        <table>
          <thead>
            <tr>
              <th>Период</th>
              <th>Выручка</th>
              <th>Долг</th>
              <th>30 дней</th>
              <th>90 дней</th>
              <th>Споры</th>
              <th>Транзакции</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            {snapshots.map((snapshot) => (
              <tr key={snapshot.id}>
                <td>{snapshot.period_date}</td>
                <td>{snapshot.revenue ?? "-"}</td>
                <td>{snapshot.debt_amount ?? "-"}</td>
                <td>{snapshot.overdue_days_30}</td>
                <td>{snapshot.overdue_days_90}</td>
                <td>{snapshot.disputes_count}</td>
                <td>{snapshot.transactions_count}</td>
                <td>
                  <button onClick={() => handlePredictSnapshot(snapshot.id)}>
                    Прогноз
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="section">
        <h2>История прогнозов риска</h2>

        <table>
          <thead>
            <tr>
              <th>Дата прогноза</th>
              <th>Risk score</th>
              <th>Уровень</th>
            </tr>
          </thead>
          <tbody>
            {riskHistory.map((prediction) => (
              <tr key={prediction.id}>
                <td>{new Date(prediction.predicted_at).toLocaleString()}</td>
                <td>{prediction.risk_score}</td>
                <td>{prediction.risk_level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}