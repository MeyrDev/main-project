type Props = {
  featureColumns: string[];
};

const featureDescriptions: Record<string, string> = {
  revenue: "Выручка организации за период",
  debt_amount: "Сумма задолженности",
  debt_ratio: "Доля задолженности относительно выручки",
  overdue_days_30: "Просрочка в 30-дневном окне",
  overdue_days_90: "Просрочка в 90-дневном окне",
  disputes_count: "Количество спорных ситуаций",
  transactions_count: "Количество транзакций",
  employees_count: "Количество сотрудников",
};

export function MLFeaturesTable({ featureColumns }: Props) {
  return (
    <table>
      <thead>
        <tr>
          <th>Признак</th>
          <th>Описание</th>
        </tr>
      </thead>

      <tbody>
        {featureColumns.map((feature) => (
          <tr key={feature}>
            <td>{feature}</td>
            <td>{featureDescriptions[feature] ?? "Входной признак ML-модели"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}