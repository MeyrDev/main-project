import type { AuditLogFilters } from "./types";

type Props = {
  filters: AuditLogFilters;
  onChange: (filters: AuditLogFilters) => void;
  onApply: () => void;
  onReset: () => void;
};

export function AuditFilters({ filters, onChange, onApply, onReset }: Props) {
  return (
    <div className="audit-filters">
      <label>
        Действие
        <select
          value={filters.action ?? ""}
          onChange={(event) =>
            onChange({
              ...filters,
              action: event.target.value || undefined,
            })
          }
        >
          <option value="">Все действия</option>
          <option value="organization.created">organization.created</option>
          <option value="organization.updated">organization.updated</option>
          <option value="feature_snapshot.created">
            feature_snapshot.created
          </option>
          <option value="risk_prediction.created">
            risk_prediction.created
          </option>
          <option value="deal.created">deal.created</option>
          <option value="deal.updated">deal.updated</option>
          <option value="interaction.created">interaction.created</option>
          <option value="interaction.updated">interaction.updated</option>
          <option value="report.created">report.created</option>
        </select>
      </label>

      <label>
        Тип сущности
        <select
          value={filters.entity_type ?? ""}
          onChange={(event) =>
            onChange({
              ...filters,
              entity_type: event.target.value || undefined,
            })
          }
        >
          <option value="">Все сущности</option>
          <option value="organization">organization</option>
          <option value="risk_feature_snapshot">risk_feature_snapshot</option>
          <option value="risk_prediction">risk_prediction</option>
          <option value="deal">deal</option>
          <option value="interaction">interaction</option>
          <option value="report">report</option>
        </select>
      </label>

      <button type="button" onClick={onApply}>
        Применить
      </button>

      <button type="button" className="secondary-audit-button" onClick={onReset}>
        Сбросить
      </button>
    </div>
  );
}