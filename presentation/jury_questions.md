# Questions du jury

## Q: Le score est-il une décision automatique?
R: Non. Le système assiste l'agent de crédit. La décision finale est humaine.

## Q: D'où viennent les données?
R: Dataset existant de 700K lignes fourni par le projet. Aucune génération artificielle.

## Q: Comment le GPU est-il utilisé?
R: Entraînement XGBoost sur Kaggle (Tesla T4). Speedup 7.1x vs CPU.

## Q: Le modèle est-il explicable?
R: Oui. SHAP TreeExplainer fournit les top 10 facteurs positifs/négatifs.

## Q: Que se passe-t-il si les données sont incomplètes?
R: Règles métier détectent le problème, affichent une alerte, et imposent une revue humaine.

## Q: Comment déployer?
R: Frontend sur Vercel, backend sur Render. Version locale hors ligne disponible.