from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import catalog as crud_catalog
from app.crud import identity as crud_identity
from app.database import get_db
from app.models.enums import UserRole, RequirementStatus
from app.models.identity import User
from app.schemas.catalog import BuyerRequirementCreate, BuyerRequirementUpdate, BuyerRequirementRead

router = APIRouter(prefix="/requirements", tags=["requirements"])


def _require_buyer_profile(db: Session, current_user: User):
    buyer = crud_identity.get_buyer_by_user_id(db, current_user.id)
    if buyer is None:
        raise NotFoundError("Buyer profile not found for this account.")
    return buyer


@router.post("/", response_model=BuyerRequirementRead, status_code=201)
def create_requirement(
    data: BuyerRequirementCreate,
    current_user: User = Depends(require_role(UserRole.BUYER)),
    db: Session = Depends(get_db),
):
    buyer = _require_buyer_profile(db, current_user)
    return crud_catalog.create_requirement(db, buyer.id, data)


@router.get("/", response_model=list[BuyerRequirementRead])
def list_requirements(
    buyer_id: int | None = None,
    crop_id: int | None = None,
    status: RequirementStatus | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud_catalog.list_requirements(db, buyer_id, crop_id, status, skip, limit)


@router.get("/{requirement_id}", response_model=BuyerRequirementRead)
def read_requirement(requirement_id: int, db: Session = Depends(get_db)):
    requirement = crud_catalog.get_requirement(db, requirement_id)
    if requirement is None:
        raise NotFoundError("Buyer requirement not found.")
    return requirement


@router.patch("/{requirement_id}", response_model=BuyerRequirementRead)
def update_requirement(
    requirement_id: int,
    updates: BuyerRequirementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    requirement = crud_catalog.get_requirement(db, requirement_id)
    if requirement is None:
        raise NotFoundError("Buyer requirement not found.")
    if current_user.role != UserRole.ADMIN and requirement.buyer.user_id != current_user.id:
        raise ForbiddenError("You can only modify your own requirements.")
    return crud_catalog.update_requirement(db, requirement, updates.model_dump(exclude_unset=True))
