# Contrat API

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### GET /health
Status du serveur et du modèle.

### GET /merchants
Liste paginée des commerçants.
- Query: `page` (int), `page_size` (int), `search` (string)

### GET /merchants/{merchant_id}
Détail d'un commerçant.

### POST /assessments
Crée une évaluation.
- Query: `merchant_id` (string)
- Retourne: AssessmentResponse

### POST /assessments/{assessment_id}/decision
Enregistre une décision humaine.
- Body: DecisionRequest

### GET /benchmarks
Résultats benchmark CPU/GPU.

## Schémas

Voir `backend/app/models.py` pour les définitions Pydantic complètes.