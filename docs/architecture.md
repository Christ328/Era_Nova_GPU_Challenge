# Architecture

## Vue d'ensemble

```
Google Drive (dataset)
       ↓
Kaggle (GPU training + SHAP)
       ↓
Modèle exporté (xgboost_model.json)
       ↓
Backend FastAPI (scoring + règles + SHAP)
       ↓
Frontend React (interface agent)
       ↓
Décision humaine IMF
```

## Backend

- FastAPI avec 4 routers: health, merchants, assessments, benchmarks
- Services: model_service, scoring_service, shap_service, rules_service, decision_service
- Stockage décisions: SQLite
- Documentation: Swagger /docs

## Frontend

- React + TypeScript + Vite
- Tailwind CSS pour le design
- Recharts pour les graphiques SHAP
- React Router pour la navigation
- 6 pages: Dashboard, Merchants, Merchant, Assessment, Review, Benchmark