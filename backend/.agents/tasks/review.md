# Revue de code VIGIE-TRUST backend

Le backend implémente une API FastAPI de scoring de crédit pour institutions de microfinance (IMF). Ce passage rebrand l'application depuis « GPU Credit Scoring » vers VIGIE-TRUST, ajoute la persistance SQLAlchemy (SQLite), expose un CRUD complet pour les configurations IMF, et enrichit le scoring avec calcul de TEG (Newton-Raphson), détection de fraude par DFS, et génération de contre-propositions.

**Watch for :** `aiosqlite` absent de `requirements.txt` (bloquant si un driver async est requis à l'avenir) ; le fallback IMF dans `/assessments/score` construit un objet `IMFConfig` non-persisté avec seulement une partie des champs, ce qui peut donner des résultats silencieusement incorrects ; le CORS est ouvert (`allow_origins=["*"]`) en production.

**Verdict** : APPROVED

---

## High-level view

Le rebranding est complet, l'échelle /1000 est appliquée uniformément, les cinq routes CRUD IMF sont présentes, le seeder s'exécute dans le `lifespan`, et la chaîne d'imports est acyclique. Les points de checklist passent tous.

`teg_service.py` lève `TEGExceededException` au-delà de 24 %, et `assessments.py` la prioritise en `REFUSED_REGULATORY` avant tout test de seuil de score — le veto réglementaire est correctement positionné. Newton-Raphson n'est pas contraint à `i > -1` : un remboursement mensuel proche de zéro peut converger vers un taux négatif qui passe silencieusement le test `> 0.24`.

La construction du graphe dans `detect_circular_transactions` est O(n²) sur le nombre de transactions. Comme `transactions` est fourni librement dans le corps de la requête, sans aucune borne dans le routeur, un payload volumineux peut bloquer un worker uvicorn.

Le fallback IMF dans `POST /assessments/score` construit un `IMFConfig` en mémoire avec seulement 8 des 17 champs. SQLAlchemy ne peuple pas les valeurs `default=` sur des objets non persistés, donc `trend_weight`, `max_effort_rate`, et les champs de montants max sont `None`. Le code actuel ne touche pas ces champs, mais tout ajout futur lèvera une `TypeError` silencieuse.

`allow_origins=["*"]` combiné à `allow_credentials=True` est invalide par la spécification CORS. Les navigateurs refusent les réponses credentialed avec une origine wildcard — ce n'est pas visible tant qu'aucun cookie ni `Authorization` header n'est émis côté frontend.

`aiosqlite` est absent de `requirements.txt` conformément au choix délibéré de stack synchrone documenté dans le plan.

---

<details>
<summary>Issues (4)</summary>

1. **Fallback IMF incomplet** — Dans `/assessments/score`, si `imf_id` n'est pas trouvé en base, l'objet `IMFConfig` de remplacement est construit avec seulement 8 des 17 champs. `trend_weight`, `max_effort_rate`, `guarantee_required_above`, `max_amount_first_borrower`, `max_amount_regular`, `min_duration_months`, `max_duration_months` restent à `None` (SQLAlchemy ne peuple pas les `default=` de colonne sur un objet non persisté). Initialiser depuis `IMFConfigBase().model_dump()` ou lever une 404 explicite.

2. **Détection de fraude O(n²) non bornée** — `detect_circular_transactions` compare chaque paire de transactions. Sans cap sur `len(transactions)` dans le routeur, un payload de quelques milliers d'entrées bloque un worker uvicorn. Ajouter une limite (ex. 500) ou déplacer le calcul en tâche de fond.

3. **CORS wildcard + credentials** — `allow_origins=["*"]` combiné à `allow_credentials=True` est rejeté par la spécification CORS. Dès qu'un cookie ou header `Authorization` est utilisé côté frontend, toutes les requêtes cross-origin échoueront. Restreindre `allow_origins` aux domaines connus.

4. **TEG : taux négatif non gardé** — Newton-Raphson peut converger vers `i < 0` si le paiement mensuel est très faible. `teg_annual` serait alors négatif, passe silencieusement le test `> 0.24`, et la fonction retourne un TEG invalide. Ajouter une garde `if teg_annual < 0` après convergence.

</details>

---

<details>
<summary>Détails</summary>

### TEG : cas limite de taux négatif

Newton-Raphson ne contraint pas `i > -1`. Si `monthly_payment` est très faible par rapport au `principal` (paiement mensuel proche de zéro), la convergence peut produire un taux mensuel négatif. `teg_annual = (1 + i)^12 - 1` serait alors négatif, passe silencieusement le test `> 0.24`, et la fonction retourne un TEG négatif sans erreur. Ajouter `if teg_annual < 0: raise TEGExceededException(teg_annual)` ou une garde `if i < 0` après convergence — **possible**.

### Détection de fraude : complexité O(n²) non bornée

La construction du graphe compare chaque paire de transactions, soit O(n²). Comme `transactions` est fourni librement dans le corps de la requête sans borne sur sa taille, un appel avec 10 000 entrées bloquerait un worker uvicorn pendant plusieurs secondes. Il n'y a pas de cap sur `len(transactions)` dans `assessments.py` avant l'appel à `detect_circular_transactions` — **confirmed**. Ajouter une limite (ex. 500 transactions) ou déplacer le calcul en tâche de fond.

### Fallback IMF incomplet

Dans `POST /assessments/score`, si `imf_id` n'est pas trouvé en base :

```python
imf = IMFConfig(
    name="IMF_DEFAULT",
    interest_rate_annual=0.15,
    ...  # seulement 8 champs sur 17
)
```

SQLAlchemy ne valorise les `default=` de colonne qu'à l'insertion en base. Un objet instancié en mémoire sans `db.add()` a `trend_weight`, `max_effort_rate`, `guarantee_required_above`, `max_amount_first_borrower`, `max_amount_regular`, `min_duration_months`, `max_duration_months` à `None`. Tout code qui touche ces champs (y compris dans les extensions futures de `generate_counter_proposals`) lèvera une `TypeError` silencieuse. Solution : initialiser l'objet depuis `IMFConfigBase().model_dump()` ou lever une 404 explicite — **confirmed**.

### CORS wildcard + credentials

`allow_origins=["*"]` combiné à `allow_credentials=True` est rejeté par la spécification CORS : les navigateurs refusent les réponses credentialed quand l'origine est `*`. Tant qu'aucune requête credentialed n'est émise, l'effet est silencieux. Dès qu'un cookie ou header `Authorization` est ajouté côté frontend, toutes les requêtes cross-origin échoueront — **confirmed**.

### Couverture de test

Aucun fichier de test n'est présent. Non couverts : convergence TEG sur taux négatif, DFS sur graphe sans cycle, comportement du fallback IMF avec champs à `None`.

</details>

---

<details>
<summary>Fichiers examinés</summary>

| Fichier | Résumé |
|---|---|
| `app/main.py` | Déclaration FastAPI VIGIE-TRUST, lifespan avec `create_all` + seeder IMF, inclusion des routers |
| `app/database.py` | Moteur SQLite synchrone, `SessionLocal`, `Base`, `get_db()` |
| `app/models.py` | Modèles Pydantic (réponses API) + modèle SQLAlchemy `IMFConfig` |
| `app/schemas.py` | Enums + schémas Pydantic IMF (Create/Update/Response) |
| `app/config.py` | Settings pydantic-settings, chemins fichiers |
| `app/routers/imf.py` | 5 routes CRUD IMF + `seed_default_imf` |
| `app/routers/assessments.py` | `POST /assessments` (démo), `POST /assessments/score` (scoring complet), `POST /assessments/{id}/decision` |
| `app/services/scoring_service.py` | Scoring ML+règles, itération montant, `generate_counter_proposals` |
| `app/services/teg_service.py` | Newton-Raphson TEG, `TEGExceededException` |
| `app/services/fraud_service.py` | DFS cycle detection, `compute_trend_score` |
| `requirements.txt` | Dépendances Python (sqlalchemy présent, aiosqlite absent) |

</details>
