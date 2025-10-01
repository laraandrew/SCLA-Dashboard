from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.car import Car
from app.utils.scraper import get_all_active_urls, scrape_urls_and_persist

router = APIRouter(prefix="/scan", tags=["scan"])

@router.get("/car")
def get_car_by_url(url: str):
    db: Session = SessionLocal()
    try:
        car = db.query(Car).filter_by(url=url).one_or_none()
        if not car:
            return {"error": "not found"}
        return {
            "id": car.id,
            "url": car.url,
            "stock": car.stock,
            "vin": car.vin,
            "year": car.year,
            "make": car.make,
            "model": car.model,
            "body_style": car.body_style,
            "exterior_color": car.exterior_color,
            "interior_color": car.interior_color,
            "miles": car.miles,
            "transmission": car.transmission,
            "engine": car.engine,
            "price": car.price,
            "price_raw": car.price_raw,
            "thumb": car.thumb,
            "status": car.status,
        }
    finally:
        db.close()

from app.utils.scraper import scrape_car_detail

@router.get("/detail")
def scrape_detail(url: str):
    return scrape_car_detail(url)


@router.get("/urls")
def scan_urls(limit: int = Query(36, ge=12, le=100), pages: int = Query(20, ge=1, le=50)):
    return get_all_active_urls(limit=limit, max_pages=pages)

@router.get("/refresh")
def refresh(limit: int = Query(36, ge=12, le=100), pages: int = Query(20, ge=1, le=50)):
    return scrape_urls_and_persist(limit=limit, max_pages=pages)

@router.get("/cars-db")
def cars_db(limit: int = Query(200), offset: int = Query(0)):
    db: Session = SessionLocal()
    try:
        q = db.query(Car).order_by(Car.id.desc())
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        items = [
            {
                "id": c.id,
                "url": c.url,
                "stock": c.stock,
                "vin": c.vin,
                "year": c.year,
                "make": c.make,
                "model": c.model,
                "body_style": c.body_style,
                "exterior_color": c.exterior_color,
                "interior_color": c.interior_color,
                "miles": c.miles,
                "transmission": c.transmission,
                "engine": c.engine,
                "price": c.price,
                "price_raw": c.price_raw,
                "thumb": c.thumb,
                "status": c.status,
            }
            for c in rows
        ]
        return {"count": total, "items": items}
    finally:
        db.close()

# Optional: keep frontend path working
@router.get("/cars")
def cars_alias(limit: int = Query(200), offset: int = Query(0)):
    return cars_db(limit=limit, offset=offset)
