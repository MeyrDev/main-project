type Props = {
  content: Record<string, unknown>;
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function asArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? (value as Record<string, unknown>[]) : [];
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

export function RiskSummaryReportView({ content }: Props) {
  const organization = asRecord(content.organization);
  const latestRisk = asRecord(content.latest_risk);
  const riskHistory = asArray(content.risk_history);
  const featureSnapshots = asArray(content.feature_snapshots);
  const conclusion = formatValue(content.conclusion);

  return (
    <div className="report-view">
      <section className="report-block">
        <h3>Организация</h3>

        <div className="report-grid">
          <div>
            <span>Название</span>
            <strong>{formatValue(organization.name)}</strong>
          </div>

          <div>
            <span>БИН</span>
            <strong>{formatValue(organization.bin)}</strong>
          </div>

          <div>
            <span>Отрасль</span>
            <strong>{formatValue(organization.industry)}</strong>
          </div>

          <div>
            <span>Регион</span>
            <strong>{formatValue(organization.region)}</strong>
          </div>

          <div>
            <span>Сегмент</span>
            <strong>{formatValue(organization.segment)}</strong>
          </div>

          <div>
            <span>Сотрудники</span>
            <strong>{formatValue(organization.employees_count)}</strong>
          </div>
        </div>
      </section>

      <section className="report-block">
        <h3>Последняя оценка риска</h3>

        {Object.keys(latestRisk).length > 0 ? (
          <div className="report-risk-grid">
            <div>
              <span>Risk score</span>
              <strong>{formatValue(latestRisk.risk_score)}</strong>
            </div>

            <div>
              <span>Уровень риска</span>
              <strong>{formatValue(latestRisk.risk_level)}</strong>
            </div>

            <div>
              <span>Дата прогноза</span>
              <strong>{formatValue(latestRisk.predicted_at)}</strong>
            </div>
          </div>
        ) : (
          <p>По организации ещё нет рассчитанного риска.</p>
        )}
      </section>

      <section className="report-block">
        <h3>Вывод</h3>
        <p className="report-conclusion">{conclusion}</p>
      </section>

      <section className="report-block">
        <h3>История прогнозов риска</h3>

        {riskHistory.length === 0 ? (
          <p>История прогнозов отсутствует.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Дата</th>
                <th>Risk score</th>
                <th>Уровень</th>
              </tr>
            </thead>

            <tbody>
              {riskHistory.map((item) => (
                <tr key={formatValue(item.id)}>
                  <td>{formatValue(item.predicted_at)}</td>
                  <td>{formatValue(item.risk_score)}</td>
                  <td>{formatValue(item.risk_level)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="report-block">
        <h3>Снимки признаков риска</h3>

        {featureSnapshots.length === 0 ? (
          <p>Снимки признаков отсутствуют.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Период</th>
                <th>Выручка</th>
                <th>Долг</th>
                <th>Просрочка 30</th>
                <th>Просрочка 90</th>
                <th>Споры</th>
                <th>Транзакции</th>
              </tr>
            </thead>

            <tbody>
              {featureSnapshots.map((item) => (
                <tr key={formatValue(item.id)}>
                  <td>{formatValue(item.period_date)}</td>
                  <td>{formatValue(item.revenue)}</td>
                  <td>{formatValue(item.debt_amount)}</td>
                  <td>{formatValue(item.overdue_days_30)}</td>
                  <td>{formatValue(item.overdue_days_90)}</td>
                  <td>{formatValue(item.disputes_count)}</td>
                  <td>{formatValue(item.transactions_count)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}