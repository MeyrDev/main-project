import type { RiskExplanation } from "./types";

type Props = {
  explanation: RiskExplanation | null;
  riskScore: string;
  riskLevel: string;
};

export const mapRisk = {
  low: "Низкий",
  medium: "Средний",
  high: "Высокий",
};

export function RiskScoresBlock({ explanation, riskScore, riskLevel }: Props) {
  const scores = explanation?.scores;

  return (
    <div className="risk-scores-grid">
      <div className="risk-score-card">
        <span>Итоговая оценка риска</span>
        <strong>{riskScore}</strong>
      </div>

      <div className="risk-score-card">
        <span>Уровень риска</span>
        <strong>{mapRisk[riskLevel as keyof typeof mapRisk] || riskLevel}</strong>
      </div>

      <div className="risk-score-card">
        <span>Вероятность ML-модели</span>
        <strong>{scores?.model_probability ?? "-"}</strong>
      </div>

      <div className="risk-score-card">
        <span>Доменная оценка</span>
        <strong>{scores?.domain_score ?? "-"}</strong>
      </div>

      <div className="risk-score-card">
        <span>Финальная оценка</span>
        <strong>{scores?.final_score ?? riskScore}</strong>
      </div>
    </div>
  );
}