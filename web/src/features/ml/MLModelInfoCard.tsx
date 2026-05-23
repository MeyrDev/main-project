import type { MLModelInfo } from "./types";

type Props = {
  model: MLModelInfo;
};

const statusMap: Record<string, string> = {
  "training": "Обучение",
  "ready": "Готова",
  "failed": "Ошибка",
}

export function MLModelInfoCard({ model }: Props) {
  return (
    <div className="ml-info-grid">
      <div className="ml-info-card">
        <span>Название модели</span>
        <strong>{model.model_name}</strong>
      </div>

      <div className="ml-info-card">
        <span>Версия</span>
        <strong>{model.version}</strong>
      </div>

      <div className="ml-info-card">
        <span>Алгоритм</span>
        <strong>{model.algorithm_name}</strong>
      </div>

      <div className="ml-info-card">
        <span>Статус</span>
        <strong>{statusMap[model.status] ||  model.status}</strong>
      </div>

      <div className="ml-info-card wide">
        <span>Artifact</span>
        <strong>{model.artifact_path}</strong>
      </div>
    </div>
  );
}