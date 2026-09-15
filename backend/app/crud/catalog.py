from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import Crop, ProduceListing, BuyerRequirement
from app.models.enums import ListingStatus, RequirementStatus


def get_or_create_crop(db: Session, name: str) -> Crop:
    crop = db.scalar(select(Crop).where(Crop.name == name))
    if crop:
        return crop
    crop = Crop(name=name)
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


def list_crops(db: Session) -> list[Crop]:
    return list(db.scalars(select(Crop)).all())


# ---------------------------------------------------------------------
# ProduceListing
# ---------------------------------------------------------------------
def create_listing(db: Session, farmer_id: int, data) -> ProduceListing:
    listing = ProduceListing(farmer_id=farmer_id, **data.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def get_listing(db: Session, listing_id: int) -> ProduceListing | None:
    return db.get(ProduceListing, listing_id)


def list_listings(
    db: Session,
    farmer_id: int | None = None,
    crop_id: int | None = None,
    status: ListingStatus | None = None,
    only_available: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> list[ProduceListing]:
    stmt = select(ProduceListing)
    if farmer_id is not None:
        stmt = stmt.where(ProduceListing.farmer_id == farmer_id)
    if crop_id is not None:
        stmt = stmt.where(ProduceListing.crop_id == crop_id)
    if status is not None:
        stmt = stmt.where(ProduceListing.status == status)
    if only_available:
        stmt = stmt.where(ProduceListing.status == ListingStatus.AVAILABLE)
    return list(db.scalars(stmt.offset(skip).limit(limit)).all())


def update_listing(db: Session, listing: ProduceListing, updates: dict) -> ProduceListing:
    for field, value in updates.items():
        if value is not None:
            setattr(listing, field, value)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


# ---------------------------------------------------------------------
# BuyerRequirement
# ---------------------------------------------------------------------
def create_requirement(db: Session, buyer_id: int, data) -> BuyerRequirement:
    requirement = BuyerRequirement(buyer_id=buyer_id, **data.model_dump())
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement


def get_requirement(db: Session, requirement_id: int) -> BuyerRequirement | None:
    return db.get(BuyerRequirement, requirement_id)


def list_requirements(
    db: Session,
    buyer_id: int | None = None,
    crop_id: int | None = None,
    status: RequirementStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[BuyerRequirement]:
    stmt = select(BuyerRequirement)
    if buyer_id is not None:
        stmt = stmt.where(BuyerRequirement.buyer_id == buyer_id)
    if crop_id is not None:
        stmt = stmt.where(BuyerRequirement.crop_id == crop_id)
    if status is not None:
        stmt = stmt.where(BuyerRequirement.status == status)
    return list(db.scalars(stmt.offset(skip).limit(limit)).all())


def update_requirement(db: Session, requirement: BuyerRequirement, updates: dict) -> BuyerRequirement:
    for field, value in updates.items():
        if value is not None:
            setattr(requirement, field, value)
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement
