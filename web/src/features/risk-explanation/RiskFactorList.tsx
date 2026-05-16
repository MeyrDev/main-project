import type { RiskFactor } from "./types";

type Props = {
  factors: RiskFactor[];
};

function translateImpact(impact: string): string {
  if (impact === "low") return "низкое влияние";
  if (impact === "medium") return "среднее влияние";
  if (impact === "high") return "высокое влияние";

  return impact;
}

export function RiskFactorList({ factors }: Props) {
  if (factors.length === 0) {
    return <p>Факторы риска не указаны.</p>;
  }

  return (
    <div className="risk-factors-list">
      {factors.map((factor) => (
        <div className="risk-factor-card" key={`${factor.factor}-${factor.value}`}>
          <div className="risk-factor-header">
            <strong>{factor.factor}</strong>
            <span className={`impact impact-${factor.impact}`}>
              {translateImpact(factor.impact)}
            </span>
          </div>

          <p>{factor.description}</p>

          <div className="risk-factor-value">
            Значение: <strong>{String(factor.value ?? "Не указано")}</strong>
          </div>
        </div>
      ))}
    </div>
  );
}