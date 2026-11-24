from fastapi import APIRouter
from app.services.rules_service import rules_service

router = APIRouter()

@router.get("/rules")
def get_rules():
    rules = rules_service.load()
    return {"rules": rules, "count": len(rules)}