from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import ForbiddenError, ConflictError
from app.core.security import create_access_token, verify_password
from app.crud.identity import create_farmer_with_user, create_buyer_with_user, get_user_by_email
from app.database import get_db
from app.models.identity import User
from app.schemas.auth import FarmerRegisterRequest, BuyerRegisterRequest, Token, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/farmer", response_model=Token, status_code=201)
def register_farmer(data: FarmerRegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise ConflictError("An account with this email already exists.")
    farmer = create_farmer_with_user(db, data)
    token = create_access_token(subject=str(farmer.user_id))
    return Token(access_token=token, user=UserRead.model_validate(farmer.user))


@router.post("/register/buyer", response_model=Token, status_code=201)
def register_buyer(data: BuyerRegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise ConflictError("An account with this email already exists.")
    buyer = create_buyer_with_user(db, data)
    token = create_access_token(subject=str(buyer.user_id))
    return Token(access_token=token, user=UserRead.model_validate(buyer.user))


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise ForbiddenError("Incorrect email or password.")
    if not user.is_active:
        raise ForbiddenError("This account has been deactivated.")
    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
