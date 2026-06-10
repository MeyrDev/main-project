import { useEffect, useState } from "react";
import {
  evaluateValidationDataset,
  getMLModelInfo,
  getTrainingReport,
} from "./api";
import { MLFeaturesTable } from "./MLFeaturesTable";
import { MLModelInfoCard } from "./MLModelInfoCard";
import type {
  ConfusionMatrix,
  MLModelInfo,
  MLTrainingReport,
  MLValidationEvaluation,
} from "./types";
import "./ml.css";

const metricLabels: Record<string, string> = {
  roc_auc: "ROC AUC",
  pr_auc: "PR AUC",
  f1: "F1",
  precision: "Precision",
  recall: "Recall",
  accuracy: "Accuracy",
  brier_score: "Brier score",
};

export function MLModelPage() {
  const [model, setModel] = useState<MLModelInfo | null>(null);
  const [report, setReport] = useState<MLTrainingReport | null>(null);
  const [evaluation, setEvaluation] = useState<MLValidationEvaluation | null>(
    null
  );
  const [modelError, setModelError] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);

  function loadModelInfo() {
    getMLModelInfo()
      .then((data) => {
        setModel(data);
        setModelError(null);
      })
      .catch((err) => setModelError(err.message));

    getTrainingReport()
      .then((data) => {
        setReport(data);
        setReportError(null);
      })
      .catch((err) => setReportError(err.message));
  }

  function runValidationEvaluation() {
    setIsEvaluating(true);
    setEvaluationError(null);

    evaluateValidationDataset()
      .then((data) => {
        setEvaluation(data);
        setReport((current) =>
          current
            ? {
                ...current,
                metrics: data.metrics,
                confusion_matrix: data.confusion_matrix,
                validation_rows: data.validation_rows,
                feature_columns: data.feature_columns,
                target_column: data.target_column,
                artifact_exists: data.artifact_exists,
                artifact_size_bytes: data.artifact_size_bytes,
                artifact_modified_at: data.artifact_modified_at,
              }
            : current
        );
      })
      .catch((err) => setEvaluationError(err.message))
      .finally(() => setIsEvaluating(false));
  }

  useEffect(() => {
    loadModelInfo();
  }, []);

  const activeMetrics = evaluation?.metrics ?? report?.metrics ?? model?.metrics ?? {};
  const activeMatrix = getConfusionMatrix(
    evaluation?.confusion_matrix ?? report?.confusion_matrix
  );
  const featureColumns =
    report?.feature_columns?.length ? report.feature_columns : model?.feature_columns ?? [];

  return (
    <div className="page">
      <div className="section-header">
        <h1>ML-модель</h1>

        <button className="button" onClick={loadModelInfo}>
          Обновить
        </button>
      </div>

      {modelError && (
        <div className="error">
          Ошибка загрузки ML-модели: {modelError}
          <br />
          Если artifact не найден, выполни:
          <pre>docker compose run --rm app python -m app.ml.train_model</pre>
        </div>
      )}

      {reportError && (
        <div className="error">Ошибка загрузки отчета обучения: {reportError}</div>
      )}

      {evaluationError && (
        <div className="error">
          Ошибка проверки validation_dataset: {evaluationError}
        </div>
      )}

      {report && (
        <section className="section">
          <div className="ml-proof-header">
            <div>
              <h2>Результаты обучения</h2>
            </div>

            <button
              className="button"
              disabled={isEvaluating}
              onClick={runValidationEvaluation}
            >
              {isEvaluating
                ? "Проверка..."
                : "Проверить модель на validation_dataset"}
            </button>
          </div>

          <div className="ml-proof-grid">
            <div className="ml-info-card">
              <span>Статус модели</span>
              <strong>
                {report.trained ? "Модель обучена" : "Модель не обучена"}
              </strong>
              <small>{report.message ?? "Отчет обучения найден"}</small>
            </div>

            <div className="ml-info-card">
              <span>Дата обучения</span>
              <strong>{formatDate(report.trained_at)}</strong>
              <small>Версия: {formatValue(report.model_version)}</small>
            </div>

            <div className="ml-info-card">
              <span>Алгоритм</span>
              <strong>{formatValue(report.algorithm)}</strong>
            </div>

            <div className="ml-info-card">
              <span>Artifact</span>
              <strong>
                {report.artifact_exists
                  ? "risk_model.joblib найден"
                  : "artifact не найден"}
              </strong>
              <small>
                {formatValue(report.artifact_path)} ·{" "}
                {formatBytes(report.artifact_size_bytes)}
              </small>
            </div>

            <div className="ml-info-card wide">
              <span>Использованные датасеты</span>
              <div className="ml-datasets">
                <div>
                  <strong>{formatValue(report.train_dataset_path)}</strong>
                  <small>Строк: {formatValue(report.train_rows)}</small>
                  <Distribution
                    distribution={report.train_target_distribution}
                    label="Target train"
                  />
                </div>

                <div>
                  <strong>{formatValue(report.validation_dataset_path)}</strong>
                  <small>Строк: {formatValue(report.validation_rows)}</small>
                  <Distribution
                    distribution={report.validation_target_distribution}
                    label="Target validation"
                  />
                </div>
              </div>
            </div>

            <div className="ml-info-card wide">
              <span>Метрики validation</span>
              <div className="ml-metric-grid">
                {Object.entries(metricLabels).map(([metric, label]) => (
                  <div className="ml-metric" key={metric}>
                    <small>{label}</small>
                    <strong>{formatValue(activeMetrics[metric])}</strong>
                  </div>
                ))}
              </div>

              {evaluation && (
                <small>
                  Свежая проверка выполнена: {formatDate(evaluation.evaluated_at)}
                </small>
              )}
            </div>

            <div className="ml-info-card">
              <span>Матрица ошибок</span>
              <div className="ml-confusion">
                <div>
                  <small>TN</small>
                  <strong>{formatValue(activeMatrix?.[0]?.[0])}</strong>
                </div>
                <div>
                  <small>FP</small>
                  <strong>{formatValue(activeMatrix?.[0]?.[1])}</strong>
                </div>
                <div>
                  <small>FN</small>
                  <strong>{formatValue(activeMatrix?.[1]?.[0])}</strong>
                </div>
                <div>
                  <small>TP</small>
                  <strong>{formatValue(activeMatrix?.[1]?.[1])}</strong>
                </div>
              </div>
            </div>

            <div className="ml-info-card wide">
              <span>Признаки модели</span>
              <div className="ml-feature-list">
                {featureColumns.map((column) => (
                  <code key={column}>{column}</code>
                ))}
              </div>
            </div>
          </div>
        </section>
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
        </>
      )}
    </div>
  );
}

function Distribution({
  distribution,
  label,
}: {
  distribution: Record<string, number | string>;
  label: string;
}) {
  return (
    <div className="ml-distribution" aria-label={label}>
      {Object.entries(distribution).map(([target, count]) => (
        <small key={target}>
          target {target}: {count}
        </small>
      ))}
    </div>
  );
}

function getConfusionMatrix(
  value: ConfusionMatrix | number[][] | null | undefined
): number[][] | null {
  if (!value) return null;
  if (Array.isArray(value)) return value;
  return value.matrix;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "нет данных";
  if (typeof value === "number") return String(value);
  return String(value);
}

function formatBytes(value: number | null | undefined): string {
  if (!value) return "нет данных";
  return `${(value / 1024).toFixed(1)} KB`;
}

function formatDate(value: string | null | undefined): string {
  if (!value) return "нет данных";

  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
