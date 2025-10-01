from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models, schemas
from ..security import require_token

router = APIRouter(prefix="/cars", tags=["cars"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.CarOut, dependencies=[Depends(require_token)])
def create_car(payload: schemas.CarIn, db: Session = Depends(get_db)):
    car = models.Car(**payload.model_dump())
    db.add(car)
    db.commit()
    db.refresh(car)
    return car

@router.get("/", response_model=list[schemas.CarOut])
def list_cars(db: Session = Depends(get_db)):
    return db.query(models.Car).order_by(models.Car.created_at.desc()).all()

@router.get("/{car_id}", response_model=schemas.CarOut)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.get(models.Car, car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    return car
