from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    vin = Column(String(32), nullable=True)
    year = Column(Integer)
    make = Column(String(64))
    model = Column(String(128))
    trim = Column(String(128))
    miles = Column(Integer)
    price = Column(Float)
    status = Column(String(32), default="available")  # available | sold | consignment
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    services = relationship("ServiceItem", back_populates="car", cascade="all, delete-orphan")

class ServiceItem(Base):
    __tablename__ = "service_items"
    id = Column(Integer, primary_key=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"))
    description = Column(Text)
    parts_cost = Column(Float, default=0)
    labor_hours = Column(Float, default=0)
    labor_rate = Column(Float, default=125)
    vendor = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    car = relationship("Car", back_populates="services")

class DocumentTemplate(Base):
    __tablename__ = "document_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    version = Column(String(32), default="v1")
    url = Column(Text)  # link to latest PDF/doc stored in S3/Drive/etc
    active = Column(Boolean, default=True)
