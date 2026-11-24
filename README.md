# GPU Credit Scoring - Alternative Credit Scoring

## Description

Solution d'aide à la décision pour les institutions de microfinance (IMF) souhaitant évaluer le risque de crédit de petits commerçants sans historique bancaire formel.

Le système exploite un dataset existant de 700 000 lignes, entraîne un modèle XGBoost sur GPU (Kaggle), et expose une API FastAPI consommée par un frontend React.

## Architecture

```
Dataset (Google Drive) → Kaggle (GPU Training) → Modèle exporté
                                                    ↓
Frontend React (Vercel) ← API FastAPI (Render) ← Modèle + Règles + SHAP
```

## Stack

| Couche | Technologie |
|--------|------------|
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Graphiques | Recharts |
| Backend | FastAPI + Pydantic |
| ML | XGBoost + SHAP |
| Entraînement | Kaggle GPU (Tesla T4) |
| Base locale | SQLite |
| Déploiement | Vercel (frontend) + Render (backend) |

## Structure

```
gpu-credit-scoring/
├── frontend/          # React + TypeScript + Vite
├── backend/           # FastAPI
├── kaggle/            # Notebook d'entraînement GPU
├── artifacts/         # Benchmarks CPU/GPU
├── docs/              # Documentation
└── presentation/      # Matériel démo jury
```

## Démarrage rapide

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

### Frontend (Vercel)
1. Importer le repo GitHub sur vercel.com
2. Root directory: `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Variable d'environnement: `VITE_API_URL=https://votre-backend.render.com`

### Backend (Render)
1. Créer un Web Service sur render.com
2. Root directory: `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Profils de démonstration

| ID | Profil | Résultat attendu |
|----|--------|-----------------|
| MCH-DEMO-01 | Activité régulière | Score favorable |
| MCH-DEMO-02 | CA élevé, marge faible | Score réduit, montant limité |
| MCH-DEMO-03 | Données insuffisantes | Confiance faible, revue humaine |

## Limites

- Données synthétiques uniquement
- Score ≠ garantie de remboursement
- Validation humaine obligatoire
- GPU Kaggle selon quotas disponibles