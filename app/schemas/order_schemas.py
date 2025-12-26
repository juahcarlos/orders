import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"


class OrderCreate(BaseModel):
    items: str
    total_price: float
    status: OrderStatus = OrderStatus.PENDING


class OrderResponse(OrderCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: int
    created_at: datetime
