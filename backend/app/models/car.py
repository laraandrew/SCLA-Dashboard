# backend/app/models/car.py
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Source/identity
    url: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    stock: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    vin: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)

    # Display
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    make: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    body_style: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    exterior_color: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    interior_color: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    miles: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    transmission: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    engine: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_raw: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Media
    thumb: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Meta
    status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # "active", "sold", etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # stock/vin are NOT guaranteed unique on this site; we keep soft uniqueness via indexes above
        UniqueConstraint("url", name="uq_car_url"),
    )
