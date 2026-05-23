type Props = {
  content: Record<string, unknown>;
};

function asArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? (value as Record<string, unknown>[]) : [];
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  return String(value);
}

export function PortfolioAnalyticsReportView({ content }: Props) {
  const riskDistribution = asArray(content.risk_distribution);

  return (
    <div className="report-view">
      <section className="report-block">
        <h3>Сводные показатели</h3>

        <div className="report-grid">
          <div>
            <span>Количество организаций</span>
            <strong>{formatValue(content.organizations_count)}</strong>
          </div>

          <div>
            <span>Количество прогнозов</span>
            <strong>{formatValue(content.predictions_count)}</strong>
          </div>
        </div>
      </section>

      <section className="report-block">
        <h3>Распределение по уровням риска</h3>

        {riskDistribution.length === 0 ? (
          <p>Нет данных для распределения риска.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Уровень риска</th>
                <th>Количество</th>
              </tr>
            </thead>

            <tbody>
              {riskDistribution.map((item) => (
                <tr key={formatValue(item.risk_level)}>
                  <td>{formatValue(item.risk_level)}</td>
                  <td>{formatValue(item.count)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}