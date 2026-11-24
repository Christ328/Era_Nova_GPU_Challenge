import json
import sqlite3
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

DB_PATH = settings.BACKEND_DIR / "decisions.db"

class DecisionService:
    @staticmethod
    def _init_db():
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                merchant_id TEXT,
                score INTEGER,
                risk_level TEXT,
                decision TEXT,
                adjusted_amount INTEGER,
                adjusted_duration INTEGER,
                comments TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    @classmethod
    def save_decision(cls, assessment_id: str, merchant_id: str,
                      score: int, risk_level: str, decision: str,
                      adjusted_amount: Optional[int] = None,
                      adjusted_duration: Optional[int] = None,
                      comments: Optional[str] = None) -> dict:
        cls._init_db()
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO decisions
            (id, merchant_id, score, risk_level, decision,
             adjusted_amount, adjusted_duration, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            assessment_id, merchant_id, score, risk_level, decision,
            adjusted_amount, adjusted_duration, comments,
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
        return {"assessment_id": assessment_id, "decision": decision,
                "message": "Décision enregistrée"}

decision_service = DecisionService()