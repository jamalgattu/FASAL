"""
Tests run against a throwaway file-based SQLite database (not
Postgres), since that's what's available in most CI / sandbox
environments without extra setup. The service-layer code under test
(inventory reservation, order transitions, matching) uses only
standard SQLAlchemy Core operations — `with_for_update()`,
transactions, constraints — that SQLite also supports, so the same
code path is exercised. See test_inventory_concurrency.py for a note
on what does and doesn't carry over to Postgres's finer-grained
row-level locking.
"""
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
import app.models  # noqa: F401 — registers all models
from app.models.identity import User, Farmer, Buyer
from app.models.catalog import Crop, ProduceListing, BuyerRequirement
from app.models.enums import UserRole, BuyerType, Unit, QualityGrade


@pytest.fixture()
def engine(tmp_path):
    db_path = tmp_path / f"test_{uuid.uuid4().hex}.db"
    eng = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False, "timeout": 30})
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def SessionFactory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db_session(SessionFactory):
    session = SessionFactory()
    yield session
    session.close()


# ---------------------------------------------------------------------
# Entity factories — created directly via the ORM so tests can focus on
# the service logic rather than the HTTP/auth layer.
# ---------------------------------------------------------------------
def make_user(db, role=UserRole.FARMER, email=None) -> User:
    user = User(
        email=email or f"{uuid.uuid4().hex}@example.com",
        hashed_password="not-a-real-hash",
        full_name="Test User",
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_farmer(db, is_fpo=True, lat=27.71, lng=80.78) -> Farmer:
    user = make_user(db, role=UserRole.FARMER)
    farmer = Farmer(
        user_id=user.id, is_fpo=is_fpo, org_name="Test FPO", district="Sitapur", state="Uttar Pradesh", lat=lat, lng=lng
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


def make_buyer(db, lat=26.85, lng=80.95) -> Buyer:
    user = make_user(db, role=UserRole.BUYER)
    buyer = Buyer(
        user_id=user.id,
        buyer_type=BuyerType.RETAIL_CHAIN,
        org_name="Test Buyer Co",
        district="Lucknow",
        state="Uttar Pradesh",
        lat=lat,
        lng=lng,
    )
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


def make_crop(db, name="Potato") -> Crop:
    crop = Crop(name=f"{name}-{uuid.uuid4().hex[:6]}")
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


def make_listing(
    db,
    farmer,
    crop,
    quantity=1000,
    price=15,
    grade=QualityGrade.A,
    lat=None,
    lng=None,
    available_in_days=1,
) -> ProduceListing:
    listing = ProduceListing(
        farmer_id=farmer.id,
        crop_id=crop.id,
        variety="Test Variety",
        quantity=quantity,
        unit=Unit.KG,
        price_per_unit=price,
        quality_grade=grade,
        harvest_date=date.today() - timedelta(days=5),
        available_date=date.today() + timedelta(days=available_in_days),
        district="Sitapur",
        state="Uttar Pradesh",
        lat=lat if lat is not None else farmer.lat,
        lng=lng if lng is not None else farmer.lng,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def make_requirement(
    db,
    buyer,
    crop,
    quantity=2000,
    acceptable_price=20,
    required_grade=QualityGrade.B,
    required_in_days=10,
) -> BuyerRequirement:
    requirement = BuyerRequirement(
        buyer_id=buyer.id,
        crop_id=crop.id,
        variety="Any",
        required_quantity=quantity,
        unit=Unit.KG,
        acceptable_price=acceptable_price,
        required_quality=required_grade,
        delivery_district=buyer.district,
        delivery_state=buyer.state,
        delivery_lat=buyer.lat,
        delivery_lng=buyer.lng,
        required_delivery_date=date.today() + timedelta(days=required_in_days),
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement
