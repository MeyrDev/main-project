import { useState, type SyntheticEvent } from "react";
import type { OrganizationListItem } from "../../types";
import type { ReportCreate, ReportType } from "./types";

type Props = {
  organizations: OrganizationListItem[];
  onSubmit: (payload: ReportCreate) => void;
};

type FormState = {
  title: string;
  report_type: ReportType;
  organization_id: string;
  period: string;
};

const initialForm: FormState = {
  title: "Отчёт по уровню риска организации",
  report_type: "risk_summary",
  organization_id: "",
  period: "2026-05",
};

export function ReportForm({ organizations, onSubmit }: Props) {
  const [form, setForm] = useState<FormState>(initialForm);

  function updateField(field: keyof FormState, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const needsOrganization =
      form.report_type === "risk_summary" ||
      form.report_type === "organization_card";

    onSubmit({
      title: form.title.trim(),
      report_type: form.report_type,
      organization_id: needsOrganization ? form.organization_id || null : null,
      created_by_id: null,
      parameters: {
        period: form.period,
        include_risk_history: true,
        include_recommendations: true,
      },
    });
  }

  const needsOrganization =
    form.report_type === "risk_summary" ||
    form.report_type === "organization_card";

  return (
    <form className="report-form" onSubmit={handleSubmit}>
      <label>
        Название отчёта
        <input
          value={form.title}
          onChange={(event) => updateField("title", event.target.value)}
          required
        />
      </label>

      <label>
        Тип отчёта
        <select
          value={form.report_type}
          onChange={(event) =>
            updateField("report_type", event.target.value as ReportType)
          }
        >
          <option value="risk_summary">Сводка риска</option>
          <option value="organization_card">Карточка организации</option>
          <option value="portfolio_analytics">Портфельная аналитика</option>
          <option value="model_quality">Качество ML-модели</option>
        </select>
      </label>

      {needsOrganization && (
        <label>
          Организация
          <select
            value={form.organization_id}
            onChange={(event) =>
              updateField("organization_id", event.target.value)
            }
            required
          >
            <option value="">Выберите организацию</option>

            {organizations.map((organization) => (
              <option key={organization.id} value={organization.id}>
                {organization.name}
              </option>
            ))}
          </select>
        </label>
      )}

      <label>
        Период
        <input
          value={form.period}
          onChange={(event) => updateField("period", event.target.value)}
          placeholder="2026-05"
        />
      </label>

      <button className="button" type="submit">Создать отчёт</button>
    </form>
  );
}