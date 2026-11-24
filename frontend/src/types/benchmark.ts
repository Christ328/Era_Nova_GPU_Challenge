export interface Benchmark {
  dataset_size: number
  n_features: number
  cpu_time: number
  gpu_time: number
  speedup: number
  cpu_auc: number
  gpu_auc: number
  gpu_type: string
  xgboost_version: string
}