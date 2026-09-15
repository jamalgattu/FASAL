from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models.enums import UserRole, BuyerType


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    phone: str | None
    role: UserRole
    is_active: bool


class FarmerRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    phone: str | None = None
    is_fpo: bool = False
    org_name: str | None = None
    village: str | None = None
    district: str
    state: str
    lat: float
    lng: float


class BuyerRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    phone: str | None = None
    buyer_type: BuyerType
    org_name: str
    district: str
    state: str
    lat: float
    lng: float


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class TokenPayload(BaseModel):
    sub: str | None = None
