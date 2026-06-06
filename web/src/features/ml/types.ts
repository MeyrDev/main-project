export type MLModelInfo = {
  model_name: string;
  version: string;
  algorithm_name: string;
  artifact_path: string;
  feature_columns: string[];
  metrics: Record<string, number | string>;
  status: string;
};

export type ConfusionMatrix = {
  labels: number[];
  matrix: number[][];
};

export type MLTrainingReport = {
  trained: boolean;
  project_name?: string | null;
  model_version?: string | null;
  algorithm?: string | null;
  trained_at?: string | null;
  train_dataset_path?: string | null;
  validation_dataset_path?: string | null;
  train_rows?: number | null;
  validation_rows?: number | null;
  feature_columns: string[];
  target_column?: string | null;
  train_target_distribution: Record<string, number | string>;
  validation_target_distribution: Record<string, number | string>;
  metrics: Record<string, number | string>;
  confusion_matrix?: ConfusionMatrix | number[][] | null;
  artifact_path?: string | null;
  notes?: string | null;
  artifact_exists: boolean;
  artifact_size_bytes?: number | null;
  artifact_modified_at?: string | null;
  message?: string | null;
};

export type MLValidationEvaluation = {
  evaluated: boolean;
  evaluated_at: string;
  validation_dataset_path: string;
  validation_rows: number;
  feature_columns: string[];
  target_column: string;
  metrics: Record<string, number>;
  confusion_matrix: ConfusionMatrix;
  artifact_path: string;
  artifact_exists: boolean;
  artifact_size_bytes?: number | null;
  artifact_modified_at?: string | null;
  evaluation_path: string;
  notes: string;
};
