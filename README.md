# GPU Credit Scoring - Alternative Credit Scoring

## Description

Solution d'aide à la décision pour les institutions de microfinance (IMF) souhaitant évaluer le risque de crédit de petits commerçants sans historique bancaire formel.

Le système exploite un dataset existant de 700 000 lignes (42 colonnes), entraîne un modèle XGBoost sur GPU (Kaggle Tesla T4), et expose une API FastAPI consommée par un frontend React.

## Architecture

```
Dataset (Google Drive, 700K lignes)
       ↓ gdown
Kaggle Notebook (GPU T4)
  - Nettoyage + encodage one-hot
  - Normalisation (log1p montants, clip ratios)
  - XGBoost CPU vs GPU
  - SHAP TreeExplainer
       ↓ export
xgboost_model.json + feature_order.json + model_metadata.json + feature_schema.json
       ↓
Backend FastAPI (Render)
  - Normalisation identique au training
  - Scoring + itération montant (seuil 70, max 300K FCFA)
  - SHAP explanations
  - 8 règles métier
  - SQLite pour décisions
       ↓ API REST
Frontend React (Vercel)
  - Tableau de bord
  - Liste commerçants
  - Profil commerçant
  - Évaluation crédit
  - Évaluation manuelle (35 champs)
  - Règles métier
  - Benchmark GPU
  - Revue humaine
```

## Stack technique

| Couche | Technologie | Rôle |
|--------|------------|------|
| Frontend | React 18 + TypeScript | Interface agent de crédit |
| Build | Vite 5 | Dev et compilation |
| Design | Tailwind CSS 3 | Styling utilitaire |
| Graphiques | Recharts 2 | SHAP bar charts |
| Routing | React Router 6 | Navigation SPA |
| Backend | FastAPI + Pydantic v2 | API REST |
| Validation | Pydantic v2 | Contrats entrée/sortie |
| ML | XGBoost 3.4.1 | Modèle de scoring |
| Explicabilité | SHAP 0.54 | TreeExplainer |
| Données | Pandas 3 + NumPy 2 | Manipulation CSV |
| Entraînement | Kaggle GPU T4 | XGBoost `device='cuda'` |
| Base locale | SQLite | Décisions humaines |
| Déploiement frontend | Vercel | CDN global |
| Déploiement backend | Render | Uvicorn + Docker |
| Versionnement | Git + GitHub | Code source |

## Structure

```
gpu-credit-scoring/
├── frontend/              # React + TypeScript + Vite + Tailwind
│   ├── src/
│   │   ├── api/           # Client axios, endpoints
│   │   ├── components/    # ScoreCard, RiskBadge, ShapBarChart, etc.
│   │   ├── pages/         # Dashboard, Merchants, Assessment, Custom, Rules, Benchmark
│   │   ├── types/         # TypeScript interfaces
│   │   └── styles/        # globals.css (Tailwind)
│   ├── vercel.json        # SPA routing rewrite
│   └── package.json
├── backend/               # FastAPI
│   ├── app/
│   │   ├── main.py        # Point d'entrée, CORS, routers
│   │   ├── config.py      # Settings (pydantic-settings)
│   │   ├── models.py      # Pydantic schemas
│   │   ├── routers/       # health, merchants, assessments, benchmarks, rules
│   │   ├── services/      # model, scoring, shap, rules, decision
│   │   └── schemas.py     # Enums (RiskLevel, Confidence, etc.)
│   ├── model/             # xgboost_model.json, feature_order.json, etc.
│   ├── rules/             # business_rules.json (8 règles)
│   ├── data/              # demo_profiles.csv (3 profils réels)
│   ├── requirements.txt
│   └── Dockerfile
├── kaggle/                # training-credit-scoring-gpu.ipynb
├── artifacts/             # benchmark_cpu_gpu.csv, summary.json
├── docs/                  # architecture, data_dictionary, api_contract, etc.
└── presentation/          # demo_script, gpu_explanation, jury_questions
```

## Fonctionnalités

- **Score 0-100** : probabilité de remboursement × 100
- **Niveaux de risque** : VERY_HIGH → VERY_LOW (5 niveaux)
- **Confiance** : LOW / MEDIUM / HIGH
- **Montant max** : 300 000 FCFA (plafond dur)
- **Itération montant** : si score < 70, réduit par paliers de 10K
- **SHAP** : top 10 facteurs positifs/négatifs
- **8 règles métier** : primo, historique court, données incomplètes, etc.
- **Évaluation manuelle** : 35 champs modifiables
- **Revue humaine** : validation agent
- **Benchmark GPU** : comparaison CPU/GPU

## Profils de démonstration

| ID | Profil | Caractéristiques |
|----|--------|-----------------|
| MCH-DEMO-01 | Bon candidat | Revenu 160K, ancienneté 42 mois, rembourse |
| MCH-DEMO-02 | Risque élevé | Revenu 225K, ancienneté 3 mois, défaut |
| MCH-DEMO-03 | Données insuffisantes | Première fois, ancienneté 5 mois, défaut |

## Démarrage local

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Swagger: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Interface: http://localhost:5173

## Déploiement

### Backend (Render)
- Root Directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
- Root Directory: `frontend`
- Build: `npm run build`
- Output: `dist`
- Env: `VITE_API_URL=https://era-nova-gpu-challenge.onrender.com`

## Entraînement Kaggle

1. New Notebook → GPU T4 x2
2. Import `kaggle/training-credit-scoring-gpu.ipynb`
3. Run All (gdown télécharge le dataset, entraîne, exporte)
4. Télécharger les 4 fichiers → remplacer dans `backend/model/`

## Limites

- Données synthétiques uniquement
- Score ≠ garantie de remboursement
- Validation humaine obligatoire
- GPU Kaggle selon quotas disponibles