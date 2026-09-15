import pytest

from app.core.exceptions import InvalidStateTransitionError, ForbiddenError, DuplicateOperationError
from app.crud import orders as crud_orders
from app.models.enums import OrderStatus, MatchStatus, ListingStatus, RequirementStatus
from app.models.matching import Match
from app.models.orders import OrderStatusHistory
from app.services import order_state_machine
from tests.conftest import make_farmer, make_buyer, make_crop, make_listing, make_requirement


def _create_order(db, quantity=500, listing_quantity=1000, requirement_quantity=2000):
    farmer = make_farmer(db)
    buyer = make_buyer(db)
    crop = make_crop(db)
    listing = make_listing(db, farmer, crop, quantity=listing_quantity, price=15)
    requirement = make_requirement(db, buyer, crop, quantity=requirement_quantity, acceptable_price=20)

    match = Match(
        listing_id=listing.id,
        requirement_id=requirement.id,
        allocated_quantity=quantity,
        match_score=90.0,
        price_score=1.0,
        distance_score=1.0,
        quality_score=1.0,
        availability_score=1.0,
        reliability_score=0.75,
        distance_km=10.0,
        reasons=[],
        explanation="test match",
        status=MatchStatus.ACCEPTED,
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    order = crud_orders.create_order_from_match(db, match, created_by_user_id=buyer.user_id)
    return order, farmer, buyer, listing, requirement


def test_order_starts_in_matched_status_with_initial_history(db_session):
    order, *_ = _create_order(db_session)
    assert order.status == OrderStatus.MATCHED

    history = db_session.query(OrderStatusHistory).filter_by(order_id=order.id).all()
    assert len(history) == 1
    assert history[0].from_status is None
    assert history[0].to_status == OrderStatus.MATCHED


def test_happy_path_transitions_through_full_lifecycle(db_session):
    order, farmer, buyer, listing, requirement = _create_order(db_session, quantity=500, listing_quantity=1000)

    happy_path = [
        OrderStatus.ACCEPTED,
        OrderStatus.RESERVED,
        OrderStatus.CONFIRMED,
        OrderStatus.PICKUP_ASSIGNED,
        OrderStatus.PICKED_UP,
        OrderStatus.IN_TRANSIT,
        OrderStatus.DELIVERED,
        OrderStatus.COMPLETED,
    ]

    for next_status in happy_path:
        order = order_state_machine.transition_order(db_session, order.id, next_status, current_user=None)
        assert order.status == next_status

    db_session.refresh(listing)
    db_session.refresh(requirement)

    # Inventory finalized: 500kg moved from reserved to sold, none left reserved.
    assert float(listing.quantity_reserved) == 0
    assert float(listing.quantity_sold) == 500
    assert float(requirement.fulfilled_quantity) == 500

    history = (
        db_session.query(OrderStatusHistory)
        .filter_by(order_id=order.id)
        .order_by(OrderStatusHistory.created_at)
        .all()
    )
    # initial MATCHED row + 8 transitions
    assert len(history) == 9


def test_reservation_reduces_available_quantity(db_session):
    order, farmer, buyer, listing, requirement = _create_order(db_session, quantity=400, listing_quantity=1000)

    assert listing.available_quantity == 1000
    order_state_machine.transition_order(db_session, order.id, OrderStatus.ACCEPTED, current_user=None)
    order_state_machine.transition_order(db_session, order.id, OrderStatus.RESERVED, current_user=None)

    db_session.refresh(listing)
    assert float(listing.quantity_reserved) == 400
    assert listing.available_quantity == 600
    assert listing.status == ListingStatus.MATCHED


def test_cancelling_after_reservation_releases_inventory(db_session):
    order, farmer, buyer, listing, requirement = _create_order(db_session, quantity=400, listing_quantity=1000)

    order_state_machine.transition_order(db_session, order.id, OrderStatus.ACCEPTED, current_user=None)
    order_state_machine.transition_order(db_session, order.id, OrderStatus.RESERVED, current_user=None)
    order_state_machine.transition_order(db_session, order.id, OrderStatus.CANCELLED, current_user=None)

    db_session.refresh(listing)
    db_session.refresh(requirement)
    assert float(listing.quantity_reserved) == 0
    assert listing.available_quantity == 1000
    assert float(requirement.fulfilled_quantity) == 0
    assert listing.status == ListingStatus.AVAILABLE


def test_invalid_transition_is_rejected(db_session):
    order, *_ = _create_order(db_session)
    with pytest.raises(InvalidStateTransitionError):
        # Can't jump straight from MATCHED to DELIVERED.
        order_state_machine.transition_order(db_session, order.id, OrderStatus.DELIVERED, current_user=None)


def test_cannot_transition_out_of_a_terminal_status(db_session):
    order, *_ = _create_order(db_session)
    order_state_machine.transition_order(db_session, order.id, OrderStatus.REJECTED, current_user=None)

    with pytest.raises(InvalidStateTransitionError):
        order_state_machine.transition_order(db_session, order.id, OrderStatus.ACCEPTED, current_user=None)


def test_duplicate_completion_is_rejected(db_session):
    order, *_ = _create_order(db_session, quantity=100, listing_quantity=1000)
    for status in [
        OrderStatus.ACCEPTED,
        OrderStatus.RESERVED,
        OrderStatus.CONFIRMED,
        OrderStatus.PICKUP_ASSIGNED,
        OrderStatus.PICKED_UP,
        OrderStatus.IN_TRANSIT,
        OrderStatus.DELIVERED,
        OrderStatus.COMPLETED,
    ]:
        order = order_state_machine.transition_order(db_session, order.id, status, current_user=None)

    # Completed is terminal — even asking to "re-complete" it must fail,
    # not silently succeed a second time.
    with pytest.raises(InvalidStateTransitionError):
        order_state_machine.transition_order(db_session, order.id, OrderStatus.COMPLETED, current_user=None)


def test_repeating_the_same_status_is_rejected_as_duplicate(db_session):
    order, *_ = _create_order(db_session)
    order_state_machine.transition_order(db_session, order.id, OrderStatus.ACCEPTED, current_user=None)
    with pytest.raises(DuplicateOperationError):
        order_state_machine.transition_order(db_session, order.id, OrderStatus.ACCEPTED, current_user=None)


def test_unauthorized_user_cannot_transition_order(db_session):
    order, farmer, buyer, listing, requirement = _create_order(db_session)
    stranger = make_buyer(db_session).user  # a buyer with no relation to this order

    with pytest.raises(ForbiddenError):
        order_state_machine.transition_order(db_session, order.id, OrderStatus.ACCEPTED, current_user=stranger)


def test_order_party_can_transition_order(db_session):
    order, farmer, buyer, listing, requirement = _create_order(db_session)
    # Should not raise — the buyer is a legitimate party to this order.
    order = order_state_machine.transition_order(db_session, order.id, OrderStatus.ACCEPTED, current_user=buyer.user)
    assert order.status == OrderStatus.ACCEPTED


def test_version_increments_on_every_transition(db_session):
    order, *_ = _create_order(db_session)
    assert order.version == 0
    order = order_state_machine.transition_order(db_session, order.id, OrderStatus.ACCEPTED, current_user=None)
    assert order.version == 1
    order = order_state_machine.transition_order(db_session, order.id, OrderStatus.RESERVED, current_user=None)
    assert order.version == 2
