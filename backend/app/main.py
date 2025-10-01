from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from app.db import engine, Base
from app.models.car import Car
from .routers import cars, services, documents, pricing, scan
from .routers.stickers import generate_sticker
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SportsCarLA Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cars.router)
app.include_router(services.router)
app.include_router(documents.router)
app.include_router(pricing.router)
app.include_router(scan.router)

@app.get("/healthz")
def health():
    return {"ok": True}

@app.get("/sticker/{car_id}")
def sticker(car_id: int):
    # TODO: load real car by ID to render exact sticker
    png = generate_sticker({"price": 32999, "year": 1995, "make": "Porsche", "model": "911", "miles": 65432})
    return Response(content=png, media_type="image/png")
