from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import VehicleType, DeliveryStatus


class VehicleCreate(BaseModel):
    registration_no: str
    vehicle_type: VehicleType
    capacity_kg: float = Field(gt=0)


class VehicleUpdate(BaseModel):
    capacity_kg: float | None = Field(default=None, gt=0)
    is_active: bool | None = None


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registration_no: str
    vehicle_type: VehicleType
    capacity_kg: float
    current_load_kg: float
    is_active: bool


class DeliveryAssignRequest(BaseModel):
    vehicle_id: int
    sequence: int | None = None


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus
    notes: str | None = None


class DeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    vehicle_id: int | None
    status: DeliveryStatus
    sequence: int | None
    picked_up_at: datetime | None
    delivered_at: datetime | None
    notes: str | None
