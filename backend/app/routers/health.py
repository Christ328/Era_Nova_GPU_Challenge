from fastapi import APIRouter
from app.services.model_service import model_service

router = APIRouter()

@router.get("/health")
def health():
    model_service.load()
    return {
        "status": "ok",
        "model_loaded": model_service._model is not None,
        "features_count": len(model_service.get_feature_names()),
    }