# Credit Scoring Bug Investigation Report

## Summary

The score=0/VERY_HIGH result for every manual assessment is caused by **one primary bug** (a probability inversion error) compounded by two secondary normalization bugs. Together they make every good borrower appear maximally risky.

---

## Bug 1 — CRITICAL: Probability is not inverted (the root cause of score=0)

**File:** `backend/app/services/scoring_service.py`, line ~44  
**Code:**
```python
proba = model_service.predict(features)
score = int(round(proba * 100))
```

**What `model_service.predict` returns:**  
`model_service.predict` calls `self._model.predict_proba(X)[0, 1]`, which returns class 1's probability. The model's target column is `defaut_paiement` (from `model_metadata.json` and `feature_schema.json`), where **class 1 = payment default = bad borrower**.

So `predict_proba(X)[0, 1]` = **P(the borrower will default)**.

**The scale is inverted:**

| Borrower quality | P(default) | Current score | RISK label assigned | Correct score | Correct RISK label |
|---|---|---|---|---|---|
| Excellent | 0.03 | 3 | VERY_HIGH ❌ | 97 | VERY_LOW ✓ |
| Good | 0.10 | 10 | VERY_HIGH ❌ | 90 | VERY_LOW ✓ |
| Risky | 0.80 | 80 | VERY_LOW ❌ | 20 | HIGH ✓ |

The `RISK_LEVELS` table in `scoring_service.py` treats score 0–29 as VERY_HIGH and 75–100 as VERY_LOW — meaning high score = good creditworthiness. But `proba * 100` makes high score = high default risk. **The score must be `(1 - proba) * 100`.**

**Cascade into `_iterate_amount`:**  
When `initial_score` is ~3–10 (a good borrower with low default probability), `_iterate_amount` triggers because `score < SCORE_THRESHOLD (70)`. It loops from 200,000 down to 50,000 in 10,000-FCFA steps, re-running the model each time. Because the model always returns low P(default) ≈ 0.05 for a good borrower regardless of amount, every loop iteration produces score ~5, which never reaches 70. The loop exhausts and returns `(50000, 0, True)`. The `iterated=True` flag appends the alert:

> "Montant adapté à 50,000 FCFA pour atteindre le score seuil de 70"

This exactly matches what the user observed.

**Fix:**
```python
# In scoring_service.py, line ~44
proba = model_service.predict(features)
score = int(round((1 - proba) * 100))   # <-- invert: proba is P(default)
```

Same fix needed inside `_iterate_amount` (lines ~90–102 in `scoring_service.py`):
```python
proba = model_service.predict(test_features)
score = int(round((1 - proba) * 100))   # same inversion
```

---

## Bug 2 — Incorrect normalization of `score_aptitude_entrepreneuriale` and `locus_controle_interne`

**File:** `backend/app/services/model_service.py`, `_normalize()` method  
**Code:**
```python
ratio_cols = ["tendance_solde_3m", "regularite_depots_ecart_type",
              "part_transferts_marchands", "stabilite_lieu_vie",
              "regularite_cotisations_tontine", "score_aptitude_entrepreneuriale",
              "score_integrite", "locus_controle_interne", "garantie"]
for col in ratio_cols:
    if col in X.columns:
        X[col] = X[col].clip(0, 1)
```

**Problem:**  
- `score_aptitude_entrepreneuriale` is on a **0–100 scale** (the user entered 65; the UI label is "Aptitude entrepreneuriale" and the default is 65). Clipping to [0, 1] turns 65 → **1.0**.  
- `locus_controle_interne` is on a **0–10 scale** (the user entered 6). Clipping to [0, 1] turns 6 → **1.0**.

Both features are listed in `feature_schema.json` under `ratio_cols`, but their actual value ranges are not 0–1. The model was presumably trained on the same normalization pipeline — meaning the model *was* trained expecting these already in 0–1 range. The mismatch is therefore between the **UI input scale** and the **model's training scale**, not between the normalization code and the model.

**Two possible fixes (choose the one matching training data):**

Option A — The model was trained with raw values (0–100, 0–10): remove those two from `ratio_cols`.  
Option B — The model was trained with pre-normalized values (0–1): add UI-side scale conversion before submitting:
  - `score_aptitude_entrepreneuriale`: divide by 100 before sending (65 → 0.65)
  - `locus_controle_interne`: divide by 10 before sending (6 → 0.6)

The safest approach is **Option B** (normalize in the frontend or at the API boundary), since `feature_schema.json` deliberately lists these as ratio columns, suggesting training data was also normalized.

---

## Bug 3 — SHAP explanations computed on unnormalized features

**File:** `backend/app/services/shap_service.py`, `_compute_shap()` method  
**Code:**
```python
X = pd.DataFrame([features])
for col in feature_order:
    if col not in X.columns:
        X[col] = 0
X = X[feature_order].fillna(0)

# _normalize() is NEVER called here
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)
```

**Problem:**  
`model_service.predict()` calls `_normalize(X)` before prediction, but `shap_service._compute_shap()` does not. This means SHAP values are computed on raw features (e.g., `revenu_mensuel_declare=150000`) while the model's internal decision boundaries were learned on log-transformed features (e.g., `log1p(150000) ≈ 11.92`). The SHAP values are therefore **computed on out-of-distribution inputs** relative to what the model's tree splits expect.

This explains why the SHAP chart shows `revenu_mensuel_declare=150000` as a large *negative* contributor: the raw value 150,000 is far outside the model's training distribution for that feature (which was `log1p`-transformed to ~12). The tree sees this as an anomalous reading.

**Fix:**
```python
# In shap_service.py, _compute_shap(), after building X and before TreeExplainer
from app.services.model_service import model_service as _ms
X = _ms._normalize(X)   # normalize before SHAP, same as predict()
```

---

## Bug 4 — `business_rules.json` uses different field names than the actual features dict

**File:** `backend/rules/business_rules.json` vs `backend/app/services/rules_service.py`

The file `business_rules.json` (loaded by `rules_service.py`) uses field names like `is_first_time_borrower`, `activity_age_months`, `data_completeness`, `expense_documentation_ratio`, `has_inconsistencies`, `regularity_score`, `margin_ratio`, `monthly_income_mean` — **none of which exist** in the features dict produced by the frontend or CSV profiles.

The actual feature dict uses: `premiere_fois`, `anciennete_activite_mois`, `depenses_mensuelles`, `revenu_mensuel_declare`, etc.

The `_check_condition` method in `rules_service.py` uses `eval()`:
```python
local_vars = {**features, "score": score, "confidence": confidence}
return bool(eval(condition, {"__builtins__": {}}, local_vars))
```

When a referenced variable (e.g., `is_first_time_borrower`) is not in `local_vars`, the `eval` raises a `NameError` which is caught and returns `False`. So all business rules silently fail — they never fire. The `RulesService._default_rules()` method (which uses the correct field names) is never reached because the JSON file exists and loads successfully.

**Impact:** No business rules trigger. The `adjustments` dict always has defaults (`amount_multiplier=1.0`, `require_human_review=False`). This is a correctness bug but does not directly cause score=0 — it means rules that should constrain amounts never apply.

**Fix:** Update `business_rules.json` to use the actual feature names:

| JSON (wrong) | Actual feature name |
|---|---|
| `is_first_time_borrower` | `premiere_fois` |
| `activity_age_months` | `anciennete_activite_mois` |
| `data_completeness` | *(no equivalent; remove or compute it)* |
| `expense_documentation_ratio` | *(no equivalent; remove)* |
| `has_inconsistencies` | *(no equivalent; remove)* |
| `regularity_score` | `regularite_depots_ecart_type` |
| `margin_ratio` | *(no equivalent)* |
| `monthly_income_mean` | `revenu_mensuel_declare` |

---

## Full Data Flow Trace

```
Frontend (CustomScorePage.tsx)
  |
  | POST /api/v1/assessments/score
  | Body: { age: 35, anciennete_activite_mois: 24, revenu_mensuel_declare: 150000,
  |         ..., score_aptitude_entrepreneuriale: 65, locus_controle_interne: 6, ... }
  v
Backend router (assessments.py:score_custom)
  |
  | features dict passed directly to scoring_service.score(features)
  v
scoring_service.score()
  |
  | -> model_service.predict(features)
  |      -> X = pd.DataFrame([features])
  |      -> missing feature_order columns filled with 0
  |         (genre_Homme, niveau_education_*, departement_*, secteur_activite_* all = 0)
  |      -> _normalize(X):
  |           log1p(revenu_mensuel_declare=150000) = 11.92
  |           log1p(montant_demande=200000)        = 12.21
  |           score_aptitude_entrepreneuriale=65   -> clip(0,1) = 1.0  [BUG 2]
  |           locus_controle_interne=6             -> clip(0,1) = 1.0  [BUG 2]
  |      -> predict_proba(X)[0,1] = P(default) ≈ 0.05  (good borrower)
  |      -> returns 0.05
  |
  | proba = 0.05
  | score = int(round(0.05 * 100)) = 5          [BUG 1: should be (1-0.05)*100 = 95]
  |
  | _apply_score_caps: ratio = 200000/150000 = 1.33, no cap applied
  |
  | _iterate_amount(features, score=5, requested=200000):
  |   score(5) < SCORE_THRESHOLD(70) -> loop starts
  |   tries 200000, 190000, ..., 50000 — model always returns P(default)≈0.05 -> score≈5
  |   never reaches 70 -> returns (50000, 0, True)
  |
  | score = 0, alert "Montant adapté à 50,000 FCFA" added
  |
  | risk_level = VERY_HIGH  (score 0 is in [0, 29] range)
  |
  | shap_service.explain(features) [BUG 3: no normalization]
  |   X built from raw features (revenu=150000, not 11.92)
  |   SHAP trees see out-of-distribution values
  |   revenu_mensuel_declare gets large negative SHAP value (looks like bad signal)
  |
  | returns { score: 0, risk_level: VERY_HIGH, ... }
  v
Frontend displays: Score 0/100, VERY_HIGH, "Montant adapté à 50,000 FCFA"
```

---

## Findings Summary Table

| # | Bug | File | Severity | Effect |
|---|---|---|---|---|
| 1 | `proba * 100` instead of `(1 - proba) * 100` | `scoring_service.py` lines 44, 97 | **CRITICAL** | Inverts all scores; good borrowers always get ~0, bad borrowers get ~100 |
| 2 | `score_aptitude_entrepreneuriale` and `locus_controle_interne` clipped to [0,1] | `model_service.py` `_normalize()` | HIGH | Features sent to model at wrong scale; distorts prediction |
| 3 | SHAP not normalized before `TreeExplainer` | `shap_service.py` `_compute_shap()` | MEDIUM | SHAP values computed on out-of-distribution raw features; explanations are misleading |
| 4 | `business_rules.json` uses wrong field names | `business_rules.json` | MEDIUM | All business rules silently fail; `eval()` NameError → all return False |

---

## Recommended Fixes (priority order)

### Fix 1 — Invert score in `scoring_service.py` (2 lines)
```python
# Line ~44: change
score = int(round(proba * 100))
# to:
score = int(round((1 - proba) * 100))

# Line ~97 (inside _iterate_amount): same change
score = int(round(proba * 100))
# to:
score = int(round((1 - proba) * 100))
```

### Fix 2 — Remove wrongly-classified features from `ratio_cols` (or normalize them in frontend)
```python
# In model_service.py _normalize(), remove from ratio_cols:
ratio_cols = ["tendance_solde_3m", "regularite_depots_ecart_type",
              "part_transferts_marchands", "stabilite_lieu_vie",
              "regularite_cotisations_tontine",
              # Remove: "score_aptitude_entrepreneuriale",  <- 0-100 scale
              "score_integrite",
              # Remove: "locus_controle_interne",           <- 0-10 scale  
              "garantie"]
```
**OR** normalize them in the frontend before submission:
- `score_aptitude_entrepreneuriale` → divide by 100
- `locus_controle_interne` → divide by 10 (or whatever the max is)

Confirm against training pipeline which approach matches how the model was trained.

### Fix 3 — Normalize before SHAP in `shap_service.py`
```python
# In _compute_shap(), after:
X = X[feature_order].fillna(0)
# Add:
from app.services.model_service import model_service as _ms
X = _ms._normalize(X)
```

### Fix 4 — Fix `business_rules.json` field names
Replace all conditions with correct feature names matching the features dict. See the mapping table above. The simplest immediate fix is to delete `business_rules.json` so that `RulesService.load()` falls through to `_default_rules()`, which already uses correct field names.
