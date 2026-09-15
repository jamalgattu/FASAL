"""
Supply-demand matching engine.

Given a BuyerRequirement and a pool of candidate ProduceListings, this
module scores each candidate on five weighted factors, then greedily
allocates the requirement's remaining quantity across the
highest-scoring candidates — splitting across multiple suppliers when
one alone can't cover the full quantity.

Deliberately NOT "pick the cheapest": price is one of five weighted
factors, so a slightly pricier but much closer, higher-quality, and
more reliable supplier can out-rank a cheap-but-far one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from math import asin, cos, radians, sin, sqrt

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.catalog import BuyerRequirement, ProduceListing
from app.models.enums import QUALITY_RANK, OrderStatus
from app.models.orders import Order


# ---------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------
@dataclass
class MatchWeights:
    price: float = settings.MATCH_WEIGHT_PRICE
    distance: float = settings.MATCH_WEIGHT_DISTANCE
    quality: float = settings.MATCH_WEIGHT_QUALITY
    availability: float = settings.MATCH_WEIGHT_AVAILABILITY
    reliability: float = settings.MATCH_WEIGHT_RELIABILITY

    def normalized(self) -> "MatchWeights":
        total = self.price + self.distance + self.quality + self.availability + self.reliability
        if total <= 0:
            raise ValueError("At least one match weight must be greater than zero")
        if abs(total - 1.0) < 1e-9:
            return self
        return MatchWeights(
            price=self.price / total,
            distance=self.distance / total,
            quality=self.quality / total,
            availability=self.availability / total,
            reliability=self.reliability / total,
        )


# ---------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------
@dataclass
class FactorScores:
    price_score: float
    distance_score: float
    quality_score: float
    availability_score: float
    reliability_score: float


@dataclass
class MatchReason:
    label: str
    satisfied: bool


@dataclass
class MatchCandidate:
    listing: ProduceListing
    distance_km: float
    factors: FactorScores
    match_score: float  # 0-100
    reasons: list[MatchReason]
    explanation: str
    allocatable_quantity: float  # min(listing available, requirement remaining) at scoring time


@dataclass
class Allocation:
    listing: ProduceListing
    allocated_quantity: float
    match_score: float
    distance_km: float
    factors: FactorScores
    reasons: list[MatchReason]
    explanation: str


@dataclass
class AllocationResult:
    requirement_id: int
    requirement_remaining_quantity: float
    fully_allocated: bool
    allocations: list[Allocation] = field(default_factory=list)


# ---------------------------------------------------------------------
# Geo helper
# ---------------------------------------------------------------------
def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two lat/lng points, in kilometers."""
    r = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lng2 - lng1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    return 2 * r * asin(sqrt(a))


# ---------------------------------------------------------------------
# Individual factor scoring — each returns a 0.0-1.0 score, or None if
# the candidate fails a hard requirement (crop, quality floor, or can't
# be available in time) and should be excluded entirely.
# ---------------------------------------------------------------------
def score_price(listing_price: float, acceptable_price: float) -> float:
    if acceptable_price <= 0:
        return 0.0
    if listing_price <= acceptable_price:
        return 1.0
    overage_ratio = (listing_price - acceptable_price) / acceptable_price
    return max(0.0, 1.0 - overage_ratio)


def score_distance(distance_km: float, max_distance_km: float) -> float:
    if max_distance_km <= 0:
        return 0.0
    return max(0.0, 1.0 - (distance_km / max_distance_km))


def score_quality(listing_grade, required_grade) -> float | None:
    listing_rank = QUALITY_RANK[listing_grade]
    required_rank = QUALITY_RANK[required_grade]
    if listing_rank < required_rank:
        return None  # hard fail — doesn't meet the minimum quality bar
    gap = listing_rank - required_rank
    return {0: 1.0, 1: 0.9, 2: 0.8}.get(gap, 0.8)


def score_availability(available_date: date, required_delivery_date: date) -> float | None:
    if available_date > required_delivery_date:
        return None  # hard fail — can't be ready in time
    buffer_days = (required_delivery_date - available_date).days
    if buffer_days >= 2:
        return 1.0
    return 0.9


def score_reliability(db: Session, farmer_id: int) -> float:
    """Ratio of completed orders to (completed + cancelled + disputed) for
    this farmer. Defaults to a neutral 0.75 when there's no order history
    yet, per the "if available" clause in the spec."""
    rows = db.scalars(select(Order.status).where(Order.farmer_id == farmer_id)).all()
    completed = sum(1 for s in rows if s == OrderStatus.COMPLETED)
    negative = sum(1 for s in rows if s in (OrderStatus.CANCELLED, OrderStatus.DISPUTED))
    total = completed + negative
    if total == 0:
        return 0.75
    return completed / total


# ---------------------------------------------------------------------
# Candidate scoring
# ---------------------------------------------------------------------
def score_candidate(
    db: Session,
    listing: ProduceListing,
    requirement: BuyerRequirement,
    weights: MatchWeights,
    max_distance_km: float,
) -> MatchCandidate | None:
    if listing.crop_id != requirement.crop_id:
        return None
    if listing.available_quantity <= 0:
        return None

    quality = score_quality(listing.quality_grade, requirement.required_quality)
    if quality is None:
        return None

    availability = score_availability(listing.available_date, requirement.required_delivery_date)
    if availability is None:
        return None

    distance_km = haversine_km(listing.lat, listing.lng, requirement.delivery_lat, requirement.delivery_lng)
    distance = score_distance(distance_km, max_distance_km)
    price = score_price(float(listing.price_per_unit), float(requirement.acceptable_price))
    reliability = score_reliability(db, listing.farmer_id)

    w = weights.normalized()
    overall = (
        w.price * price
        + w.distance * distance
        + w.quality * quality
        + w.availability * availability
        + w.reliability * reliability
    )
    match_score = round(overall * 100, 1)

    reasons = [
        MatchReason("Quantity available", listing.available_quantity > 0),
        MatchReason("Quality compatible", quality >= 0.9),
        MatchReason("Price within budget", price >= 0.9),
        MatchReason("Short distance", distance_km <= max_distance_km * 0.3),
        MatchReason("Available within required date", True),
    ]

    factors = FactorScores(
        price_score=round(price, 3),
        distance_score=round(distance, 3),
        quality_score=round(quality, 3),
        availability_score=round(availability, 3),
        reliability_score=round(reliability, 3),
    )

    explanation = _build_explanation(factors, distance_km, listing, requirement)

    return MatchCandidate(
        listing=listing,
        distance_km=round(distance_km, 1),
        factors=factors,
        match_score=match_score,
        reasons=reasons,
        explanation=explanation,
        allocatable_quantity=min(listing.available_quantity, requirement.remaining_quantity),
    )


def _build_explanation(factors: FactorScores, distance_km: float, listing: ProduceListing, requirement: BuyerRequirement) -> str:
    parts = []
    if factors.price_score >= 0.95:
        parts.append("priced at or below your target")
    elif factors.price_score >= 0.7:
        parts.append("priced close to your target")
    else:
        parts.append("priced above your target")

    parts.append(f"{round(distance_km)} km from the delivery location")

    if factors.quality_score >= 1.0:
        parts.append(f"exactly Grade {requirement.required_quality.value} as required")
    else:
        parts.append(f"exceeds the required Grade {requirement.required_quality.value}")

    if factors.availability_score >= 1.0:
        parts.append("comfortably available before your required date")
    else:
        parts.append("available just in time for your required date")

    if factors.reliability_score >= 0.85:
        parts.append("a highly reliable supplier based on order history")
    elif factors.reliability_score < 0.6:
        parts.append("a supplier with limited or mixed order history")

    return "This supplier is " + ", ".join(parts) + "."


# ---------------------------------------------------------------------
# Allocation across (possibly) multiple suppliers
# ---------------------------------------------------------------------
def find_candidates(
    db: Session,
    requirement: BuyerRequirement,
    weights: MatchWeights | None = None,
    max_distance_km: float | None = None,
    listings: list[ProduceListing] | None = None,
) -> list[MatchCandidate]:
    weights = weights or MatchWeights()
    max_distance_km = max_distance_km or settings.MATCH_MAX_DISTANCE_KM

    if listings is None:
        listings = list(
            db.scalars(
                select(ProduceListing).where(ProduceListing.crop_id == requirement.crop_id)
            ).all()
        )

    candidates = []
    for listing in listings:
        candidate = score_candidate(db, listing, requirement, weights, max_distance_km)
        if candidate is not None:
            candidates.append(candidate)

    candidates.sort(key=lambda c: c.match_score, reverse=True)
    return candidates


def allocate_supply(
    db: Session,
    requirement: BuyerRequirement,
    weights: MatchWeights | None = None,
    max_distance_km: float | None = None,
    listings: list[ProduceListing] | None = None,
) -> AllocationResult:
    """
    Greedily allocate `requirement.remaining_quantity` across the
    highest-scoring candidates first, splitting across as many suppliers
    as necessary to fulfil the requirement (or until candidates run out).
    """
    candidates = find_candidates(db, requirement, weights, max_distance_km, listings)

    remaining = requirement.remaining_quantity
    allocations: list[Allocation] = []

    for candidate in candidates:
        if remaining <= 0:
            break
        take = min(candidate.allocatable_quantity, remaining)
        if take <= 0:
            continue
        allocations.append(
            Allocation(
                listing=candidate.listing,
                allocated_quantity=round(take, 2),
                match_score=candidate.match_score,
                distance_km=candidate.distance_km,
                factors=candidate.factors,
                reasons=candidate.reasons,
                explanation=candidate.explanation,
            )
        )
        remaining -= take

    return AllocationResult(
        requirement_id=requirement.id,
        requirement_remaining_quantity=round(max(remaining, 0), 2),
        fully_allocated=remaining <= 1e-6,
        allocations=allocations,
    )
