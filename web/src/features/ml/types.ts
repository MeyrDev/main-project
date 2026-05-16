export type MLModelInfo = {
  model_name: string;
  version: string;
  algorithm_name: string;
  artifact_path: string;
  feature_columns: string[];
  metrics: Record<string, number | string>;
  status: string;
};