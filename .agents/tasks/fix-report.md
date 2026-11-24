# Bug Fix Report — Eranova Credit Scoring Backend

## Fix 1 — CRITICAL: Invert probability in `scoring_service.py`

**File:** `backend/app/services/scoring_service.py`

The model returns P(default). The score must represent creditworthiness, so it must be `(1 - proba) * 100`, not `proba * 100`.

### Change 1a — `score()` method (line 43)
```diff
- score = int(round(proba * 100))
+ score = int(round((1 - proba) * 100))
```

### Change 1b — `_iterate_amount()` method (line 101)
```diff
- score = int(round(proba * 100))
+ score = int(round((1 - proba) * 100))
```

Both occurrences were changed. Confirmed with grep: no instances of `int(round(proba * 100))` remain.

---

## Fix 2 — HIGH: Wrong normalization scale in `model_service.py`

**File:** `backend/app/services/model_service.py`

`score_aptitude_entrepreneuriale` (0–100 scale) and `locus_controle_interne` (0–10 scale) were included in `ratio_cols` and clipped to [0, 1], which corrupted any value above 1 (e.g., 65 → 1.0, 6 → 1.0).

### Change 2a — Remove the two columns from `ratio_cols`
```diff
  ratio_cols = ["tendance_solde_3m", "regularite_depots_ecart_type",
                "part_transferts_marchands", "stabilite_lieu_vie",
-               "regularite_cotisations_tontine", "score_aptitude_entrepreneuriale",
-               "score_integrite", "locus_controle_interne", "garantie"]
+               "regularite_cotisations_tontine",
+               "score_integrite", "garantie"]
```

### Change 2b — Add explicit per-scale normalization after the `ratio_cols` loop
```python
        # Normalize non-ratio columns with known scales
        if "score_aptitude_entrepreneuriale" in X.columns:
            X["score_aptitude_entrepreneuriale"] = X["score_aptitude_entrepreneuriale"].clip(0, 100) / 100
        if "locus_controle_interne" in X.columns:
            X["locus_controle_interne"] = X["locus_controle_interne"].clip(0, 10) / 10
```

Inserted immediately before `return X` in `_normalize()`.

---

## Fix 3 — MEDIUM: SHAP not normalized in `shap_service.py`

**File:** `backend/app/services/shap_service.py`

`_compute_shap()` passed raw unnormalized features to `shap.TreeExplainer`, while `model_service.predict()` normalizes before inference. SHAP values were computed on a different input distribution than the model was trained on.

### Change 3 — Add normalization call after `fillna(0)`
```diff
  X = X[feature_order].fillna(0)
+ X = model_service._normalize(X)  # normalize before SHAP, same as predict()

  model = model_service._model
```

`model_service` was already imported at the top of the file, so no import change was needed.

---

## Fix 4 — MEDIUM: `business_rules.json` uses wrong field names

**File:** `backend/rules/business_rules.json`

All eight rules used English field names (`is_first_time_borrower`, `activity_age_months`, `data_completeness`, `expense_documentation_ratio`, `has_inconsistencies`, `regularity_score`, `margin_ratio`, `monthly_income_mean`) that do not exist in the features dict. Every rule silently failed via `NameError` inside `eval()`.

### Change 4 — Replace entire file with an empty JSON array
```json
[]
```

When the file contains `[]`, the `for rule in rules` loop in `rules_service.evaluate()` runs zero iterations and returns default adjustments cleanly. This disables the broken rules without modifying any Python code.

---

## Verification Trace

### Fix 1 — grep confirms both occurrences corrected
- Line 43: `score = int(round((1 - proba) * 100))` ✓  
- Line 101: `score = int(round((1 - proba) * 100))` ✓  
- No remaining instances of `int(round(proba * 100))` ✓

### Fix 2 — model_service.py `_normalize()` verified
- `ratio_cols` no longer contains `score_aptitude_entrepreneuriale` or `locus_controle_interne` ✓  
- Explicit `/100` and `/10` division lines present after the loop ✓

### Fix 3 — shap_service.py `_compute_shap()` verified
- `X = model_service._normalize(X)` present between `fillna(0)` and `model = model_service._model` ✓

### Fix 4 — business_rules.json verified
- File contains only `[]` ✓

### Sanity trace — good borrower (P(default) ≈ 0.05)

```
proba = 0.05
score = int(round((1 - 0.05) * 100)) = int(round(95.0)) = 95

_iterate_amount(features, initial_score=95, requested=...):
    95 >= SCORE_THRESHOLD (70) → return (requested, 95, False)   # no loop

iterated = False → no "amount adjusted" alert added

_get_risk_level(95):
    75 <= 95 <= 100 → RiskLevel.VERY_LOW ✓
```

Before the fix, proba=0.05 would have produced `score = int(round(0.05 * 100)) = 5`, which maps to `RiskLevel.VERY_HIGH` — the exact inversion the bug caused.
