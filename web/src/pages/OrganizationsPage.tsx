import { useEffect, useState, type SyntheticEvent } from "react";
import { createOrganization, getOrganizations } from "../api/client";
import type { OrganizationCreate, OrganizationListItem } from "../types";

type Props = {
  onSelectOrganization: (id: string) => void;
};

type OrganizationFormState = {
  bin: string;
  name: string;
  industry: string;
  region: string;
  segment: string;
  annual_revenue: string;
  employees_count: string;
  description: string;
};

const initialForm: OrganizationFormState = {
  bin: "",
  name: "",
  industry: "",
  region: "",
  segment: "",
  annual_revenue: "",
  employees_count: "",
  description: "",
};

export function OrganizationsPage({ onSelectOrganization }: Props) {
  const [items, setItems] = useState<OrganizationListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [form, setForm] = useState<OrganizationFormState>(initialForm);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const limit = 10;

  function loadOrganizations(nextOffset = offset) {
    getOrganizations({
      search,
      limit,
      offset: nextOffset,
    })
      .then((response) => {
        setItems(response.items);
        setTotal(response.total);
        setOffset(response.offset);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    loadOrganizations(0);
  }, []);

  function updateFormField(field: keyof OrganizationFormState, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function toNumberOrNull(value: string): number | null {
    if (!value.trim()) {
      return null;
    }

    return Number(value);
  }

  function toStringOrNull(value: string): string | null {
    const trimmed = value.trim();

    return trimmed ? trimmed : null;
  }

  function handleCreateOrganization(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const payload: OrganizationCreate = {
      bin: toStringOrNull(form.bin),
      name: form.name.trim(),
      industry: toStringOrNull(form.industry),
      region: toStringOrNull(form.region),
      segment: toStringOrNull(form.segment),
      status: "active",
      annual_revenue: toNumberOrNull(form.annual_revenue),
      employees_count: toNumberOrNull(form.employees_count),
      description: toStringOrNull(form.description),
    };

    createOrganization(payload)
      .then((organization) => {
        setForm(initialForm);
        setIsFormVisible(false);
        loadOrganizations(0);
        onSelectOrganization(organization.id);
      })
      .catch((err) => setError(err.message));
  }

  const canGoBack = offset > 0;
  const canGoNext = offset + limit < total;

  return (
    <div className="page">
      <div className="section-header">
        <h1>Организации</h1>

        <button className="button" onClick={() => setIsFormVisible((value) => !value)}>
          {isFormVisible ? "Скрыть форму" : "Создать организацию"}
        </button>
      </div>

      {isFormVisible && (
        <section className="section">
          <h2>Новая организация</h2>

          <form className="organization-form" onSubmit={handleCreateOrganization}>
            <label>
              БИН
              <input
                value={form.bin}
                onChange={(event) => updateFormField("bin", event.target.value)}
                placeholder="12 цифр"
              />
            </label>

            <label>
              Название
              <input
                value={form.name}
                onChange={(event) => updateFormField("name", event.target.value)}
                required
                placeholder="ТОО Demo Company"
              />
            </label>

            <label>
              Отрасль
              <input
                value={form.industry}
                onChange={(event) => updateFormField("industry", event.target.value)}
                placeholder="IT-услуги"
              />
            </label>

            <label>
              Регион
              <input
                value={form.region}
                onChange={(event) => updateFormField("region", event.target.value)}
                placeholder="Алматы"
              />
            </label>

            <label>
              Сегмент
              <input
                value={form.segment}
                onChange={(event) => updateFormField("segment", event.target.value)}
                placeholder="Малый бизнес"
              />
            </label>

            <label>
              Годовая выручка
              <input
                value={form.annual_revenue}
                onChange={(event) =>
                  updateFormField("annual_revenue", event.target.value)
                }
                placeholder="50000000"
              />
            </label>

            <label>
              Сотрудники
              <input
                value={form.employees_count}
                onChange={(event) =>
                  updateFormField("employees_count", event.target.value)
                }
                placeholder="25"
              />
            </label>

            <label>
              Описание
              <input
                value={form.description}
                onChange={(event) =>
                  updateFormField("description", event.target.value)
                }
                placeholder="Краткое описание организации"
              />
            </label>

            <button className="button" type="submit">Сохранить организацию</button>
          </form>
        </section>
      )}

      <div className="toolbar">
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Поиск по названию или БИН"
        />

        <button className="button" onClick={() => loadOrganizations(0)}>
          Найти
        </button>
      </div>

      {error && <div className="error">Ошибка загрузки: {error}</div>}

      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>БИН</th>
            <th>Отрасль</th>
            <th>Регион</th>
            <th>Сегмент</th>
            <th>Выручка</th>
            <th>Сотрудники</th>
            <th>Действия</th>
          </tr>
        </thead>

        <tbody>
          {items.map((organization) => (
            <tr key={organization.id}>
              <td>{organization.name}</td>
              <td>{organization.bin ?? "-"}</td>
              <td>{organization.industry ?? "-"}</td>
              <td>{organization.region ?? "-"}</td>
              <td>{organization.segment ?? "-"}</td>
              <td>{organization.annual_revenue ?? "-"}</td>
              <td>{organization.employees_count ?? "-"}</td>
              <td>
                <button className="button" onClick={() => onSelectOrganization(organization.id)}>
                  Открыть
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="pagination">
        <button
          className="button"
          disabled={!canGoBack}
          onClick={() => loadOrganizations(Math.max(offset - limit, 0))}
        >
          Назад
        </button>

        <span>
          Показано {items.length} из {total}
        </span>

        <button
          className="button"
          disabled={!canGoNext}
          onClick={() => loadOrganizations(offset + limit)}
        >
          Вперёд
        </button>
      </div>
    </div>
  );
}