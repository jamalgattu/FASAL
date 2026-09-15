from datetime import date
from typing import Optional

from sqlalchemy import String, Numeric, Date, ForeignKey, Enum as SAEnum, Float, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import Unit, QualityGrade, ListingStatus, RequirementStatus


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    default_unit: Mapped[Unit] = mapped_column(SAEnum(Unit, name="crop_default_unit"), default=Unit.KG)

    listings: Mapped[list["ProduceListing"]] = relationship(back_populates="crop")
    requirements: Mapped[list["BuyerRequirement"]] = relationship(back_populates="crop")


class ProduceListing(Base, TimestampMixin):
    """
    A farmer/FPO's supply offer.

    Inventory bookkeeping: `quantity` is the total ever listed.
    `quantity_reserved` is held by orders that are RESERVED-or-later but
    not yet COMPLETED. `quantity_sold` is finalized (COMPLETED) sales.
    `available_quantity` (a computed property, never stored) is what's
    left to match against new demand — it can never be negative because
    every write path that changes reserved/sold is checked first.
    """

    __tablename__ = "produce_listings"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_listing_quantity_nonneg"),
        CheckConstraint("quantity_reserved >= 0", name="ck_listing_reserved_nonneg"),
        CheckConstraint("quantity_sold >= 0", name="ck_listing_sold_nonneg"),
        CheckConstraint("quantity_reserved + quantity_sold <= quantity", name="ck_listing_no_overallocation"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), nullable=False, index=True)
    variety: Mapped[str] = mapped_column(String(255), nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    quantity_reserved: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    quantity_sold: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    unit: Mapped[Unit] = mapped_column(SAEnum(Unit, name="listing_unit"), nullable=False)

    price_per_unit: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quality_grade: Mapped[QualityGrade] = mapped_column(SAEnum(QualityGrade, name="listing_quality_grade"), nullable=False)

    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    available_date: Mapped[date] = mapped_column(Date, nullable=False)

    village: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    district: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(255), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[ListingStatus] = mapped_column(
        SAEnum(ListingStatus, name="listing_status"), default=ListingStatus.AVAILABLE, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    farmer: Mapped["Farmer"] = relationship(back_populates="listings")
    crop: Mapped["Crop"] = relationship(back_populates="listings")

    @property
    def available_quantity(self) -> float:
        return float(self.quantity) - float(self.quantity_reserved) - float(self.quantity_sold)


class BuyerRequirement(Base, TimestampMixin):
    """A buyer's demand posting. `fulfilled_quantity` accumulates as orders
    against it reach RESERVED-or-later, and can be less than
    `required_quantity` when a requirement is only partially matched."""

    __tablename__ = "buyer_requirements"
    __table_args__ = (
        CheckConstraint("required_quantity >= 0", name="ck_requirement_quantity_nonneg"),
        CheckConstraint("fulfilled_quantity >= 0", name="ck_requirement_fulfilled_nonneg"),
        CheckConstraint("fulfilled_quantity <= required_quantity", name="ck_requirement_no_overfulfillment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), nullable=False, index=True)
    variety: Mapped[str] = mapped_column(String(255), nullable=False)

    required_quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fulfilled_quantity: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    unit: Mapped[Unit] = mapped_column(SAEnum(Unit, name="requirement_unit"), nullable=False)

    acceptable_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    required_quality: Mapped[QualityGrade] = mapped_column(SAEnum(QualityGrade, name="requirement_quality_grade"), nullable=False)

    delivery_district: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_state: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_lat: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_lng: Mapped[float] = mapped_column(Float, nullable=False)

    required_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[RequirementStatus] = mapped_column(
        SAEnum(RequirementStatus, name="requirement_status"), default=RequirementStatus.OPEN, nullable=False
    )

    buyer: Mapped["Buyer"] = relationship(back_populates="requirements")
    crop: Mapped["Crop"] = relationship(back_populates="requirements")

    @property
    def remaining_quantity(self) -> float:
        return float(self.required_quantity) - float(self.fulfilled_quantity)
