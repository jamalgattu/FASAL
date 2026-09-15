from typing import Optional

from sqlalchemy import String, Boolean, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import UserRole, BuyerType


class User(Base, TimestampMixin):
    """Every login-capable account: farmers, FPO reps, buyers, and admins."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    farmer_profile: Mapped[Optional["Farmer"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    buyer_profile: Mapped[Optional["Buyer"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class Farmer(Base, TimestampMixin):
    """
    Represents both an individual farmer and an FPO (Farmer Producer
    Organization) — `is_fpo` distinguishes the two. The /fpos API is a
    filtered view over this same table rather than a separate entity,
    since an FPO is operationally just a farmer account that aggregates
    produce on behalf of its members.
    """

    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_fpo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    org_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    village: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    district: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(255), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped["User"] = relationship(back_populates="farmer_profile")
    listings: Mapped[list["ProduceListing"]] = relationship(back_populates="farmer")


class Buyer(Base, TimestampMixin):
    __tablename__ = "buyers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    buyer_type: Mapped[BuyerType] = mapped_column(SAEnum(BuyerType, name="buyer_type"), nullable=False)
    org_name: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(255), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped["User"] = relationship(back_populates="buyer_profile")
    requirements: Mapped[list["BuyerRequirement"]] = relationship(back_populates="buyer")
