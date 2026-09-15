from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import identity as crud_identity
from app.database import get_db
from app.models.enums import UserRole
from app.models.identity import Farmer, User
from app.schemas.identity import FarmerRead, FarmerUpdate

router = APIRouter(prefix="/farmers", tags=["farmers"])


def _to_read(farmer: Farmer) -> FarmerRead:
    read = FarmerRead.model_validate(farmer)
    read.full_name = farmer.user.full_name
    return read


@router.get("/", response_model=list[FarmerRead])
def list_farmers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    farmers = crud_identity.list_farmers(db, only_fpo=None, skip=skip, limit=limit)
    return [_to_read(f) for f in farmers]


@router.get("/me", response_model=FarmerRead)
def read_my_farmer_profile(current_user: User = Depends(require_role(UserRole.FARMER)), db: Session = Depends(get_db)):
    farmer = crud_identity.get_farmer_by_user_id(db, current_user.id)
    if farmer is None:
        raise NotFoundError("Farmer profile not found for this account.")
    return _to_read(farmer)


@router.patch("/me", response_model=FarmerRead)
def update_my_farmer_profile(
    updates: FarmerUpdate,
    current_user: User = Depends(require_role(UserRole.FARMER)),
    db: Session = Depends(get_db),
):
    farmer = crud_identity.get_farmer_by_user_id(db, current_user.id)
    if farmer is None:
        raise NotFoundError("Farmer profile not found for this account.")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(farmer, field, value)
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return _to_read(farmer)


@router.get("/{farmer_id}", response_model=FarmerRead)
def read_farmer(farmer_id: int, db: Session = Depends(get_db)):
    farmer = db.get(Farmer, farmer_id)
    if farmer is None:
        raise NotFoundError("Farmer not found.")
    return _to_read(farmer)
