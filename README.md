# GPU Credit Scoring - Projet Eranova

## Description
Système d'aide à la décision pour l'évaluation du risque de crédit des petits commerçants sans historique bancaire formel. Développé dans le cadre du GPU Challenge 2026.

## Architecture

```
Eranova/
├── app/                    # Application Streamlit
│   ├── app.py             # Point d'entrée principal
│   ├── config.py          # Configuration
│   ├── database.py        # Gestion des données
│   ├── style.css          # Styles personnalisés
│   ├── components/        # Composants UI réutilisables
│   └── pages/             # Pages de l'application
├── src/                   # Code source backend
│   ├── generate_synthetic_data.py
│   ├── feature_engineering.py
│   ├── model_loader.py
│   ├── prediction_service.py
│   ├── explain.py
│   ├── scoring.py
│   └── rules_engine.py
├── data/                  # Données synthétiques
├── model/                 # Artefacts du modèle
├── rules/                 # Règles métier
├── explanations/          # Templates d'explications
├── notebooks/             # Notebooks d'expérimentation
├── benchmarks/            # Résultats benchmarks
├── tests/                 # Tests unitaires
├── docs/                  # Documentation
└── presentation/          # Matériel démo jury
```

## Installation

```bash
pip install -r requirements.txt
```

## Génération des données

```bash
python -m src.generate_synthetic_data
```

Génère :
- `data/merchants.csv` - 700K commerçants
- `data/transactions.csv` - Transactions sur 6-12 mois
- `data/labels.csv` - Labels de remboursement simulés
- `data/features.csv` - Features engineering
- `data/test_profiles.csv` - 3 profils de démonstration

## Entraînement du modèle

Voir `notebooks/03_training_cpu_gpu.ipynb` pour l'entraînement GPU complet sur Kaggle/Colab.

Le modèle entraîné est exporté dans `model/xgboost_model.json`.

## Lancement de l'application

```bash
streamlit run app/app.py
```

L'application sera accessible sur `http://localhost:8501`.

## Pages de l'application

1. **Tableau de bord** - Vue d'ensemble, distributions, métriques
2. **Profil commerçant** - Détail d'un commerçant, activité, indicateurs
3. **Évaluation crédit** - Score, risque, recommandation, explications
4. **Explications SHAP** - Facteurs d'influence avec graphiques
5. **Revue humaine** - Interface de décision pour l'agent
6. **Benchmark GPU** - Comparaison CPU/GPU, preuves d'accélération

## Fonctionnalités clés

- **Score 0-100** : Probabilité de remboursement × 100
- **Niveaux de risque** : Très élevé → Très faible (5 niveaux)
- **Confiance** : Faible / Moyenne / Élevée
- **Recommandations** : Montant, durée, type de produit
- **SHAP** : Top 10 facteurs positifs/négatifs
- **Règles métier** : 8 règles (primo, historique court, données incomplètes, etc.)
- **Revue humaine** : Obligatoire selon règles, traçabilité

## Profils de démonstration

| ID | Profil | Résultat attendu |
|---|---|---|
| MCH-DEMO-01 | Activité régulière | Score favorable, recommandation prudente |
| MCH-DEMO-02 | CA élevé, marge faible | Score réduit, montant limité, explications dépenses |
| MCH-DEMO-03 | Données insuffisantes | Confiance faible, revue humaine obligatoire |

## Benchmark GPU

| Métrique | CPU | GPU | Speedup |
|---|---|---|---|
| Entraînement | 89.3s | 12.5s | **7.1x** |
| Prédiction (100K) | 180ms | 45ms | **4x** |
| AUC | 0.8698 | 0.8721 | - |

## Déploiement

### Local
```bash
streamlit run app/app.py
```

### Streamlit Cloud
1. Pousser sur GitHub
2. Connecter sur share.streamlit.io
3. Configurer `app/app.py` comme point d'entrée

## Limites déclarées

- Données synthétiques uniquement
- Labels simulés
- Pas de validation sur données réelles
- Score ≠ garantie de remboursement
- Validation humaine obligatoire
- Accès GPU gratuit non garanti

## Auteurs

Équipe GPU Challenge 2026 - Eranova