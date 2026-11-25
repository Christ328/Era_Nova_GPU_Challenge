# Hybrid scoring engine for Eranova micro-credit — re-review pass 2

The change replaces raw XGBoost output as the sole credit score with a weighted combination of the ML score and a purpose-built business rules score. The rules engine (`compute_business_score`) evaluates ten domain rules covering liquidity, tontine participation, revenue coherence, repayment burden, guarantee leverage, first-loan paradox, balance momentum, and professional integration. The final hybrid score adapts its weights based on data quality: 0.55 ML / 0.45 rules when data quality ≥ 0.5, and 0.35 ML / 0.65 rules below that threshold. The amount-iteration loop in `_iterate_amount` uses the hybrid formula and is now efficient.

**Watch for:** R18 sign fix is confirmed correct. R10 spurious else-branch is gone. `_iterate_amount` now extracts `data_quality` once before the loop. All four findings from pass 1 are resolved with no new issues introduced.

**Verdict**: APPROVED

---

## High-level view

All pass-1 findings have been addressed. R18 (balance momentum) now correctly penalizes the 0 < tendance ≤ 0.15 zone with −5 instead of the previous erroneous +3. R10 (revenue coherence) drops the undocumented else-branch; the rule now has exactly the two outcomes defined in the spec (+12 and −8), eliminating the unintended score inflation for borderline cash-flow profiles. The normalization constants (raw_min=−88, raw_max=104) remain valid given these corrections — with the +4 else-branch removed and R18 fixed, the theoretical maximum raw sum is unchanged at 104.

`_iterate_amount` now computes `data_quality` once before the loop using the outer `features` dict and reuses `dq` and the derived weights `(a, b)` across all iterations. The previous concern about up to ~59 redundant recomputations per scoring call is gone.

The frontend `Assessment` interface and breakdown card are unchanged from pass 1 and remain consistent: the three new fields (`ml_score`, `business_score`, `score_weights`) are optional and the breakdown card renders only when at least one is present.

---

<details>
<summary>Issues (0)</summary>

No open issues. All pass-1 findings resolved.

</details>

---

<details>
<summary>Details</summary>

## Pass-1 findings: resolution status

**R18 sign error (confirmed fixed)** — The `elif tendance > 0` branch now reads `raw -= 5`, matching the spec's penalty for sluggish positive momentum. The previous `raw += 3` is gone.

**R10 undocumented else-branch (confirmed fixed)** — The else-branch (`raw += 4`) has been removed. R10 now has exactly two branches: `+12` for 0.5 ≤ coherence ≤ 2.0 and `−8` for coherence < 0.2, consistent with the spec.

**raw_max validity (resolved by R10 fix)** — With the +4 else-branch removed, the raw_max=104 constant is correct for the current rule set. No normalization drift.

**`_iterate_amount` efficiency (confirmed fixed)** — `dq` and `(a, b)` are now computed once before the loop body:

```python
dq = self._get_data_quality(features)
a, b = (0.35, 0.65) if dq < 0.5 else (0.55, 0.45)

for amount in range(requested - 5000, 4999, -5000):
    test_features = {**features, "montant_demande": amount}
    ...
    score = int(round(a * ml_s + b * biz_s))
```

The loop no longer calls `_get_data_quality` on each step.

</details>

---

<details>
<summary>Files changed</summary>

- `backend/app/services/rules_service.py` — R18 branch corrected (`+3` → `−5`); R10 else-branch removed
- `backend/app/services/scoring_service.py` — `_iterate_amount` efficiency fix: `data_quality` extracted before loop
- `backend/app/schemas.py` — unchanged
- `frontend/src/types/assessment.ts` — unchanged from pass 1
- `frontend/src/pages/CustomScorePage.tsx` — unchanged from pass 1

Full diff: `git diff main` from workspace root.

</details>
