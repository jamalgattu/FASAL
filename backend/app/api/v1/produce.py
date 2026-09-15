from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import catalog as crud_catalog
from app.crud import identity as crud_identity
from app.database import get_db
from app.models.enums import UserRole, ListingStatus
from app.models.identity import User
from app.schemas.catalog import ProduceListingCreate, ProduceListingUpdate, ProduceListingRead

router = APIRouter(prefix="/produce", tags=["produce"])


def _require_farmer_profile(db: Session, current_user: User):
    farmer = crud_identity.get_farmer_by_user_id(db, current_user.id)
    if farmer is None:
        raise NotFoundError("Farmer profile not found for this account.")
    return farmer


@router.post("/", response_model=ProduceListingRead, status_code=201)
def create_listing(
    data: ProduceListingCreate,
    current_user: User = Depends(require_role(UserRole.FARMER)),
    db: Session = Depends(get_db),
):
    farmer = _require_farmer_profile(db, current_user)
    listing = crud_catalog.create_listing(db, farmer.id, data)
    return listing


@router.get("/", response_model=list[ProduceListingRead])
def list_listings(
    farmer_id: int | None = None,
    crop_id: int | None = None,
    status: ListingStatus | None = None,
    only_available: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud_catalog.list_listings(db, farmer_id, crop_id, status, only_available, skip, limit)


@router.get("/{listing_id}", response_model=ProduceListingRead)
def read_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = crud_catalog.get_listing(db, listing_id)
    if listing is None:
        raise NotFoundError("Produce listing not found.")
    return listing


@router.patch("/{listing_id}", response_model=ProduceListingRead)
def update_listing(
    listing_id: int,
    updates: ProduceListingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    listing = crud_catalog.get_listing(db, listing_id)
    if listing is None:
        raise NotFoundError("Produce listing not found.")
    if current_user.role != UserRole.ADMIN and listing.farmer.user_id != current_user.id:
        raise ForbiddenError("You can only modify your own listings.")
    return crud_catalog.update_listing(db, listing, updates.model_dump(exclude_unset=True))
