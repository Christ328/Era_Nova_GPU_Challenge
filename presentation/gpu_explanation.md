# Explication GPU

## Pourquoi GPU?

- XGBoost `tree_method='hist'` + `device='cuda'`
- Entraînement sur 700K lignes
- Speedup mesuré: **7.1x** (89.3s → 12.5s)

## Preuve

- Benchmark CPU vs GPU dans `artifacts/benchmark_cpu_gpu.csv`
- Métriques AUC comparables (0.8698 vs 0.8721)
- GPU: NVIDIA Tesla T4 (Kaggle)

## En production

- L'API FastAPI fait des prédictions CPU (une requête à la fois)
- Le GPU sert à l'entraînement et aux lots
- Le modèle exporté est chargé au démarrage de l'API