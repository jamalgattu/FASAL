from typing import Optional

from sqlalchemy import Numeric, Float, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import MatchStatus


class Match(Base, TimestampMixin):
    """
    One proposed or accepted pairing between a ProduceListing and a
    BuyerRequirement, with a full breakdown of how its score was computed.
    A single requirement can have many Match rows (one per supplier) when
    the matching engine splits it across multiple suppliers.
    """

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("produce_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("buyer_requirements.id", ondelete="CASCADE"), nullable=False, index=True)

    allocated_quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    price_score: Mapped[float] = mapped_column(Float, nullable=False)
    distance_score: Mapped[float] = mapped_column(Float, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    availability_score: Mapped[float] = mapped_column(Float, nullable=False)
    reliability_score: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)

    reasons: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    explanation: Mapped[str] = mapped_column(nullable=False)

    status: Mapped[MatchStatus] = mapped_column(SAEnum(MatchStatus, name="match_status"), default=MatchStatus.PROPOSED, nullable=False)

    listing: Mapped["ProduceListing"] = relationship()
    requirement: Mapped["BuyerRequirement"] = relationship()
    order: Mapped[Optional["Order"]] = relationship(back_populates="match", uselist=False)
