from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime
from typing import Optional, Callable

class Car(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stock: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    vin: Optional[str] = None
    odometer: Optional[str] = None
    price: Optional[str] = None
    exterior: Optional[str] = None
    interior: Optional[str] = None
    engine: Optional[str] = None
    transmission: Optional[str] = None
    url: str
    thumb_url: Optional[str] = None
    seller: Optional[str] = None
    buyer: Optional[str] = None
    status: str = "OnLot"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

_engine = create_engine("sqlite:///cars.db")
SQLModel.metadata.create_all(_engine)

def get_db():
    with Session(_engine) as s:
        yield Database(s)

class Database:
    def __init__(self, s: Session):
        self.s = s
    def list_cars(self):
        return self.s.exec(select(Car).order_by(Car.created_at.desc())).all()
    def search(self, q: str):
        stmt = select(Car).where(
            (Car.make.ilike(f"%{q}%")) | (Car.model.ilike(f"%{q}%")) | (Car.vin.ilike(f"%{q}%")) | (Car.stock.ilike(f"%{q}%"))
        ).order_by(Car.created_at.desc())
        return self.s.exec(stmt).all()
    def get(self, id: int) -> Car:
        return self.s.get(Car, id)
    def upsert_from_dict(self, d: dict) -> Car:
        car = Car(**d)
        self.s.add(car)
        self.s.commit()
        self.s.refresh(car)
        return car
    def update(self, car: Car, **fields):
        for k,v in fields.items():
            setattr(car, k, v)
        self.s.add(car)
        self.s.commit()
        self.s.refresh(car)
        return car
