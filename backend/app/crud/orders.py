from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.models.matching import Match
from app.models.orders import Order
from app.models.enums import OrderStatus, MatchStatus
from app.services import order_state_machine


def create_order_from_match(db: Session, match: Match, created_by_user_id: int) -> Order:
    if match.status == MatchStatus.CONVERTED:
        raise ConflictError("This match has already been converted into an order.")

    listing = match.listing
    requirement = match.requirement

    order = Order(
        match_id=match.id,
        listing_id=listing.id,
        requirement_id=requirement.id,
        farmer_id=listing.farmer_id,
        buyer_id=requirement.buyer_id,
        crop_id=listing.crop_id,
        variety=listing.variety,
        quantity=match.allocated_quantity,
        unit=listing.unit,
        agreed_price=listing.price_per_unit,
        total_value=round(float(match.allocated_quantity) * float(listing.price_per_unit), 2),
        quality_grade=listing.quality_grade,
        pickup_district=listing.district,
        pickup_state=listing.state,
        pickup_lat=listing.lat,
        pickup_lng=listing.lng,
        delivery_district=requirement.delivery_district,
        delivery_state=requirement.delivery_state,
        delivery_lat=requirement.delivery_lat,
        delivery_lng=requirement.delivery_lng,
        required_delivery_date=requirement.required_delivery_date,
        status=OrderStatus.MATCHED,
        created_by_user_id=created_by_user_id,
    )
    db.add(order)
    match.status = MatchStatus.CONVERTED
    db.add(match)
    db.commit()
    db.refresh(order)

    order_state_machine.record_initial_status(db, order, None)
    return order


def get_order(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def list_orders_for_farmer(db: Session, farmer_id: int, skip: int = 0, limit: int = 100) -> list[Order]:
    return list(db.scalars(select(Order).where(Order.farmer_id == farmer_id).offset(skip).limit(limit)).all())


def list_orders_for_buyer(db: Session, buyer_id: int, skip: int = 0, limit: int = 100) -> list[Order]:
    return list(db.scalars(select(Order).where(Order.buyer_id == buyer_id).offset(skip).limit(limit)).all())
