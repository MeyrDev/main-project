import { useEffect, useState, type ChangeEvent, type SyntheticEvent } from "react";
import {
  createOrganizationFeatureSnapshot,
  getOrganization,
  getOrganizationFeatureSnapshots,
  getOrganizationRisk,
  getOrganizationRiskHistory,
  predictOrganizationRisk,
  predictRiskBySnapshot,
  updateOrganization
} from "../api/client";
import type {
  OrganizationDetail,
  OrganizationRiskResponse,
  RiskFeatureSnapshotItem,
  RiskPredictionItem,
} from "../types";
import { toNumber, toNumberOrNull, toStringOrNull } from "../utils";
import { Deals } from "../features/Deals";

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

type OrganizationEditFormState = {
  bin: string;
  name: string;
  industry: string;
  region: string;
  segment: string;
  annual_revenue: string;
  employees_count: string;
  description: string;
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
  const [isEditingOrganization, setIsEditingOrganization] = useState(false);
  const [editForm, setEditForm] = useState<OrganizationEditFormState>({
    bin: "",
    name: "",
    industry: "",
    region: "",
    segment: "",
    annual_revenue: "",
    employees_count: "",
    description: "",
  });
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

        setEditForm({
          bin: organizationData.bin ?? "",
          name: organizationData.name,
          industry: organizationData.industry ?? "",
          region: organizationData.region ?? "",
          segment: organizationData.segment ?? "",
          annual_revenue: organizationData.annual_revenue ?? "",
          employees_count: organizationData.employees_count
            ? String(organizationData.employees_count)
            : "",
          description: organizationData.description ?? "",
        });
      })
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

  function updateEditFormField(
    field: keyof OrganizationEditFormState,
    value: string
  ) {
    setEditForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handleUpdateOrganization(event: SyntheticEvent) {
    event.preventDefault();

    updateOrganization(organizationId, {
      bin: toStringOrNull(editForm.bin),
      name: editForm.name.trim(),
      industry: toStringOrNull(editForm.industry),
      region: toStringOrNull(editForm.region),
      segment: toStringOrNull(editForm.segment),
      status: "active",
      annual_revenue: toNumberOrNull(editForm.annual_revenue),
      employees_count: toNumberOrNull(editForm.employees_count),
      description: toStringOrNull(editForm.description),
    })
    .then((updatedOrganization) => {
      setOrganization(updatedOrganization);
      setIsEditingOrganization(false);
      loadData();
    })
    .catch((err) => setError(err.message));
  }


  function handleCreateSnapshot(event: ChangeEvent<HTMLFormElement>) {
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
        <div className="section-header">
          <h2>Карточка организации</h2>

          <button onClick={() => setIsEditingOrganization((value) => !value)}>
            {isEditingOrganization ? "Отмена" : "Редактировать"}
          </button>
        </div>

        {!isEditingOrganization ? (
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

            <div>
              <span>Описание</span>
              <strong>{organization.description ?? "-"}</strong>
            </div>
          </div>
        ) : (
          <form className="organization-form" onSubmit={handleUpdateOrganization}>
            <label>
              БИН
              <input
                value={editForm.bin}
                onChange={(event) => updateEditFormField("bin", event.target.value)}
                placeholder="12 цифр"
              />
            </label>

            <label>
              Название
              <input
                value={editForm.name}
                onChange={(event) => updateEditFormField("name", event.target.value)}
                required
              />
            </label>

            <label>
              Отрасль
              <input
                value={editForm.industry}
                onChange={(event) =>
                  updateEditFormField("industry", event.target.value)
                }
              />
            </label>

            <label>
              Регион
              <input
                value={editForm.region}
                onChange={(event) => updateEditFormField("region", event.target.value)}
              />
            </label>

            <label>
              Сегмент
              <input
                value={editForm.segment}
                onChange={(event) =>
                  updateEditFormField("segment", event.target.value)
                }
              />
            </label>

            <label>
              Годовая выручка
              <input
                value={editForm.annual_revenue}
                onChange={(event) =>
                  updateEditFormField("annual_revenue", event.target.value)
                }
              />
            </label>

            <label>
              Сотрудники
              <input
                value={editForm.employees_count}
                onChange={(event) =>
                  updateEditFormField("employees_count", event.target.value)
                }
              />
            </label>

            <label>
              Описание
              <input
                value={editForm.description}
                onChange={(event) =>
                  updateEditFormField("description", event.target.value)
                }
              />
            </label>

            <button type="submit">Сохранить изменения</button>
          </form>
        )}
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

      <Deals 
        organizationId={organizationId}
        loadData={loadData}
        setError={setError}
      />

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