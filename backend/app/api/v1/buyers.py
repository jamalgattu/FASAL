from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.exceptions import NotFoundError
from app.crud import identity as crud_identity
from app.database import get_db
from app.models.enums import UserRole
from app.models.identity import Buyer, User
from app.schemas.identity import BuyerRead, BuyerUpdate

router = APIRouter(prefix="/buyers", tags=["buyers"])


@router.get("/", response_model=list[BuyerRead])
def list_buyers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_identity.list_buyers(db, skip=skip, limit=limit)


@router.get("/me", response_model=BuyerRead)
def read_my_buyer_profile(current_user: User = Depends(require_role(UserRole.BUYER)), db: Session = Depends(get_db)):
    buyer = crud_identity.get_buyer_by_user_id(db, current_user.id)
    if buyer is None:
        raise NotFoundError("Buyer profile not found for this account.")
    return buyer


@router.patch("/me", response_model=BuyerRead)
def update_my_buyer_profile(
    updates: BuyerUpdate,
    current_user: User = Depends(require_role(UserRole.BUYER)),
    db: Session = Depends(get_db),
):
    buyer = crud_identity.get_buyer_by_user_id(db, current_user.id)
    if buyer is None:
        raise NotFoundError("Buyer profile not found for this account.")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(buyer, field, value)
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


@router.get("/{buyer_id}", response_model=BuyerRead)
def read_buyer(buyer_id: int, db: Session = Depends(get_db)):
    buyer = db.get(Buyer, buyer_id)
    if buyer is None:
        raise NotFoundError("Buyer not found.")
    return buyer
