type Props = {
  actions: string[];
};

export function RiskRecommendations({ actions }: Props) {
  if (actions.length === 0) {
    return <p>Рекомендации отсутствуют.</p>;
  }

  return (
    <ul className="risk-recommendations">
      {actions.map((action) => (
        <li key={action}>{action}</li>
      ))}
    </ul>
  );
}