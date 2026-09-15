from datetime import datetime
from typing import Optional

from sqlalchemy import String, Numeric, Boolean, Integer, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import VehicleType, DeliveryStatus


class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    registration_no: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(SAEnum(VehicleType, name="vehicle_type"), nullable=False)
    capacity_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    current_load_kg: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    deliveries: Mapped[list["Delivery"]] = relationship(back_populates="vehicle")


class Delivery(Base, TimestampMixin):
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    vehicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vehicles.id"), nullable=True)
    status: Mapped[DeliveryStatus] = mapped_column(SAEnum(DeliveryStatus, name="delivery_status"), default=DeliveryStatus.PENDING, nullable=False)
    sequence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    picked_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="delivery")
    vehicle: Mapped[Optional["Vehicle"]] = relationship(back_populates="deliveries")
