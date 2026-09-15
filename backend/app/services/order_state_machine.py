"""
Order lifecycle state machine.

MATCHED -> ACCEPTED -> RESERVED -> CONFIRMED -> PICKUP_ASSIGNED ->
PICKED_UP -> IN_TRANSIT -> DELIVERED -> COMPLETED

Side branches: CANCELLED, REJECTED, PARTIALLY_FULFILLED, DISPUTED.

Every transition:
  1. locks the Order row (SELECT ... FOR UPDATE) so two concurrent
     transition requests for the same order can't both succeed,
  2. checks the caller is actually a party to the order (or an admin),
  3. checks the transition is allowed from the order's CURRENT status
     (re-read under the lock, not whatever the caller thought it was),
  4. applies any inventory side effect atomically in the same
     transaction (reserve / release / finalize — see services/inventory.py),
  5. writes one immutable OrderStatusHistory row,
  6. commits everything together.

If any step raises, nothing above is left half-applied — it's one
transaction.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    NotFoundError,
    ForbiddenError,
    InvalidStateTransitionError,
    DuplicateOperationError,
)
from app.models.enums import OrderStatus, UserRole, TERMINAL_ORDER_STATUSES, INVENTORY_RESERVED_STATUSES
from app.models.identity import User
from app.models.orders import Order, OrderStatusHistory
from app.services import inventory

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.MATCHED: {OrderStatus.ACCEPTED, OrderStatus.REJECTED, OrderStatus.CANCELLED},
    OrderStatus.ACCEPTED: {OrderStatus.RESERVED, OrderStatus.CANCELLED, OrderStatus.REJECTED},
    OrderStatus.RESERVED: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PICKUP_ASSIGNED, OrderStatus.CANCELLED, OrderStatus.DISPUTED},
    OrderStatus.PICKUP_ASSIGNED: {OrderStatus.PICKED_UP, OrderStatus.CANCELLED, OrderStatus.DISPUTED},
    OrderStatus.PICKED_UP: {OrderStatus.IN_TRANSIT, OrderStatus.DISPUTED},
    OrderStatus.IN_TRANSIT: {OrderStatus.DELIVERED, OrderStatus.DISPUTED},
    OrderStatus.DELIVERED: {OrderStatus.COMPLETED, OrderStatus.PARTIALLY_FULFILLED, OrderStatus.DISPUTED},
    OrderStatus.PARTIALLY_FULFILLED: {OrderStatus.COMPLETED, OrderStatus.DISPUTED},
    OrderStatus.DISPUTED: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.REJECTED: set(),
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _lock_order(db: Session, order_id: int) -> Order:
    order = db.scalar(select(Order).where(Order.id == order_id).with_for_update())
    if order is None:
        raise NotFoundError("Order not found.")
    return order


def _check_authorization(order: Order, user: User | None) -> None:
    if user is None:
        return  # internal/system call (e.g. from tests or scheduled jobs)
    if user.role == UserRole.ADMIN:
        return
    is_farmer_party = order.farmer.user_id == user.id
    is_buyer_party = order.buyer.user_id == user.id
    if not (is_farmer_party or is_buyer_party):
        raise ForbiddenError("You are not a party to this order.")


def transition_order(
    db: Session,
    order_id: int,
    new_status: OrderStatus,
    current_user: User | None,
    note: str | None = None,
) -> Order:
    order = _lock_order(db, order_id)
    _check_authorization(order, current_user)

    old_status = order.status

    if old_status in TERMINAL_ORDER_STATUSES:
        raise InvalidStateTransitionError(
            f"Order is already {old_status.value} and cannot be modified further."
        )
    if new_status == old_status:
        raise DuplicateOperationError(f"Order is already {old_status.value}.")

    allowed = ALLOWED_TRANSITIONS.get(old_status, set())
    if new_status not in allowed:
        raise InvalidStateTransitionError(
            f"Cannot move an order from {old_status.value} to {new_status.value}."
        )

    # --- Inventory side effects, inside the same locked transaction ---
    if new_status == OrderStatus.RESERVED:
        inventory.reserve(db, order.listing_id, order.requirement_id, float(order.quantity))
    elif new_status in (OrderStatus.CANCELLED, OrderStatus.REJECTED) and old_status in INVENTORY_RESERVED_STATUSES:
        inventory.release(db, order.listing_id, order.requirement_id, float(order.quantity))
    elif new_status == OrderStatus.COMPLETED:
        inventory.finalize_sale(db, order.listing_id, float(order.quantity))

    order.status = new_status
    order.version += 1
    db.add(order)

    db.add(
        OrderStatusHistory(
            order_id=order.id,
            from_status=old_status,
            to_status=new_status,
            changed_by_user_id=current_user.id if current_user else None,
            note=note,
            created_at=_utcnow(),
        )
    )

    db.commit()
    db.refresh(order)
    return order


def record_initial_status(db: Session, order: Order, current_user: User | None) -> None:
    """Call once, right after an Order row is first inserted, so the
    audit trail has a starting point (from_status=None)."""
    db.add(
        OrderStatusHistory(
            order_id=order.id,
            from_status=None,
            to_status=order.status,
            changed_by_user_id=current_user.id if current_user else None,
            note="Order created from accepted match.",
            created_at=_utcnow(),
        )
    )
    db.commit()
