from pydantic import BaseModel
from typing import Optional, List, Tuple

class ServiceItemIn(BaseModel):
    description: str
    parts_cost: float = 0
    labor_hours: float = 0
    labor_rate: float = 125
    vendor: Optional[str] = None

class ServiceItemOut(ServiceItemIn):
    id: int
    class Config:
        from_attributes = True

class CarIn(BaseModel):
    url: str
    vin: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    miles: Optional[int] = None
    price: Optional[float] = None
    status: Optional[str] = "available"

class CarOut(CarIn):
    id: int
    services: List[ServiceItemOut] = []
    class Config:
        from_attributes = True

class PricingEstimate(BaseModel):
    target_sale_low: float
    target_sale_high: float
    target_buy_low: float
    target_buy_high: float
    est_recon_cost: float
    est_profit_range: Tuple[float, float]
