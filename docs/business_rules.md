# Règles métier

1. **Primo-emprunteur** : limiter le montant initial (×0.7)
2. **Historique insuffisant** (< 6 mois) : imposer une revue humaine
3. **Données incomplètes** (< 70%) : pas de recommandation automatique
4. **Dépenses non renseignées** (< 30%) : réduire confiance et plafond (×0.8)
5. **Incohérences** : suspendre la recommandation automatique
6. **Marge faible malgré CA élevé** : limiter le montant (×0.6)
7. **Activité irrégulière** : recommander un crédit progressif
8. **Confiance faible** : demander des informations complémentaires

## Format

```json
{
  "name": "rule_name",
  "condition": "python_expression",
  "action": "limit_amount|require_human_review|no_auto_recommendation|reduce_amount|progressive_amount|request_additional_info",
  "severity": "error|warning|info"
}
```

Fichier: `backend/rules/business_rules.json`