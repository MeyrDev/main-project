import type { AuditLogItem } from "./types";

type Props = {
  items: AuditLogItem[];
};

export function AuditLogsTable({ items }: Props) {
  if (items.length === 0) {
    return <p>Записи аудита не найдены.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Дата</th>
          <th>Действие</th>
          <th>Сущность</th>
          <th>ID сущности</th>
          <th>Детали</th>
        </tr>
      </thead>

      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{new Date(item.created_at).toLocaleString()}</td>
            <td>{item.action}</td>
            <td>{item.entity_type ?? "-"}</td>
            <td className="audit-entity-id">{item.entity_id ?? "-"}</td>
            <td>
              <pre className="audit-details">
                {JSON.stringify(item.details ?? {}, null, 2)}
              </pre>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}