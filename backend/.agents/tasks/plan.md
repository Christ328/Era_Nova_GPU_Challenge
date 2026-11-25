# Plan d'implémentation — Refonte VIGIE-TRUST

## Contexte codebase

- **Framework** : FastAPI + Pydantic v2 + pydantic-settings
- **DB existante** : SQLite brut via `sqlite3` dans `decision_service.py` (pattern à étendre avec SQLAlchemy)
- **Modèles Pydantic** : dans `app/models.py` (pas de SQLAlchemy actuellement)
- **Schémas Enum** : dans `app/schemas.py`
- **Score actuel** : /100 partout — `ml_score`, `business_score`, `RISK_LEVELS`, `SCORE_THRESHOLD`, `AssessmentResponse.score`
- **Router assessments** : `POST /assessments/score` retourne `AssessmentResponse` (défini dans `models.py`)
- **Pas de tests** dans le repo — vérification par démarrage du serveur (`uvicorn app.main:app`)
- **Commande de vérification** : `cd backend && uvicorn app.main:app --reload` puis `curl http://localhost:8000/docs`

---

## Ordre de dépendance

```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10
         ↓
     (database.py requis par 4, 8)
```

---

## Plan détaillé

- [ ] 1. **Renommage "GPU Credit Scoring" → "VIGIE-TRUST"**

  Remplacer toutes les occurrences de la chaîne `"GPU Credit Scoring"` par `"VIGIE-TRUST"` dans :
  - `app/main.py` : `title=`, `description=`, la route `/` (message et return dict)
  - Tout commentaire ou docstring qui contient cette chaîne dans les autres fichiers (vérifier `scoring_service.py`, `rules_service.py`)

  Modifications :
  - `app/main.py` — `title="VIGIE-TRUST API"`, `description="API d'aide à la décision VIGIE-TRUST"`, `return {"message": "VIGIE-TRUST API", ...}`

  **Fichiers** : `app/main.py`

  **Vérification** : `uvicorn app.main:app --reload` → `GET /` retourne `{"message": "VIGIE-TRUST API", ...}` ; `/docs` affiche "VIGIE-TRUST API" dans le titre.

---

- [ ] 2. **Score /1000 : mettre à jour `scoring_service.py`**

  Modifier `ScoringService` et les constantes globales selon les règles suivantes.

  **Constantes à remplacer** (lignes exactes) :
  ```python
  # Avant
  RISK_LEVELS = [
      (0, 29, ...VERY_HIGH...), (30, 44, ...HIGH...), (45, 59, ...MODERATE...),
      (60, 74, ...LOW...), (75, 100, ...VERY_LOW...),
  ]
  SCORE_THRESHOLD = 70

  # Après
  RISK_LEVELS = [
      (0, 299, RiskLevel.VERY_HIGH, "#C2414B"),
      (300, 449, RiskLevel.HIGH, "#C47B12"),
      (450, 599, RiskLevel.MODERATE, "#C47B12"),
      (600, 749, RiskLevel.LOW, "#168A62"),
      (750, 1000, RiskLevel.VERY_LOW, "#168A62"),
  ]
  SCORE_THRESHOLD = 700
  ```

  **Dans `ScoringService.score()`** :
  - `ml_score = int(round((1 - proba) * 1000))` puis `max(0, min(1000, ml_score))`
  - `business_score` : la fonction `compute_business_score` retourne déjà 0–100 ; multiplier par 10 pour le normaliser sur 1000 : `business_score = int(round(business_score_val * 10))`
  - Plafonnement final : `score = max(0, min(1000, score))`
  - `_apply_score_caps` : remplacer les plafonds `10/20/30/45/25/50` par leurs équivalents ×10 : `100/200/300/450/250/500`
  - `_iterate_amount` : mettre à jour `ml_s`, `biz_s`, `score` pour travailler sur 1000 (même logique, `max(0, min(1000, ...))`)
  - `_recommend` : les seuils `>= 75` et `>= 45` deviennent `>= 750` et `>= 450`
  - `_build_explanation` : remplacer la chaîne `/100` par `/1000`
  - `_get_confidence_level` : les seuils CONFIDENCE_LEVELS restent en pourcentage relatif à 100 (la valeur de confiance est entre 0 et 1 et multipliée par 100 dans `_get_confidence_level`) — **ne pas modifier**

  **Dans `app/models.py`** :
  - `AssessmentResponse.score : int = Field(ge=0, le=1000)` (était `le=100`)

  **Fichiers** : `app/services/scoring_service.py`, `app/models.py`

  **Vérification** : démarrer le serveur et appeler `POST /api/v1/assessments/score` avec un payload minimal `{"montant_demande": 100000, "revenu_mensuel_declare": 50000}` — le champ `score` retourné doit être compris entre 0 et 1000.

---

- [ ] 3. **Créer `app/database.py` — connexion SQLite via SQLAlchemy**

  Créer le fichier `app/database.py` avec le moteur SQLAlchemy, la `SessionLocal`, et `Base`.
  Utiliser SQLite synchrone (pas `aiosqlite`) pour rester cohérent avec le pattern existant dans `decision_service.py` (synchrone). Le chemin de la DB : `settings.BACKEND_DIR / "vigie_trust.db"`.

  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker, DeclarativeBase
  from app.config import settings

  SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.BACKEND_DIR / 'vigie_trust.db'}"

  engine = create_engine(
      SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
  )
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

  class Base(DeclarativeBase):
      pass

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```

  **Fichiers** : `app/database.py` (nouveau)

  **Vérification** : `python -c "from app.database import engine, Base; print('OK')"` depuis `backend/` retourne `OK` sans erreur.

---

- [ ] 4. **Ajouter le modèle SQLAlchemy `IMFConfig` dans `app/models.py`**

  Ajouter en bas de `app/models.py` les imports SQLAlchemy et la classe `IMFConfig`.
  Conserver tous les modèles Pydantic existants intacts.

  ```python
  # --- SQLAlchemy models ---
  from sqlalchemy import Column, Integer, String, Float, DateTime
  from sqlalchemy.sql import func
  from app.database import Base

  class IMFConfig(Base):
      __tablename__ = "imf_configs"

      id = Column(Integer, primary_key=True, index=True)
      name = Column(String, nullable=False)
      interest_rate_annual = Column(Float, default=0.15)
      processing_fee = Column(Float, default=0.02)
      insurance_rate = Column(Float, default=0.005)
      max_amount_first_borrower = Column(Integer, default=50000)
      max_amount_regular = Column(Integer, default=500000)
      min_duration_months = Column(Integer, default=3)
      max_duration_months = Column(Integer, default=24)
      auto_accept_score = Column(Integer, default=700)
      manual_review_score = Column(Integer, default=500)
      max_effort_rate = Column(Float, default=0.45)
      guarantee_required_above = Column(Integer, default=200000)
      bonus_tontine = Column(Integer, default=40)
      bonus_guarantee = Column(Integer, default=30)
      malus_first_borrower = Column(Integer, default=-50)
      malus_fraud = Column(Integer, default=-80)
      trend_weight = Column(Float, default=0.20)
      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())
  ```

  **Fichiers** : `app/models.py`

  **Vérification** : `python -c "from app.models import IMFConfig; print(IMFConfig.__tablename__)"` → `imf_configs`.

---

- [ ] 5. **Ajouter les schémas Pydantic IMF dans `app/schemas.py`**

  Ajouter à la fin de `app/schemas.py` les trois classes Pydantic pour l'IMF.

  ```python
  from pydantic import BaseModel
  from typing import Optional
  from datetime import datetime

  class IMFConfigBase(BaseModel):
      name: str
      interest_rate_annual: float = 0.15
      processing_fee: float = 0.02
      insurance_rate: float = 0.005
      max_amount_first_borrower: int = 50000
      max_amount_regular: int = 500000
      min_duration_months: int = 3
      max_duration_months: int = 24
      auto_accept_score: int = 700
      manual_review_score: int = 500
      max_effort_rate: float = 0.45
      guarantee_required_above: int = 200000
      bonus_tontine: int = 40
      bonus_guarantee: int = 30
      malus_first_borrower: int = -50
      malus_fraud: int = -80
      trend_weight: float = 0.20

  class IMFConfigCreate(IMFConfigBase):
      pass

  class IMFConfigUpdate(IMFConfigBase):
      name: Optional[str] = None
      # all fields optional for partial update

  class IMFConfigResponse(IMFConfigBase):
      id: int
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None

      model_config = {"from_attributes": True}
  ```

  **Fichiers** : `app/schemas.py`

  **Vérification** : `python -c "from app.schemas import IMFConfigCreate, IMFConfigUpdate, IMFConfigResponse; print('OK')"` → `OK`.

---

- [ ] 6. **Créer le router IMF `app/routers/imf.py`**

  Créer `app/routers/imf.py` avec les 5 endpoints CRUD et le seeder de démarrage.

  Structure :
  - Dépendance `get_db` injectée via `Depends(get_db)`
  - Fonction `seed_default_imf(db)` : crée une IMF par défaut nommée `"IMF_DEFAULT"` si la table est vide
  - `GET /imf` → liste toutes les IMF (`List[IMFConfigResponse]`)
  - `POST /imf` → crée (`IMFConfigCreate` → `IMFConfigResponse`)
  - `GET /imf/{imf_id}` → détail ou 404
  - `PUT /imf/{imf_id}` → mise à jour partielle (`IMFConfigUpdate` → `IMFConfigResponse`) ou 404
  - `DELETE /imf/{imf_id}` → suppression ou 404, retourne `{"message": "IMF supprimée"}`

  Le seeder sera appelé depuis `main.py` au démarrage (voir étape 10).

  ```python
  from fastapi import APIRouter, Depends, HTTPException
  from sqlalchemy.orm import Session
  from typing import List
  from app.database import get_db
  from app.models import IMFConfig
  from app.schemas import IMFConfigCreate, IMFConfigUpdate, IMFConfigResponse

  router = APIRouter()

  def seed_default_imf(db: Session):
      if db.query(IMFConfig).count() == 0:
          default = IMFConfig(name="IMF_DEFAULT")
          db.add(default)
          db.commit()

  @router.get("/imf", response_model=List[IMFConfigResponse])
  def list_imf(db: Session = Depends(get_db)):
      return db.query(IMFConfig).all()

  @router.post("/imf", response_model=IMFConfigResponse, status_code=201)
  def create_imf(payload: IMFConfigCreate, db: Session = Depends(get_db)):
      obj = IMFConfig(**payload.model_dump())
      db.add(obj)
      db.commit()
      db.refresh(obj)
      return obj

  @router.get("/imf/{imf_id}", response_model=IMFConfigResponse)
  def get_imf(imf_id: int, db: Session = Depends(get_db)):
      obj = db.query(IMFConfig).filter(IMFConfig.id == imf_id).first()
      if not obj:
          raise HTTPException(status_code=404, detail="IMF non trouvée")
      return obj

  @router.put("/imf/{imf_id}", response_model=IMFConfigResponse)
  def update_imf(imf_id: int, payload: IMFConfigUpdate, db: Session = Depends(get_db)):
      obj = db.query(IMFConfig).filter(IMFConfig.id == imf_id).first()
      if not obj:
          raise HTTPException(status_code=404, detail="IMF non trouvée")
      for field, value in payload.model_dump(exclude_unset=True).items():
          setattr(obj, field, value)
      db.commit()
      db.refresh(obj)
      return obj

  @router.delete("/imf/{imf_id}")
  def delete_imf(imf_id: int, db: Session = Depends(get_db)):
      obj = db.query(IMFConfig).filter(IMFConfig.id == imf_id).first()
      if not obj:
          raise HTTPException(status_code=404, detail="IMF non trouvée")
      db.delete(obj)
      db.commit()
      return {"message": "IMF supprimée"}
  ```

  **Fichiers** : `app/routers/imf.py` (nouveau)

  **Vérification** : `python -c "from app.routers.imf import router; print('OK')"` → `OK`.

---

- [ ] 7. **Créer le service TEG `app/services/teg_service.py`**

  Créer `app/services/teg_service.py` avec Newton-Raphson. Ne pas utiliser `scipy` — implémenter Newton-Raphson manuellement (3 lignes, pas de dépendance supplémentaire, cohérent avec les autres services qui n'utilisent pas scipy).

  Logique :
  - `compute_teg(principal, monthly_payment, n_months, fees, insurance_rate) -> float`
  - Valeur présente des flux : `PV(i) = sum(monthly_payment / (1+i)^t, t=1..n) - fees`  
    où `fees = principal * fees_rate + principal * insurance_rate * n_months / 12`
  - Chercher `i` tel que `PV(i) = principal` ↔ `f(i) = PV(i) - principal = 0`
  - Dérivée : `f'(i) = -sum(t * monthly_payment / (1+i)^(t+1), t=1..n)`
  - Newton-Raphson : `i = i - f(i)/f'(i)`, max 100 itérations, convergence `|f(i)| < 1e-8`
  - `teg_annual = (1 + i_mensuel) ** 12 - 1`
  - Lever `TEGExceededException` (exception custom définie dans le même fichier) si `teg_annual > 0.24`
  - Valeur initiale : `i0 = 0.01` (1% mensuel)

  ```python
  class TEGExceededException(Exception):
      def __init__(self, teg: float):
          self.teg = teg
          super().__init__(f"TEG {teg:.2%} dépasse le plafond réglementaire de 24%")

  def compute_teg(principal: float, monthly_payment: float,
                  n_months: int, fees_rate: float, insurance_rate: float) -> float:
      fees = principal * fees_rate + principal * insurance_rate * n_months / 12
      adjusted_principal = principal + fees

      i = 0.01
      for _ in range(100):
          pv = sum(monthly_payment / (1 + i) ** t for t in range(1, n_months + 1))
          f = pv - adjusted_principal
          df = -sum(t * monthly_payment / (1 + i) ** (t + 1) for t in range(1, n_months + 1))
          if abs(df) < 1e-12:
              break
          i = i - f / df
          if abs(f) < 1e-8:
              break

      teg_annual = (1 + i) ** 12 - 1
      if teg_annual > 0.24:
          raise TEGExceededException(teg_annual)
      return teg_annual
  ```

  **Fichiers** : `app/services/teg_service.py` (nouveau)

  **Vérification** : `python -c "from app.services.teg_service import compute_teg; print(round(compute_teg(100000, 5000, 24, 0.02, 0.005), 4))"` — retourne un float sans erreur.

---

- [ ] 8. **Créer le service anti-fraude `app/services/fraud_service.py`**

  Créer `app/services/fraud_service.py` avec deux fonctions.

  `detect_circular_transactions(transactions: list) -> bool` :
  - Chaque transaction est un dict `{"from": str, "to": str, "amount": float, "timestamp": float}` (timestamp UNIX)
  - Construire un graphe orienté : arête de `from` vers `to` si `montants similaires à ±10%` ET `|t1 - t2| < 86400` pour toute paire d'arêtes dans le graphe
  - DFS pour détecter un cycle (backtracking avec un ensemble `visiting`) — retourner `True` si cycle trouvé
  - Décision : inclure toutes les arêtes qui respectent les deux conditions ; si le graphe ainsi formé a un cycle, c'est une fraude

  `compute_trend_score(balances: list[float]) -> float` :
  - Régression linéaire simple (pente) sur les indices 0..n-1
  - `slope = (n*sum(i*b) - sum(i)*sum(b)) / (n*sum(i²) - sum(i)²)` (formule directe, pas de numpy requis)
  - Normaliser : `score = max(-1.0, min(1.0, slope / max(abs(balances))))`  
    — si `max(abs(balances)) == 0`, retourner `0.0`

  **Fichiers** : `app/services/fraud_service.py` (nouveau)

  **Vérification** : `python -c "from app.services.fraud_service import detect_circular_transactions, compute_trend_score; print(compute_trend_score([100, 200, 300]))"` → retourne un float positif.

---

- [ ] 9. **Ajouter `generate_counter_proposals` dans `scoring_service.py`**

  Ajouter la méthode `generate_counter_proposals(self, features: dict, imf_config) -> list` à `ScoringService`.

  Scénarios à tester (6 scénarios) :
  | Label | Montant | Durée |
  |---|---|---|
  | "M-10%" | `montant_demande * 0.9` | durée originale |
  | "M-20%" | `montant_demande * 0.8` | durée originale |
  | "M + n+3" | `montant_demande` | `duree_credit_mois + 3` |
  | "M + n+6" | `montant_demande` | `duree_credit_mois + 6` |
  | "M-10% + n+3" | `montant_demande * 0.9` | `duree_credit_mois + 3` |
  | "M + garantie" | `montant_demande` | durée originale (bonus garantie appliqué) |

  Pour chaque scénario :
  1. Construire `test_features = {**features, "montant_demande": amount, "duree_credit_mois": duration}`
  2. Pour le scénario "M + garantie", ajouter aussi `"garantie": 1`
  3. Appeler `self.score(test_features)` pour obtenir le score hybride
  4. Calculer `effort_rate = (amount / duration) / max(features.get("revenu_mensuel_declare", 1), 1)`
  5. Filtrer : garder uniquement si `scenario_score >= imf_config.auto_accept_score`
  6. Trier par score décroissant, retourner les 3 premiers

  Format de retour :
  ```python
  {"amount": int, "duration": int, "score": int, "effort_rate": float, "label": str}
  ```

  **Important** : `generate_counter_proposals` appelle `self.score()` récursivement — mettre un paramètre `_depth=0` pour éviter l'infini si jamais la contre-proposition elle-même déclenche une autre, et ne pas appeler `generate_counter_proposals` depuis l'intérieur de `score()`.

  **Fichiers** : `app/services/scoring_service.py`

  **Vérification** : démarrer le serveur et vérifier que l'import fonctionne sans erreur circulaire.

---

- [ ] 10. **Mettre à jour `AssessmentResponse` et créer `ScoringResponse` dans `app/models.py`**

  Le format de réponse requis dans l'étape 8 du cahier des charges est différent de `AssessmentResponse` actuel. Ajouter un nouveau modèle `ScoringResponse` pour `POST /assessments/score` tout en conservant `AssessmentResponse` pour `POST /assessments/{merchant_id}`.

  ```python
  class CounterProposal(BaseModel):
      amount: int
      duration: int
      score: int
      effort_rate: float
      label: str

  class ScoringResponse(BaseModel):
      merchant_id: str
      score: int = Field(ge=0, le=1000)
      score_max: int = 1000
      risk_level: RiskLevel
      decision: str                       # ACCEPTED | MANUAL_REVIEW | REFUSED_RISK | REFUSED_REGULATORY
      ml_score: Optional[int] = None
      business_score: Optional[int] = None
      score_weights: Optional[dict] = None
      teg: Optional[float] = None
      teg_blocked: bool = False
      fraud_detected: bool = False
      counter_proposals: List[CounterProposal] = []
      top_factors: List[ShapFactor]
      explanation: str
      alerts: List[Alert]
      confidence: ConfidenceLevel
      data_quality: float = Field(ge=0, le=1)
      recommended_amount_min: int
      recommended_amount_max: int
      recommended_duration_months: int
      product_type: ProductType
      human_review_required: bool
  ```

  **Fichiers** : `app/models.py`

  **Vérification** : `python -c "from app.models import ScoringResponse, CounterProposal; print('OK')"` → `OK`.

---

- [ ] 11. **Mettre à jour `POST /api/v1/assessments/score` dans `assessments.py`**

  Réécrire le handler `score_custom` pour :

  1. Accepter un paramètre `imf_id: int = 1` (query param ou dans le corps — choisir query param pour ne pas casser le body `features: dict`)
  2. Ouvrir une session DB, charger `IMFConfig` par `imf_id` (404 si absent)
  3. Appeler `scoring_service.score(features)` → `result`
  4. **Bonus/malus IMF** sur le score final :
     - Si `features.get("membre_tontine")` : `result["score"] += imf.bonus_tontine`
     - Si `features.get("garantie")` : `result["score"] += imf.bonus_guarantee`
     - Si `features.get("premiere_fois")` : `result["score"] += imf.malus_first_borrower` (valeur négative)
     - Reclamper : `result["score"] = max(0, min(1000, result["score"]))`
  5. **Fraude** : si `features.get("transactions")` est une liste, appeler `detect_circular_transactions(features["transactions"])` ; si True, `result["score"] += imf.malus_fraud`, reclamper, `fraud_detected = True`
  6. **TEG** : calculer `monthly_payment = features.get("mensualite", (features.get("montant_demande", 0) / max(features.get("duree_credit_mois", 1), 1)) * 1.1)` ; appeler `compute_teg(...)` dans un try/except `TEGExceededException` → `teg_blocked = True`, ajouter une alerte `error`
  7. **Décision** :
     ```
     score >= imf.auto_accept_score                    → ACCEPTED
     imf.manual_review_score <= score < imf.auto_accept_score → MANUAL_REVIEW
     teg_blocked                                       → REFUSED_REGULATORY
     score < imf.manual_review_score                   → REFUSED_RISK
     ```
     Priorité : `teg_blocked` prend le dessus sur `ACCEPTED`.
  8. **Contre-propositions** : si décision != ACCEPTED → `counter_proposals = scoring_service.generate_counter_proposals(features, imf)`
  9. Retourner `ScoringResponse` avec tous les champs

  Signature du handler :
  ```python
  @router.post("/assessments/score", response_model=ScoringResponse)
  def score_custom(features: dict, imf_id: int = 1, db: Session = Depends(get_db)):
  ```

  **Fichiers** : `app/routers/assessments.py`

  **Vérification** : `POST /api/v1/assessments/score?imf_id=1` avec `{"montant_demande": 100000, "revenu_mensuel_declare": 50000, "duree_credit_mois": 12}` — réponse JSON inclut les champs `decision`, `teg`, `teg_blocked`, `fraud_detected`, `counter_proposals`, `score_max`.

---

- [ ] 12. **Mettre à jour `app/main.py` : enregistrer le router IMF et créer les tables au démarrage**

  Deux modifications :
  1. Importer et enregistrer `imf.router`
  2. Ajouter un `lifespan` FastAPI pour :
     - Créer toutes les tables SQLAlchemy (`Base.metadata.create_all(bind=engine)`)
     - Appeler `seed_default_imf` avec une session DB

  ```python
  from contextlib import asynccontextmanager
  from app.database import engine, Base, SessionLocal, get_db
  from app.routers import imf
  from app.models import IMFConfig  # pour que SQLAlchemy enregistre la table
  from app.routers.imf import seed_default_imf

  @asynccontextmanager
  async def lifespan(app: FastAPI):
      Base.metadata.create_all(bind=engine)
      db = SessionLocal()
      try:
          seed_default_imf(db)
      finally:
          db.close()
      yield

  app = FastAPI(
      title="VIGIE-TRUST API",
      ...
      lifespan=lifespan,
  )
  ...
  app.include_router(imf.router, prefix=settings.API_V1_PREFIX, tags=["imf"])
  ```

  **Fichiers** : `app/main.py`

  **Vérification** : `uvicorn app.main:app --reload` démarre sans erreur ; `GET /api/v1/imf` retourne `[{"id": 1, "name": "IMF_DEFAULT", ...}]`.

---

- [ ] 13. **Mettre à jour `requirements.txt`**

  Ajouter les dépendances manquantes :
  ```
  sqlalchemy>=2.0
  ```

  Note : `aiosqlite` n'est pas nécessaire car l'implémentation est synchrone. `scipy` n'est pas nécessaire car Newton-Raphson est implémenté manuellement (étape 7). Ne pas ajouter de dépendances inutiles.

  **Fichiers** : `requirements.txt`

  **Vérification** : `pip install -r requirements.txt` s'exécute sans erreur d'incompatibilité.

---

## Résumé des fichiers

| Fichier | Action |
|---|---|
| `app/main.py` | Modifier (renommage, lifespan, router imf) |
| `app/models.py` | Modifier (score /1000, IMFConfig SQLAlchemy, ScoringResponse, CounterProposal) |
| `app/schemas.py` | Modifier (IMFConfigCreate, IMFConfigUpdate, IMFConfigResponse) |
| `app/config.py` | Pas de modification |
| `app/database.py` | **Créer** |
| `app/services/scoring_service.py` | Modifier (score /1000, generate_counter_proposals) |
| `app/services/teg_service.py` | **Créer** |
| `app/services/fraud_service.py` | **Créer** |
| `app/routers/imf.py` | **Créer** |
| `app/routers/assessments.py` | Modifier (score_custom avec IMF, TEG, fraude, contre-propositions) |
| `requirements.txt` | Modifier (ajouter sqlalchemy>=2.0) |

## Commande de vérification globale

```bash
cd c:\Users\Omnibook\Desktop\GPU_Challenge\Eranova\backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Puis dans un second terminal :
```bash
curl http://localhost:8000/
curl http://localhost:8000/api/v1/imf
curl -X POST http://localhost:8000/api/v1/assessments/score?imf_id=1 \
  -H "Content-Type: application/json" \
  -d '{"montant_demande": 100000, "revenu_mensuel_declare": 50000, "duree_credit_mois": 12}'
```

La réponse doit contenir `score_max`, `decision`, `teg`, `teg_blocked`, `fraud_detected`, `counter_proposals`.
