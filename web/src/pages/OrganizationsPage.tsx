import { useEffect, useState } from "react";
import { getOrganizations } from "../api/client";
import type { OrganizationListItem } from "../types";

export function OrganizationsPage() {
  const [items, setItems] = useState<OrganizationListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
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

  const canGoBack = offset > 0;
  const canGoNext = offset + limit < total;

  return (
    <div className="page">
      <h1>Организации</h1>

      <div className="toolbar">
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Поиск по названию или БИН"
        />

        <button onClick={() => loadOrganizations(0)}>Найти</button>
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
            </tr>
          ))}
        </tbody>
      </table>

      <div className="pagination">
        <button
          disabled={!canGoBack}
          onClick={() => loadOrganizations(Math.max(offset - limit, 0))}
        >
          Назад
        </button>

        <span>
          Показано {items.length} из {total}
        </span>

        <button
          disabled={!canGoNext}
          onClick={() => loadOrganizations(offset + limit)}
        >
          Вперёд
        </button>
      </div>
    </div>
  );
}