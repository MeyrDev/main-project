import { useEffect, useState } from "react";
import { getMLModelInfo } from "./api";
import { MLFeaturesTable } from "./MLFeaturesTable";
import { MLModelInfoCard } from "./MLModelInfoCard";
import type { MLModelInfo } from "./types";
import "./ml.css";

export function MLModelPage() {
  const [model, setModel] = useState<MLModelInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  function loadModelInfo() {
    getMLModelInfo()
      .then((data) => {
        setModel(data);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    loadModelInfo();
  }, []);

  return (
    <div className="page">
      <div className="section-header">
        <h1>ML-модель</h1>

        <button onClick={loadModelInfo}>Обновить</button>
      </div>

      {error && (
        <div className="error">
          Ошибка загрузки ML-модели: {error}
          <br />
          Если artifact не найден, выполни:
          <pre>docker compose run --rm app python -m app.ml.train_model</pre>
        </div>
      )}

      {model && (
        <>
          <section className="section">
            <h2>Информация о модели</h2>

            <MLModelInfoCard model={model} />
          </section>

          <section className="section">
            <h2>Метрики качества</h2>

            <table>
              <thead>
                <tr>
                  <th>Метрика</th>
                  <th>Значение</th>
                </tr>
              </thead>

              <tbody>
                {Object.entries(model.metrics).map(([metric, value]) => (
                  <tr key={metric}>
                    <td>{metric}</td>
                    <td>{String(value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="section">
            <h2>Используемые признаки</h2>

            <MLFeaturesTable featureColumns={model.feature_columns} />
          </section>

          <section className="section">
            <h2>Назначение ML-модуля</h2>

            <p>
              ML-модуль использует финансово-операционные признаки организации
              из таблицы <strong>Снимки признаков риска</strong> и рассчитывает
              вероятность риска. Результат сохраняется в таблицу{" "}
              <strong>Результаты прогнозирования риска</strong>.
            </p>

            <pre className="ml-flow">
                Снимки признаков риска
                        →
                ML-модель
                        →
                Оценка риска / уровень риска
                        →
                Результаты прогнозирования риска
            </pre>
          </section>
        </>
      )}
    </div>
  );
}