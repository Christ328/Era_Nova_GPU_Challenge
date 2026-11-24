# Kaggle - Entraînement GPU

## Dataset

- Fichier: `dataset_scoring_benin_700k.csv`
- Source: Google Drive du projet
- Taille: ~219.5 MB
- Import dans Kaggle comme dataset privé

## Notebook

`training-credit-scoring-gpu.ipynb`

### Étapes

1. Charger le dataset Kaggle
2. Inspecter les colonnes et types
3. Vérifier les valeurs manquantes
4. Nettoyer les données
5. Identifier la variable cible
6. Séparer features et label
7. Séparer train/test
8. Entraîner XGBoost CPU
9. Entraîner XGBoost GPU (`tree_method='hist', device='cuda'`)
10. Comparer temps et métriques
11. Calculer SHAP (TreeExplainer)
12. Construire le score 0-100
13. Tester les règles métier
14. Exporter le modèle et métadonnées

## Export

- `xgboost_model.json` → `backend/model/`
- `model_metadata.json` → `backend/model/`
- `feature_schema.json` → `backend/model/`
- `feature_order.json` → `backend/model/`
- `benchmark_cpu_gpu.csv` → `artifacts/`