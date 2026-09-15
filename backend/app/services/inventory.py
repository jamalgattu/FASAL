"""
All inventory mutations go through this module, and every function here
locks the row it's about to change with SELECT ... FOR UPDATE before
reading or writing it. That's what makes "two orders reserving the last
50kg at the same time" safe: whichever transaction gets the row lock
first finishes its read-check-write as one atomic unit before the
second transaction's lock request is even granted, so the second one
always sees the already-updated quantity — it can never act on a stale
read. (On SQLite, used only for local tests, this degenerates to
SQLite's whole-database write lock, which still serializes writers and
exercises the same code path — see tests/test_inventory_concurrency.py.)
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import InsufficientInventoryError, NotFoundError
from app.models.catalog import ProduceListing, BuyerRequirement
from app.models.enums import ListingStatus, RequirementStatus


def _lock_listing(db: Session, listing_id: int) -> ProduceListing:
    listing = db.scalar(select(ProduceListing).where(ProduceListing.id == listing_id).with_for_update())
    if listing is None:
        raise NotFoundError("Produce listing not found.")
    return listing


def _lock_requirement(db: Session, requirement_id: int) -> BuyerRequirement:
    requirement = db.scalar(
        select(BuyerRequirement).where(BuyerRequirement.id == requirement_id).with_for_update()
    )
    if requirement is None:
        raise NotFoundError("Buyer requirement not found.")
    return requirement


def _refresh_listing_status(listing: ProduceListing) -> None:
    if listing.available_quantity <= 0:
        listing.status = ListingStatus.SOLD_OUT
    elif listing.quantity_reserved > 0 or listing.quantity_sold > 0:
        listing.status = ListingStatus.IN_ORDER if listing.quantity_sold > 0 else ListingStatus.MATCHED
    else:
        listing.status = ListingStatus.AVAILABLE


def _refresh_requirement_status(requirement: BuyerRequirement) -> None:
    if requirement.remaining_quantity <= 0:
        requirement.status = RequirementStatus.FULFILLED
    elif requirement.fulfilled_quantity > 0:
        requirement.status = RequirementStatus.MATCHED
    elif requirement.status not in (RequirementStatus.CLOSED,):
        requirement.status = RequirementStatus.OPEN


def reserve(db: Session, listing_id: int, requirement_id: int, quantity: float) -> None:
    """Reserve `quantity` against a listing and mark it fulfilled on the
    requirement, atomically. Raises InsufficientInventoryError rather
    than ever letting available_quantity go negative."""
    listing = _lock_listing(db, listing_id)
    requirement = _lock_requirement(db, requirement_id)

    if listing.available_quantity < quantity:
        raise InsufficientInventoryError(
            f"Only {listing.available_quantity} {listing.unit.value} available, {quantity} requested."
        )

    listing.quantity_reserved = float(listing.quantity_reserved) + quantity
    requirement.fulfilled_quantity = float(requirement.fulfilled_quantity) + quantity

    _refresh_listing_status(listing)
    _refresh_requirement_status(requirement)

    db.add(listing)
    db.add(requirement)


def release(db: Session, listing_id: int, requirement_id: int, quantity: float) -> None:
    """Release a previously reserved quantity back to available stock —
    used when an order is cancelled/rejected after reservation."""
    listing = _lock_listing(db, listing_id)
    requirement = _lock_requirement(db, requirement_id)

    listing.quantity_reserved = max(0.0, float(listing.quantity_reserved) - quantity)
    requirement.fulfilled_quantity = max(0.0, float(requirement.fulfilled_quantity) - quantity)

    _refresh_listing_status(listing)
    _refresh_requirement_status(requirement)

    db.add(listing)
    db.add(requirement)


def finalize_sale(db: Session, listing_id: int, quantity: float) -> None:
    """Convert a reservation into a completed sale — called when an order
    reaches COMPLETED. Requirement.fulfilled_quantity is left untouched
    (it was already counted at reservation time)."""
    listing = _lock_listing(db, listing_id)

    listing.quantity_reserved = max(0.0, float(listing.quantity_reserved) - quantity)
    listing.quantity_sold = float(listing.quantity_sold) + quantity

    _refresh_listing_status(listing)
    db.add(listing)
