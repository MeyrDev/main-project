type Props = {
  content: Record<string, unknown>;
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  if (typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }

  return String(value);
}

export function ModelQualityReportView({ content }: Props) {
  const model = asRecord(content.model);
  const metrics = asRecord(model.metrics);

  if (Object.keys(model).length === 0) {
    return <p>Информация о ML-модели отсутствует.</p>;
  }

  return (
    <div className="report-view">
      <section className="report-block">
        <h3>ML-модель</h3>

        <div className="report-grid">
          <div>
            <span>Название</span>
            <strong>{formatValue(model.name)}</strong>
          </div>

          <div>
            <span>Версия</span>
            <strong>{formatValue(model.version)}</strong>
          </div>

          <div>
            <span>Алгоритм</span>
            <strong>{formatValue(model.algorithm_name)}</strong>
          </div>

          <div>
            <span>Целевая переменная</span>
            <strong>{formatValue(model.target_name)}</strong>
          </div>

          <div className="wide">
            <span>Artifact</span>
            <strong>{formatValue(model.artifact_path)}</strong>
          </div>
        </div>
      </section>

      <section className="report-block">
        <h3>Метрики качества</h3>

        {Object.keys(metrics).length === 0 ? (
          <p>Метрики отсутствуют.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Метрика</th>
                <th>Значение</th>
              </tr>
            </thead>

            <tbody>
              {Object.entries(metrics).map(([key, value]) => (
                <tr key={key}>
                  <td>{key}</td>
                  <td>{formatValue(value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}