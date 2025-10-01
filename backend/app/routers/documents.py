from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models

router = APIRouter(prefix="/documents", tags=["documents"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_templates(db: Session = Depends(get_db)):
    return db.query(models.DocumentTemplate).filter(models.DocumentTemplate.active==True).all()
