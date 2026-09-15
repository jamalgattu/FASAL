from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Enum as SAEnum, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import Unit, QualityGrade, OrderStatus


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[Optional[int]] = mapped_column(ForeignKey("matches.id"), nullable=True, unique=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("produce_listings.id"), nullable=False, index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("buyer_requirements.id"), nullable=False, index=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id"), nullable=False, index=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("buyers.id"), nullable=False, index=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), nullable=False)

    variety: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[Unit] = mapped_column(SAEnum(Unit, name="order_unit"), nullable=False)
    agreed_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_value: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    quality_grade: Mapped[QualityGrade] = mapped_column(SAEnum(QualityGrade, name="order_quality_grade"), nullable=False)

    pickup_district: Mapped[str] = mapped_column(String(255), nullable=False)
    pickup_state: Mapped[str] = mapped_column(String(255), nullable=False)
    pickup_lat: Mapped[float] = mapped_column(Float, nullable=False)
    pickup_lng: Mapped[float] = mapped_column(Float, nullable=False)

    delivery_district: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_state: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_lat: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_lng: Mapped[float] = mapped_column(Float, nullable=False)

    required_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus, name="order_status"), default=OrderStatus.MATCHED, nullable=False)

    # Bumped on every status transition. Lets a client detect it's acting
    # on a stale copy of the order (optimistic-locking style safety net
    # layered on top of the pessimistic row lock used during the actual
    # transition — see services/order_state_machine.py).
    version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    match: Mapped[Optional["Match"]] = relationship(back_populates="order")
    listing: Mapped["ProduceListing"] = relationship()
    requirement: Mapped["BuyerRequirement"] = relationship()
    farmer: Mapped["Farmer"] = relationship()
    buyer: Mapped["Buyer"] = relationship()
    history: Mapped[list["OrderStatusHistory"]] = relationship(back_populates="order", order_by="OrderStatusHistory.created_at")
    delivery: Mapped[Optional["Delivery"]] = relationship(back_populates="order", uselist=False)


class OrderStatusHistory(Base):
    """Immutable audit trail — one row per status change, ever. Never
    updated or deleted, so it always reflects exactly what happened and
    when, regardless of what the Order row currently says."""

    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status: Mapped[Optional[OrderStatus]] = mapped_column(SAEnum(OrderStatus, name="order_status"), nullable=True)
    to_status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus, name="order_status"), nullable=False)
    changed_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="history")
