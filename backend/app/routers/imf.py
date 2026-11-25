from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import IMFConfig
from app.schemas import IMFConfigCreate, IMFConfigUpdate, IMFConfigResponse

router = APIRouter()


def seed_default_imf(db: Session) -> None:
    """Create the default IMF entry if the table is empty."""
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


@router.delete("/imf/{imf_id}", status_code=204)
def delete_imf(imf_id: int, db: Session = Depends(get_db)):
    obj = db.query(IMFConfig).filter(IMFConfig.id == imf_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="IMF non trouvée")
    db.delete(obj)
    db.commit()
