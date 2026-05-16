import type { MLModelInfo } from "./types";

type Props = {
  model: MLModelInfo;
};

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
        <strong>{model.status}</strong>
      </div>

      <div className="ml-info-card wide">
        <span>Artifact</span>
        <strong>{model.artifact_path}</strong>
      </div>
    </div>
  );
}