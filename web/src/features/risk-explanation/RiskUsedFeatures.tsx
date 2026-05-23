type Props = {
  features: Record<string, unknown>;
};

type FeatureMeta = {
  label: string;
  description: string;
  unit?: string;
  format?: "money" | "number" | "percent";
};

const featureMeta: Record<string, FeatureMeta> = {
  revenue: {
    label: "Выручка",
    description: "Объём выручки организации за анализируемый период",
    unit: "KZT",
    format: "money",
  },
  debt_amount: {
    label: "Задолженность",
    description: "Общая сумма долговой нагрузки организации",
    unit: "KZT",
    format: "money",
  },
  debt_ratio: {
    label: "Доля задолженности",
    description: "Отношение задолженности к выручке",
    format: "percent",
  },
  overdue_days_30: {
    label: "Просрочка 30 дней",
    description: "Количество дней просрочки в 30-дневном окне",
    unit: "дней",
    format: "number",
  },
  overdue_days_90: {
    label: "Просрочка 90 дней",
    description: "Количество дней просрочки в 90-дневном окне",
    unit: "дней",
    format: "number",
  },
  disputes_count: {
    label: "Спорные ситуации",
    description: "Количество спорных или конфликтных ситуаций",
    unit: "шт.",
    format: "number",
  },
  transactions_count: {
    label: "Количество транзакций",
    description: "Операционная активность организации за период",
    unit: "шт.",
    format: "number",
  },
  employees_count: {
    label: "Количество сотрудников",
    description: "Размер организации по численности персонала",
    unit: "чел.",
    format: "number",
  },
};

function normalizeNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  const numberValue = Number(value);

  return Number.isFinite(numberValue) ? numberValue : null;
}

function formatFeatureValue(value: unknown, meta?: FeatureMeta): string {
  const numberValue = normalizeNumber(value);

  if (numberValue === null) {
    return "-";
  }

  if (meta?.format === "money") {
    return new Intl.NumberFormat("ru-RU", {
      maximumFractionDigits: 2,
    }).format(numberValue);
  }

  if (meta?.format === "percent") {
    return `${(numberValue * 100).toFixed(2)}%`;
  }

  return new Intl.NumberFormat("ru-RU", {
    maximumFractionDigits: 2,
  }).format(numberValue);
}

function getRiskInterpretation(key: string, value: unknown): string {
  const numberValue = normalizeNumber(value);

  if (numberValue === null) {
    return "Нет данных для интерпретации";
  }

  if (key === "debt_ratio") {
    if (numberValue >= 0.7) return "Высокая долговая нагрузка";
    if (numberValue >= 0.4) return "Повышенная долговая нагрузка";
    if (numberValue >= 0.2) return "Умеренная долговая нагрузка";
    return "Низкая долговая нагрузка";
  }

  if (key === "overdue_days_90") {
    if (numberValue > 0) return "Есть длительная просрочка";
    return "Длительная просрочка отсутствует";
  }

  if (key === "overdue_days_30") {
    if (numberValue >= 30) return "Значительная краткосрочная просрочка";
    if (numberValue > 0) return "Есть краткосрочная просрочка";
    return "Просрочка отсутствует";
  }

  if (key === "disputes_count") {
    if (numberValue >= 5) return "Много спорных ситуаций";
    if (numberValue > 0) return "Есть спорные ситуации";
    return "Спорные ситуации отсутствуют";
  }

  if (key === "transactions_count") {
    if (numberValue < 50) return "Низкая транзакционная активность";
    if (numberValue < 150) return "Умеренная транзакционная активность";
    return "Нормальная транзакционная активность";
  }

  if (key === "employees_count") {
    if (numberValue < 20) return "Малая организация";
    if (numberValue < 100) return "Средняя организация";
    return "Крупная организация";
  }

  return "Используется при расчёте риск-оценки";
}

export function RiskUsedFeatures({ features }: Props) {
  const entries = Object.entries(features).filter(
    ([, value]) => value !== null && value !== undefined
  );

  if (entries.length === 0) {
    return <p>Использованные признаки отсутствуют.</p>;
  }

  return (
    <div className="risk-used-features">
      {entries.map(([key, value]) => {
        const meta = featureMeta[key];

        return (
          <div className="risk-used-feature-card" key={key}>
            <div className="risk-used-feature-header">
              <div>
                <span>{meta?.label ?? key}</span>
                <strong>{formatFeatureValue(value, meta)}</strong>
              </div>

              {meta?.unit && <em>{meta.unit}</em>}
            </div>

            <p>{meta?.description ?? "Признак, использованный ML-моделью"}</p>

            <div className="risk-used-feature-interpretation">
              {getRiskInterpretation(key, value)}
            </div>
          </div>
        );
      })}
    </div>
  );
}