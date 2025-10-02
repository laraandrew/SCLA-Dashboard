# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine  # single source of truth
from app import models  # ensures models are registered before create_all

# import routers AS MODULES, not functions
from .routers import cars, services, documents, pricing, scan, stickers

# create tables (sqlite default)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SportsCarLA Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(cars.router)
app.include_router(services.router)
app.include_router(documents.router)
app.include_router(pricing.router)
app.include_router(scan.router)
app.include_router(stickers.router)   # <-- THIS mounts /stickers/...

@app.get("/healthz")
def health():
    return {"ok": True}
