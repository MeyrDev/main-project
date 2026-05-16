import { useEffect, useState } from "react";
import { getOrganizations } from "../../api/client";
import type { OrganizationListItem } from "../../types";
import { getOrganizationRisk } from "./api";
import { RiskFactorList } from "./RiskFactorList";
import { RiskRecommendations } from "./RiskRecommendations";
import { RiskScoresBlock } from "./RiskScoresBlock";
import type { OrganizationRiskResponse } from "./types";
import "./riskExplanation.css";

export function RiskExplanationPage() {
  const [organizations, setOrganizations] = useState<OrganizationListItem[]>([]);
  const [selectedOrganizationId, setSelectedOrganizationId] = useState("");
  const [riskData, setRiskData] = useState<OrganizationRiskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOrganizations({ limit: 200, offset: 0 })
      .then((response) => {
        setOrganizations(response.items);

        if (response.items.length > 0) {
          setSelectedOrganizationId(response.items[0].id);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!selectedOrganizationId) {
      return;
    }

    loadRiskExplanation(selectedOrganizationId);
  }, [selectedOrganizationId]);

  function loadRiskExplanation(organizationId: string) {
    getOrganizationRisk(organizationId)
      .then((data) => {
        setRiskData(data);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }

  const prediction = riskData?.risk_prediction ?? null;
  const explanation = prediction?.explanation ?? null;
  const mainFactors = explanation?.main_factors ?? [];
  const recommendations = prediction?.recommendations?.actions ?? [];

  return (
    <div className="page">
      <h1>Объяснение риска</h1>

      {error && <div className="error">Ошибка: {error}</div>}

      <section className="section">
        <h2>Выбор организации</h2>

        <select
          className="risk-organization-select"
          value={selectedOrganizationId}
          onChange={(event) => setSelectedOrganizationId(event.target.value)}
        >
          {organizations.map((organization) => (
            <option key={organization.id} value={organization.id}>
              {organization.name} {organization.bin ? `(${organization.bin})` : ""}
            </option>
          ))}
        </select>
      </section>

      {!prediction && (
        <section className="section">
          <h2>Риск ещё не рассчитан</h2>
          <p>
            Для выбранной организации пока нет сохранённого прогноза риска.
            Сначала добавь признаки риска и запусти прогноз.
          </p>
        </section>
      )}

      {prediction && (
        <>
          <section className="section">
            <h2>Итоговая оценка риска</h2>

            <RiskScoresBlock
              explanation={explanation}
              riskScore={prediction.risk_score}
              riskLevel={prediction.risk_level}
            />

            <p className="risk-date">
              Дата прогноза:{" "}
              <strong>{new Date(prediction.predicted_at).toLocaleString()}</strong>
            </p>
          </section>

          <section className="section">
            <h2>Главные факторы риска</h2>

            <RiskFactorList factors={mainFactors} />
          </section>

          <section className="section">
            <h2>Рекомендации</h2>

            <RiskRecommendations actions={recommendations} />
          </section>

          <section className="section">
            <h2>Использованные признаки</h2>

            <pre className="risk-json">
              {JSON.stringify(explanation?.features ?? {}, null, 2)}
            </pre>
          </section>

          <section className="section">
            <h2>Техническая информация модели</h2>

            <div className="risk-model-info">
              <div>
                <span>Метод</span>
                <strong>{explanation?.method ?? "-"}</strong>
              </div>

              <div>
                <span>Модель</span>
                <strong>{explanation?.model_name ?? "-"}</strong>
              </div>

              <div>
                <span>Версия</span>
                <strong>{explanation?.version ?? "-"}</strong>
              </div>

              <div>
                <span>Алгоритм</span>
                <strong>{explanation?.algorithm ?? "-"}</strong>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}