from pydantic import BaseModel, ConfigDict

from app.models.enums import BuyerType


class FarmerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    is_fpo: bool
    org_name: str | None
    village: str | None
    district: str
    state: str
    lat: float
    lng: float
    full_name: str | None = None  # populated from the linked User in the router


class FarmerUpdate(BaseModel):
    org_name: str | None = None
    village: str | None = None
    district: str | None = None
    state: str | None = None
    lat: float | None = None
    lng: float | None = None


class BuyerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    buyer_type: BuyerType
    org_name: str
    district: str
    state: str
    lat: float
    lng: float


class BuyerUpdate(BaseModel):
    buyer_type: BuyerType | None = None
    org_name: str | None = None
    district: str | None = None
    state: str | None = None
    lat: float | None = None
    lng: float | None = None
