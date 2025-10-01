from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models, schemas
from ..utils.pricing_engine import estimate

router = APIRouter(prefix="/pricing", tags=["pricing"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{car_id}", response_model=schemas.PricingEstimate)
def pricing_for_car(car_id: int, db: Session = Depends(get_db)):
    car = db.get(models.Car, car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    data = estimate(car.year or 0, car.make or "", car.model or "", car.miles, car.price)
    return data
