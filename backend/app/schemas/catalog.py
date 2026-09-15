from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import Unit, QualityGrade, ListingStatus, RequirementStatus


class CropRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    default_unit: Unit


class CropCreate(BaseModel):
    name: str
    default_unit: Unit = Unit.KG


# ---------------------------------------------------------------------
# ProduceListing
# ---------------------------------------------------------------------
class ProduceListingCreate(BaseModel):
    crop_id: int
    variety: str
    quantity: float = Field(gt=0)
    unit: Unit
    price_per_unit: float = Field(gt=0)
    quality_grade: QualityGrade
    harvest_date: date
    available_date: date
    village: str | None = None
    district: str
    state: str
    lat: float
    lng: float
    notes: str | None = None

    @field_validator("available_date")
    @classmethod
    def available_not_before_harvest(cls, v: date, info):
        harvest = info.data.get("harvest_date")
        if harvest and v < harvest:
            raise ValueError("available_date cannot be before harvest_date")
        return v


class ProduceListingUpdate(BaseModel):
    variety: str | None = None
    price_per_unit: float | None = Field(default=None, gt=0)
    quality_grade: QualityGrade | None = None
    notes: str | None = None
    status: ListingStatus | None = None


class ProduceListingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: int
    crop_id: int
    variety: str
    quantity: float
    quantity_reserved: float
    quantity_sold: float
    available_quantity: float
    unit: Unit
    price_per_unit: float
    quality_grade: QualityGrade
    harvest_date: date
    available_date: date
    village: str | None
    district: str
    state: str
    lat: float
    lng: float
    status: ListingStatus
    notes: str | None


# ---------------------------------------------------------------------
# BuyerRequirement
# ---------------------------------------------------------------------
class BuyerRequirementCreate(BaseModel):
    crop_id: int
    variety: str
    required_quantity: float = Field(gt=0)
    unit: Unit
    acceptable_price: float = Field(gt=0)
    required_quality: QualityGrade
    delivery_district: str
    delivery_state: str
    delivery_lat: float
    delivery_lng: float
    required_delivery_date: date


class BuyerRequirementUpdate(BaseModel):
    acceptable_price: float | None = Field(default=None, gt=0)
    required_quality: QualityGrade | None = None
    required_delivery_date: date | None = None
    status: RequirementStatus | None = None


class BuyerRequirementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    buyer_id: int
    crop_id: int
    variety: str
    required_quantity: float
    fulfilled_quantity: float
    remaining_quantity: float
    unit: Unit
    acceptable_price: float
    required_quality: QualityGrade
    delivery_district: str
    delivery_state: str
    delivery_lat: float
    delivery_lng: float
    required_delivery_date: date
    status: RequirementStatus
