from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.matching import Match
from app.models.enums import MatchStatus
from app.services.matching_engine import Allocation


def persist_allocation(db: Session, requirement_id: int, allocation: Allocation) -> Match:
    match = Match(
        listing_id=allocation.listing.id,
        requirement_id=requirement_id,
        allocated_quantity=allocation.allocated_quantity,
        match_score=allocation.match_score,
        price_score=allocation.factors.price_score,
        distance_score=allocation.factors.distance_score,
        quality_score=allocation.factors.quality_score,
        availability_score=allocation.factors.availability_score,
        reliability_score=allocation.factors.reliability_score,
        distance_km=allocation.distance_km,
        reasons=[{"label": r.label, "satisfied": r.satisfied} for r in allocation.reasons],
        explanation=allocation.explanation,
        status=MatchStatus.PROPOSED,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def get_match(db: Session, match_id: int) -> Match | None:
    return db.get(Match, match_id)


def list_matches_for_requirement(db: Session, requirement_id: int) -> list[Match]:
    return list(db.scalars(select(Match).where(Match.requirement_id == requirement_id)).all())


def list_matches_for_listing(db: Session, listing_id: int) -> list[Match]:
    return list(db.scalars(select(Match).where(Match.listing_id == listing_id)).all())
