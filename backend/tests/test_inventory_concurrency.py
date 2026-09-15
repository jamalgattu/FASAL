"""
Concurrency tests for the inventory reservation path.

These run several threads against the SAME SQLite database file
simultaneously, each trying to reserve stock that only some of them
can actually get. The engine is opened with isolation_level="IMMEDIATE",
which makes SQLite acquire its write lock at the START of every
transaction (not lazily on the first write) — this is the closest
SQLite equivalent to Postgres's `SELECT ... FOR UPDATE` row lock, and
it's what makes it safe to reuse `services/inventory.py` unmodified
here: the same "lock, re-read, check, write" code path in
inventory.reserve() is what's under test, just serialized more coarsely
(whole-database lock vs. Postgres's per-row lock).

The property under test is the one the spec calls out explicitly:
however many threads race for the same limited stock, the total
reserved can never exceed what was available, and no reservation is
silently lost or double-counted.
"""
import threading
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import InsufficientInventoryError
from app.crud import orders as crud_orders
from app.models.base import Base
import app.models  # noqa: F401
from app.models.enums import UserRole, BuyerType, Unit, QualityGrade, OrderStatus, MatchStatus
from app.models.identity import User, Farmer, Buyer
from app.models.catalog import ProduceListing, BuyerRequirement
from app.models.matching import Match
from app.services import order_state_machine


@pytest.fixture()
def concurrency_engine(tmp_path):
    db_path = tmp_path / f"concurrency_{uuid.uuid4().hex}.db"
    eng = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False, "timeout": 30},
        isolation_level="IMMEDIATE",
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def ConcurrentSessionFactory(concurrency_engine):
    return sessionmaker(bind=concurrency_engine, autoflush=False, autocommit=False)


def _seed_listing_and_orders(SessionFactory, listing_quantity: float, order_quantity: float, n_orders: int):
    """Creates one listing with `listing_quantity` stock, and `n_orders`
    separate orders (each wanting `order_quantity`) all sitting in
    ACCEPTED status, ready to race for RESERVED."""
    db = SessionFactory()

    from app.models.catalog import Crop

    user_f = User(email=f"f{uuid.uuid4().hex}@x.com", hashed_password="x", full_name="F", role=UserRole.FARMER)
    db.add(user_f)
    db.flush()
    farmer = Farmer(user_id=user_f.id, is_fpo=True, district="Sitapur", state="UP", lat=27.71, lng=80.78)
    db.add(farmer)

    user_b = User(email=f"b{uuid.uuid4().hex}@x.com", hashed_password="x", full_name="B", role=UserRole.BUYER)
    db.add(user_b)
    db.flush()
    buyer = Buyer(user_id=user_b.id, buyer_type=BuyerType.RETAIL_CHAIN, org_name="B", district="Lucknow", state="UP", lat=26.85, lng=80.95)
    db.add(buyer)

    crop = Crop(name=f"crop-{uuid.uuid4().hex[:6]}")
    db.add(crop)
    db.commit()

    listing = ProduceListing(
        farmer_id=farmer.id,
        crop_id=crop.id,
        variety="Test",
        quantity=listing_quantity,
        unit=Unit.KG,
        price_per_unit=15,
        quality_grade=QualityGrade.A,
        harvest_date=date.today() - timedelta(days=5),
        available_date=date.today(),
        district="Sitapur",
        state="UP",
        lat=27.71,
        lng=80.78,
    )
    db.add(listing)

    requirement = BuyerRequirement(
        buyer_id=buyer.id,
        crop_id=crop.id,
        variety="Any",
        required_quantity=listing_quantity * 10,  # plenty of headroom
        unit=Unit.KG,
        acceptable_price=20,
        required_quality=QualityGrade.B,
        delivery_district="Lucknow",
        delivery_state="UP",
        delivery_lat=26.85,
        delivery_lng=80.95,
        required_delivery_date=date.today() + timedelta(days=10),
    )
    db.add(requirement)
    db.commit()

    order_ids = []
    for _ in range(n_orders):
        match = Match(
            listing_id=listing.id,
            requirement_id=requirement.id,
            allocated_quantity=order_quantity,
            match_score=90.0,
            price_score=1.0,
            distance_score=1.0,
            quality_score=1.0,
            availability_score=1.0,
            reliability_score=0.75,
            distance_km=10.0,
            reasons=[],
            explanation="test",
            status=MatchStatus.ACCEPTED,
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        order = crud_orders.create_order_from_match(db, match, created_by_user_id=user_b.id)
        order_state_machine.transition_order(db, order.id, OrderStatus.ACCEPTED, current_user=None)
        order_ids.append(order.id)

    listing_id = listing.id
    requirement_id = requirement.id
    db.close()
    return listing_id, requirement_id, order_ids


def test_concurrent_reservations_never_exceed_available_stock(ConcurrentSessionFactory):
    # 100kg available, 10 orders each wanting 20kg => only 5 can succeed.
    listing_id, requirement_id, order_ids = _seed_listing_and_orders(
        ConcurrentSessionFactory, listing_quantity=100, order_quantity=20, n_orders=10
    )

    results = {"success": 0, "failed": 0}
    lock = threading.Lock()

    def worker(order_id):
        db = ConcurrentSessionFactory()
        try:
            order_state_machine.transition_order(db, order_id, OrderStatus.RESERVED, current_user=None)
            with lock:
                results["success"] += 1
        except InsufficientInventoryError:
            with lock:
                results["failed"] += 1
        finally:
            db.close()

    threads = [threading.Thread(target=worker, args=(oid,)) for oid in order_ids]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results["success"] == 5
    assert results["failed"] == 5

    verify_db = ConcurrentSessionFactory()
    listing = verify_db.get(ProduceListing, listing_id)
    requirement = verify_db.get(BuyerRequirement, requirement_id)

    # The critical invariant: reserved stock exactly matches what
    # succeeded — never more than what was available, never silently lost.
    assert float(listing.quantity_reserved) == 100
    assert listing.available_quantity == 0
    assert float(requirement.fulfilled_quantity) == 100
    verify_db.close()


def test_concurrent_reservations_exactly_filling_stock_all_succeed(ConcurrentSessionFactory):
    # 100kg available, 5 orders of 20kg each => exactly fits, all should succeed.
    listing_id, requirement_id, order_ids = _seed_listing_and_orders(
        ConcurrentSessionFactory, listing_quantity=100, order_quantity=20, n_orders=5
    )

    results = {"success": 0, "failed": 0}
    lock = threading.Lock()

    def worker(order_id):
        db = ConcurrentSessionFactory()
        try:
            order_state_machine.transition_order(db, order_id, OrderStatus.RESERVED, current_user=None)
            with lock:
                results["success"] += 1
        except InsufficientInventoryError:
            with lock:
                results["failed"] += 1
        finally:
            db.close()

    threads = [threading.Thread(target=worker, args=(oid,)) for oid in order_ids]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results["success"] == 5
    assert results["failed"] == 0

    verify_db = ConcurrentSessionFactory()
    listing = verify_db.get(ProduceListing, listing_id)
    assert listing.available_quantity == 0
    assert float(listing.quantity_reserved) == 100
    verify_db.close()


def test_reservation_never_drives_available_quantity_negative(ConcurrentSessionFactory):
    """A single over-large request must be rejected outright, never
    partially applied."""
    listing_id, requirement_id, order_ids = _seed_listing_and_orders(
        ConcurrentSessionFactory, listing_quantity=50, order_quantity=999, n_orders=1
    )

    db = ConcurrentSessionFactory()
    with pytest.raises(InsufficientInventoryError):
        order_state_machine.transition_order(db, order_ids[0], OrderStatus.RESERVED, current_user=None)
    db.close()

    verify_db = ConcurrentSessionFactory()
    listing = verify_db.get(ProduceListing, listing_id)
    assert float(listing.quantity_reserved) == 0
    assert listing.available_quantity == 50
    verify_db.close()
