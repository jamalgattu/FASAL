from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.crud import catalog as crud_catalog
from app.crud import matching as crud_matching
from app.database import get_db
from app.models.enums import UserRole, MatchStatus
from app.models.identity import User
from app.schemas.matching import (
    MatchWeights as MatchWeightsSchema,
    MatchAllocationResponse,
    MatchAllocationRead,
    MatchFactorScores,
    MatchReasonSchema,
    MatchRead,
)
from app.services import matching_engine

router = APIRouter(prefix="/matches", tags=["matches"])


def _to_allocation_read(allocation) -> MatchAllocationRead:
    return MatchAllocationRead(
        listing_id=allocation.listing.id,
        farmer_id=allocation.listing.farmer_id,
        farmer_name=allocation.listing.farmer.org_name or allocation.listing.farmer.user.full_name,
        allocated_quantity=allocation.allocated_quantity,
        match_score=allocation.match_score,
        distance_km=allocation.distance_km,
        factors=MatchFactorScores(
            price_score=allocation.factors.price_score,
            distance_score=allocation.factors.distance_score,
            quality_score=allocation.factors.quality_score,
            availability_score=allocation.factors.availability_score,
            reliability_score=allocation.factors.reliability_score,
        ),
        reasons=[MatchReasonSchema(label=r.label, satisfied=r.satisfied) for r in allocation.reasons],
        explanation=allocation.explanation,
    )


def _require_requirement_access(db: Session, requirement_id: int, current_user: User):
    requirement = crud_catalog.get_requirement(db, requirement_id)
    if requirement is None:
        raise NotFoundError("Buyer requirement not found.")
    if current_user.role != UserRole.ADMIN and requirement.buyer.user_id != current_user.id:
        raise ForbiddenError("You can only run matching for your own requirements.")
    return requirement


@router.get("/preview/{requirement_id}", response_model=MatchAllocationResponse)
def preview_matches(
    requirement_id: int,
    weight_price: float | None = None,
    weight_distance: float | None = None,
    weight_quality: float | None = None,
    weight_availability: float | None = None,
    weight_reliability: float | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Read-only: runs the matching engine and returns a proposed
    allocation without writing anything to the database."""
    requirement = _require_requirement_access(db, requirement_id, current_user)

    weights = None
    if any(w is not None for w in (weight_price, weight_distance, weight_quality, weight_availability, weight_reliability)):
        defaults = MatchWeightsSchema()
        weights = matching_engine.MatchWeights(
            price=weight_price if weight_price is not None else defaults.price,
            distance=weight_distance if weight_distance is not None else defaults.distance,
            quality=weight_quality if weight_quality is not None else defaults.quality,
            availability=weight_availability if weight_availability is not None else defaults.availability,
            reliability=weight_reliability if weight_reliability is not None else defaults.reliability,
        )

    result = matching_engine.allocate_supply(db, requirement, weights=weights)
    return MatchAllocationResponse(
        requirement_id=result.requirement_id,
        requirement_remaining_quantity=result.requirement_remaining_quantity,
        fully_allocated=result.fully_allocated,
        allocations=[_to_allocation_read(a) for a in result.allocations],
    )


@router.post("/generate/{requirement_id}", response_model=list[MatchRead], status_code=201)
def generate_and_persist_matches(
    requirement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Runs the matching engine and persists each allocation as a
    PROPOSED Match row, ready to be accepted and turned into Orders."""
    requirement = _require_requirement_access(db, requirement_id, current_user)
    result = matching_engine.allocate_supply(db, requirement)
    return [crud_matching.persist_allocation(db, requirement_id, a) for a in result.allocations]


@router.get("/", response_model=list[MatchRead])
def list_matches(
    requirement_id: int | None = None,
    listing_id: int | None = None,
    db: Session = Depends(get_db),
):
    if requirement_id is not None:
        return crud_matching.list_matches_for_requirement(db, requirement_id)
    if listing_id is not None:
        return crud_matching.list_matches_for_listing(db, listing_id)
    raise ConflictError("Provide requirement_id or listing_id to list matches.")


@router.get("/{match_id}", response_model=MatchRead)
def read_match(match_id: int, db: Session = Depends(get_db)):
    match = crud_matching.get_match(db, match_id)
    if match is None:
        raise NotFoundError("Match not found.")
    return match


def _check_match_party(match, current_user: User):
    if current_user.role == UserRole.ADMIN:
        return
    is_farmer_party = match.listing.farmer.user_id == current_user.id
    is_buyer_party = match.requirement.buyer.user_id == current_user.id
    if not (is_farmer_party or is_buyer_party):
        raise ForbiddenError("You are not a party to this match.")


@router.post("/{match_id}/accept", response_model=MatchRead)
def accept_match(match_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    match = crud_matching.get_match(db, match_id)
    if match is None:
        raise NotFoundError("Match not found.")
    _check_match_party(match, current_user)
    if match.status != MatchStatus.PROPOSED:
        raise ConflictError(f"Match is already {match.status.value}.")
    match.status = MatchStatus.ACCEPTED
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.post("/{match_id}/reject", response_model=MatchRead)
def reject_match(match_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    match = crud_matching.get_match(db, match_id)
    if match is None:
        raise NotFoundError("Match not found.")
    _check_match_party(match, current_user)
    if match.status != MatchStatus.PROPOSED:
        raise ConflictError(f"Match is already {match.status.value}.")
    match.status = MatchStatus.REJECTED
    db.add(match)
    db.commit()
    db.refresh(match)
    return match
