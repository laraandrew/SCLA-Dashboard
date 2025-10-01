from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models, schemas
from ..security import require_token

router = APIRouter(prefix="/services", tags=["services"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{car_id}", response_model=schemas.CarOut, dependencies=[Depends(require_token)])
def add_service(car_id: int, payload: schemas.ServiceItemIn, db: Session = Depends(get_db)):
    car = db.get(models.Car, car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    item = models.ServiceItem(car_id=car_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(car)
    return car
