from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.identity import User, Farmer, Buyer
from app.models.enums import UserRole


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_farmer_with_user(db: Session, data) -> Farmer:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role=UserRole.FARMER,
    )
    db.add(user)
    db.flush()  # obtain user.id without committing yet

    farmer = Farmer(
        user_id=user.id,
        is_fpo=data.is_fpo,
        org_name=data.org_name,
        village=data.village,
        district=data.district,
        state=data.state,
        lat=data.lat,
        lng=data.lng,
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


def create_buyer_with_user(db: Session, data) -> Buyer:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role=UserRole.BUYER,
    )
    db.add(user)
    db.flush()

    buyer = Buyer(
        user_id=user.id,
        buyer_type=data.buyer_type,
        org_name=data.org_name,
        district=data.district,
        state=data.state,
        lat=data.lat,
        lng=data.lng,
    )
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


def get_farmer_by_user_id(db: Session, user_id: int) -> Farmer | None:
    return db.scalar(select(Farmer).where(Farmer.user_id == user_id))


def get_buyer_by_user_id(db: Session, user_id: int) -> Buyer | None:
    return db.scalar(select(Buyer).where(Buyer.user_id == user_id))


def list_farmers(db: Session, only_fpo: bool | None = None, skip: int = 0, limit: int = 100) -> list[Farmer]:
    stmt = select(Farmer)
    if only_fpo is not None:
        stmt = stmt.where(Farmer.is_fpo == only_fpo)
    return list(db.scalars(stmt.offset(skip).limit(limit)).all())


def list_buyers(db: Session, skip: int = 0, limit: int = 100) -> list[Buyer]:
    return list(db.scalars(select(Buyer).offset(skip).limit(limit)).all())
