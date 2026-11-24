# GPU Challenge 2026 — Projet de scoring alternatif des petits commerçants

## 1. Résumé du projet

Le projet consiste à développer un système d’aide à la décision pour évaluer le risque de crédit de petits commerçants ne disposant pas d’un historique bancaire formel.

Le système utilise des données synthétiques représentant :

- le profil du commerçant ;
- son activité commerciale ;
- ses transactions simulées sur 6 à 12 mois ;
- ses revenus, dépenses et soldes ;
- un historique synthétique de remboursement ou de défaut.

À partir de ces données, le système calcule un score de 0 à 100, explique les facteurs qui influencent ce score et propose une recommandation de crédit. La décision finale reste sous la responsabilité d’un agent de crédit humain.

> Le système est un outil d’aide à la décision, et non un mécanisme automatique d’acceptation ou de refus de crédit.

---

## 2. Problème traité

Les petits commerçants peuvent avoir une activité réelle mais peu de traces bancaires formelles. Une institution de microfinance dispose donc de peu d’informations classiques pour évaluer leur capacité de remboursement.

Le projet cherche à répondre à la question suivante :

> Comment utiliser des indicateurs alternatifs d’activité pour produire une évaluation de risque compréhensible, prudente et exploitable par un agent de crédit ?

Le projet ne prétend pas utiliser de vraies données bancaires ou mobile-money. Les données sont synthétiques et servent à démontrer la méthode et l’architecture.

---

## 3. Utilisateurs et bénéficiaires

### Utilisateurs directs

- Agent de crédit ;
- responsable risque ;
- institution de microfinance ;
- équipe d’analyse crédit.

### Bénéficiaires finaux

- petits commerçants ;
- microentrepreneurs ;
- commerçants sans historique bancaire formel.

### Rôle de l’agent de crédit

L’agent :

1. sélectionne ou renseigne un commerçant ;
2. consulte son profil et ses indicateurs ;
3. lance l’évaluation ;
4. consulte le score et ses explications ;
5. examine les alertes et règles métier ;
6. accepte, modifie ou rejette la recommandation ;
7. enregistre sa décision humaine.

---

## 4. Fonctionnalités principales

L’application doit permettre de :

1. sélectionner un commerçant synthétique ;
2. afficher son profil et son activité ;
3. afficher ses indicateurs financiers et transactionnels ;
4. calculer un score de crédit de 0 à 100 ;
5. afficher le niveau de risque ;
6. afficher le niveau de confiance et la qualité des données ;
7. proposer un montant indicatif ;
8. proposer une durée indicative ;
9. proposer un type de produit de crédit ;
10. afficher les facteurs SHAP positifs et négatifs ;
11. appliquer les règles métier ;
12. imposer une revue humaine lorsque nécessaire ;
13. enregistrer la décision de l’agent ;
14. afficher la preuve d’utilisation du GPU ;
15. fonctionner localement sans dépendre de Kaggle ou Colab.

---

## 5. Architecture générale

```text
                 DONNÉES SYNTHÉTIQUES
        Profils commerçants + transactions 6–12 mois
                              │
                              ▼
                  GÉNÉRATION ET VALIDATION
                              │
                              ▼
                    FEATURE ENGINEERING
      Revenus, dépenses, régularité, croissance, marge,
        stabilité du solde, activité, complétude des données
                              │
                              ▼
                    ENTRAÎNEMENT GPU/CPU
                XGBoost + comparaison CPU/GPU
                              │
                              ▼
                       MODÈLE EXPORTÉ
                   xgboost_model.json
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
       PRÉDICTION                         EXPLICATION
  Score 0–100, risque,                 SHAP, facteurs clés,
  confiance, recommandation             direction des impacts
             │                                 │
             └────────────────┬────────────────┘
                              ▼
                      RÈGLES MÉTIER
        Plafonds, données insuffisantes, primo-emprunteur,
              incohérences, revue humaine obligatoire
                              │
                              ▼
                    APPLICATION STREAMLIT
       Profil → Évaluation → Explication → Décision humaine
                              │
                              ▼
                  DÉMONSTRATION AU JURY
```

---

## 6. Séparation GPU et application web

### Partie GPU

Le GPU est utilisé pour :

- générer ou traiter de grands volumes de transactions synthétiques ;
- entraîner XGBoost ;
- exécuter des prédictions en lots ;
- tester plusieurs scénarios ;
- calculer éventuellement les contributions explicatives accélérées ;
- comparer les performances CPU et GPU.

L’expérimentation GPU est réalisée dans Google Colab ou Kaggle lorsque le GPU gratuit est disponible. La disponibilité du GPU n’est pas garantie.

### Partie application

L’application Streamlit fonctionne sur CPU avec le modèle déjà entraîné. Elle réalise principalement :

- le chargement du modèle ;
- la prédiction d’un commerçant ;
- l’affichage des explications ;
- l’application des règles métier ;
- la saisie de la décision humaine.

Cette séparation est normale : le GPU sert au calcul intensif, tandis que l’application web reste légère et compatible avec un hébergement gratuit.

---

## 7. Données synthétiques

### Profil commerçant

Exemples de champs :

- `merchant_id` ;
- activité ;
- zone ;
- ancienneté de l’activité ;
- statut de primo-emprunteur ;
- taille estimée de l’activité.

### Transactions

Exemples de champs :

- identifiant du commerçant ;
- date ;
- type de transaction ;
- montant ;
- solde ;
- type de contrepartie.

### Types d’activités possibles

- alimentation ;
- restauration ;
- textile ;
- transport ;
- recharge téléphonique ;
- commerce de détail.

### Types de transactions possibles

- paiement reçu ;
- dépôt ;
- retrait ;
- achat fournisseur ;
- transfert ;
- recharge ;
- remboursement.

### Scénarios générés

- activité stable ;
- activité saisonnière ;
- chiffre d’affaires élevé mais faible marge ;
- activité irrégulière ;
- historique court ;
- données incomplètes ;
- incohérences entre revenus et dépenses.

---

## 8. Variables utilisées par le modèle

Les variables finales sont calculées à partir des transactions et du profil du commerçant.

Exemples :

- revenu mensuel moyen ;
- variabilité des revenus ;
- nombre de jours actifs ;
- nombre de transactions ;
- croissance des revenus ;
- ratio dépenses/revenus ;
- marge estimée ;
- solde moyen ;
- solde minimum ;
- régularité des dépôts ;
- diversité des contreparties ;
- concentration des revenus ;
- saisonnalité ;
- ancienneté de l’activité ;
- complétude des données.

Chaque variable doit avoir :

- un nom technique ;
- un libellé lisible ;
- un type ;
- une unité ;
- une définition ;
- une formule ;
- un traitement des valeurs manquantes.

---

## 9. Modèle de scoring

Le modèle principal est XGBoost pour une classification binaire :

```text
1 = remboursement simulé
0 = défaut simulé
```

Configuration indicative :

```python
XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="hist",
    device="cuda"
)
```

Pour l’entraînement CPU, `device="cpu"` est utilisé.

### Score

Le modèle produit une probabilité transformée en score :

```text
score = probabilité_estimée_de_remboursement × 100
```

Convention retenue :

```text
0   = profil très défavorable ou données insuffisantes
100 = profil plus favorable selon les données synthétiques
```

Le score ne constitue pas une garantie de remboursement réel.

---

## 10. Sortie du moteur de scoring

Exemple de sortie :

```json
{
  "merchant_id": "MCH-DEMO-01",
  "score": 76,
  "risk_level": "moderate",
  "confidence": "medium",
  "recommended_amount_min": 100000,
  "recommended_amount_max": 200000,
  "recommended_duration_months": 6,
  "product_type": "progressive_microloan",
  "human_review_required": true,
  "top_factors": [],
  "alerts": [],
  "explanation": "La régularité de l’activité améliore le score estimé."
}
```

---

## 11. Explicabilité avec SHAP

Pour chaque prédiction, l’application affiche les principaux facteurs qui influencent le score.

Exemples de facteurs positifs :

- activité régulière ;
- revenus stables ;
- croissance récente ;
- solde suffisamment stable.

Exemples de facteurs négatifs :

- dépenses élevées par rapport aux revenus ;
- forte volatilité ;
- concentration des revenus ;
- historique trop court ;
- données manquantes.

Chaque facteur doit être présenté avec :

- son nom lisible ;
- sa valeur ;
- sa contribution ;
- sa direction ;
- une phrase explicative.

Exemple :

> Le nombre élevé de jours actifs améliore le score estimé.

> Le poids important des dépenses réduit la capacité estimée.

---

## 12. Règles métier

Les règles métier complètent le modèle statistique.

Exemples :

1. **Primo-emprunteur** : appliquer un plafond de montant.
2. **Historique trop court** : imposer une revue humaine.
3. **Données incomplètes** : ne pas produire de recommandation automatique.
4. **Dépenses non documentées** : réduire le montant recommandé.
5. **Incohérences détectées** : classer le dossier en revue manuelle.
6. **Confiance faible** : demander des informations complémentaires.
7. **Activité instable** : proposer un montant progressif.
8. **Score élevé mais marge faible** : limiter la recommandation.

La sortie finale doit distinguer :

```text
Score du modèle
+ règles métier
+ décision de l’agent
```

Le système ne doit jamais afficher qu’un crédit est automatiquement accordé.

---

## 13. Trois profils de démonstration

### Profil 1 — Activité régulière

Caractéristiques :

- revenus réguliers ;
- activité fréquente ;
- dépenses cohérentes ;
- données suffisamment complètes.

Résultat attendu :

- score favorable ou modéré ;
- recommandation prudente ;
- confiance relativement élevée ;
- validation humaine maintenue.

### Profil 2 — Chiffre d’affaires élevé mais faible marge

Caractéristiques :

- volume de ventes important ;
- dépenses élevées ;
- marge faible ;
- revenus concentrés sur quelques jours.

Résultat attendu :

- score inférieur à ce que le chiffre d’affaires seul laisserait penser ;
- montant recommandé réduit ;
- explication SHAP montrant le poids des dépenses et l’instabilité.

### Profil 3 — Données insuffisantes

Caractéristiques :

- historique très court ;
- dépenses absentes ;
- informations contradictoires ;
- faible complétude des données.

Résultat attendu :

- confiance faible ou score indéterminé ;
- revue humaine obligatoire ;
- aucune recommandation automatique importante.

---

## 14. Architecture logicielle

```text
gpu-credit-scoring/
├── README.md
├── requirements.txt
├── app/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── components/
│   │   ├── score_card.py
│   │   ├── shap_chart.py
│   │   └── explanation_panel.py
│   └── pages/
│       ├── 01_dashboard.py
│       ├── 02_merchant_profile.py
│       ├── 03_credit_assessment.py
│       ├── 04_explanations.py
│       ├── 05_human_review.py
│       └── 06_gpu_benchmark.py
├── data/
│   ├── merchants.csv
│   ├── transactions.csv
│   ├── labels.csv
│   ├── features.csv
│   ├── test_profiles.csv
│   └── data_dictionary.csv
├── model/
│   ├── xgboost_model.json
│   ├── model_metadata.json
│   ├── model_config.json
│   ├── feature_schema.json
│   └── feature_order.json
├── src/
│   ├── generate_synthetic_data.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── feature_validation.py
│   ├── model_loader.py
│   ├── prediction_service.py
│   ├── scoring.py
│   ├── explain.py
│   └── rules_engine.py
├── rules/
│   ├── business_rules.json
│   └── rules_documentation.md
├── explanations/
│   ├── feature_labels.json
│   ├── explanation_templates.json
│   └── expected_shap_results.json
├── notebooks/
│   ├── 01_data_generation.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_training_cpu_gpu.ipynb
│   └── 04_model_evaluation.ipynb
├── benchmarks/
│   ├── benchmark_cpu_gpu.csv
│   ├── benchmark_summary.json
│   ├── training_config.json
│   └── gpu_training.ipynb
├── tests/
│   ├── test_data_loader.py
│   ├── test_feature_engineering.py
│   ├── test_model.py
│   ├── test_prediction_service.py
│   ├── test_rules_engine.py
│   ├── test_explanations.py
│   └── business_test_cases.md
├── docs/
│   ├── architecture.md
│   ├── feature_interpretation.md
│   ├── assumptions_and_limits.md
│   ├── user_acceptance_report.md
│   └── deployment.md
└── presentation/
    ├── demo_script.md
    ├── gpu_explanation.md
    ├── jury_questions.md
    └── demo_scenarios.md
```

---

## 15. Rôle de chaque membre

### Data scientist

Responsable de :

- génération des données ;
- définition des variables ;
- feature engineering ;
- entraînement CPU/GPU ;
- évaluation du modèle ;
- export du modèle ;
- calcul SHAP ;
- benchmark GPU ;
- documentation scientifique.

### Développeur full-stack

Responsable de :

- dépôt GitHub ;
- architecture Python/Streamlit ;
- chargement des données ;
- intégration du modèle ;
- interface utilisateur ;
- affichage du score et de SHAP ;
- règles métier dans l’application ;
- tests techniques ;
- déploiement ;
- fonctionnement hors ligne.

### Profil métier / produit

Responsable de :

- validation du problème ;
- réalisme des scénarios ;
- règles de crédit ;
- seuils et recommandations ;
- validation des textes ;
- tests comme agent de crédit ;
- scénario de présentation ;
- réponses aux questions du jury.

---

## 16. Ordre chronologique de réalisation

```text
1. Cadrer le problème et les utilisateurs
2. Définir les données et les règles métier
3. Générer les données synthétiques
4. Valider les données avec le profil métier
5. Construire les features
6. Entraîner le modèle CPU et GPU
7. Évaluer et sélectionner le modèle
8. Exporter le modèle
9. Implémenter le score et les recommandations
10. Implémenter les explications SHAP
11. Implémenter les règles métier
12. Construire l’application Streamlit
13. Tester les trois profils de démonstration
14. Mesurer et afficher le benchmark GPU
15. Déployer sur Streamlit Community Cloud
16. Préparer une version locale hors ligne
17. Répéter la démonstration devant le jury
```

---

## 17. Déploiement et démonstration

### Entraînement

- Google Colab ou Kaggle avec GPU disponible ;
- notebook reproductible ;
- modèle exporté après entraînement ;
- résultats du benchmark conservés.

### Hébergement

- Streamlit Community Cloud pour la version publique ;
- exécution locale pour la version principale de secours ;
- aucun téléchargement obligatoire depuis Colab ou Kaggle pendant la démonstration.

### Préparation du jour du jury

L’équipe doit avoir :

1. l’application Streamlit locale ;
2. le modèle déjà téléchargé ;
3. les données de démonstration locales ;
4. une URL Streamlit Cloud ;
5. le notebook GPU ;
6. le benchmark CPU/GPU ;
7. une vidéo ou des captures de secours ;
8. un scénario de démonstration répété.

---

## 18. Message technique à présenter au jury

> Le GPU est utilisé pour accélérer le traitement des historiques transactionnels, l’entraînement XGBoost, les prédictions en lots et l’évaluation de scénarios. Le modèle entraîné est ensuite exporté vers une application Streamlit légère, capable de servir les prédictions sur CPU. L’interface ne prend pas seule la décision : elle fournit à l’agent de crédit un score explicable, des règles métier et une recommandation soumise à validation humaine.

---

## 19. Limites à déclarer

- Les données sont synthétiques.
- Le label de remboursement est simulé.
- Les performances ne représentent pas la performance sur la population réelle.
- Le modèle ne remplace pas une enquête de crédit.
- Le score ne garantit pas le remboursement.
- Les variables peuvent contenir des biais.
- Une validation humaine est nécessaire.
- L’accès au GPU gratuit n’est pas garanti.
- Le GPU n’est pas forcément plus rapide sur un très petit dataset ; l’intérêt est démontré avec des traitements répétés, des lots et des scénarios plus volumineux.

---

## 20. Livrables finaux obligatoires

```text
1. Application Streamlit fonctionnelle
2. Modèle XGBoost exporté
3. Données synthétiques
4. Code de génération des données
5. Code de feature engineering
6. Dictionnaire des variables
7. Fonction de prédiction
8. Fonction d’explication SHAP
9. Moteur de règles métier
10. Trois profils de démonstration
11. Tests techniques et métier
12. Notebook d’entraînement GPU
13. Benchmark CPU/GPU réel
14. Documentation d’installation
15. URL hébergée
16. Version locale hors ligne
17. Script de démonstration
18. Documentation des limites
```
