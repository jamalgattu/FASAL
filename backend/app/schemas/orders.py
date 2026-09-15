from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Unit, QualityGrade, OrderStatus


class OrderCreateFromMatch(BaseModel):
    match_id: int


class OrderTransitionRequest(BaseModel):
    new_status: OrderStatus
    note: str | None = None


class OrderStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_status: OrderStatus | None
    to_status: OrderStatus
    changed_by_user_id: int | None
    note: str | None
    created_at: datetime


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int | None
    listing_id: int
    requirement_id: int
    farmer_id: int
    buyer_id: int
    crop_id: int
    variety: str
    quantity: float
    unit: Unit
    agreed_price: float
    total_value: float
    quality_grade: QualityGrade
    pickup_district: str
    pickup_state: str
    delivery_district: str
    delivery_state: str
    required_delivery_date: date
    status: OrderStatus
    version: int
    created_at: datetime


class OrderDetailRead(OrderRead):
    history: list[OrderStatusHistoryRead] = []
