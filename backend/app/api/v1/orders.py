from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.crud import matching as crud_matching
from app.crud import orders as crud_orders
from app.crud import identity as crud_identity
from app.database import get_db
from app.models.enums import UserRole, MatchStatus
from app.models.identity import User
from app.schemas.orders import OrderCreateFromMatch, OrderRead, OrderDetailRead, OrderTransitionRequest
from app.services import order_state_machine

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderRead, status_code=201)
def create_order(
    data: OrderCreateFromMatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = crud_matching.get_match(db, data.match_id)
    if match is None:
        raise NotFoundError("Match not found.")
    if match.status != MatchStatus.ACCEPTED:
        raise ConflictError("Only an ACCEPTED match can be converted into an order.")

    is_farmer_party = match.listing.farmer.user_id == current_user.id
    is_buyer_party = match.requirement.buyer.user_id == current_user.id
    if current_user.role != UserRole.ADMIN and not (is_farmer_party or is_buyer_party):
        raise ForbiddenError("You are not a party to this match.")

    return crud_orders.create_order_from_match(db, match, created_by_user_id=current_user.id)


@router.get("/", response_model=list[OrderRead])
def list_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == UserRole.FARMER:
        farmer = crud_identity.get_farmer_by_user_id(db, current_user.id)
        return crud_orders.list_orders_for_farmer(db, farmer.id) if farmer else []
    if current_user.role == UserRole.BUYER:
        buyer = crud_identity.get_buyer_by_user_id(db, current_user.id)
        return crud_orders.list_orders_for_buyer(db, buyer.id) if buyer else []
    return []  # admin: use farmer_id/buyer_id specific endpoints, or extend as needed


def _check_order_party(order, current_user: User):
    if current_user.role == UserRole.ADMIN:
        return
    is_farmer_party = order.farmer.user_id == current_user.id
    is_buyer_party = order.buyer.user_id == current_user.id
    if not (is_farmer_party or is_buyer_party):
        raise ForbiddenError("You are not a party to this order.")


@router.get("/{order_id}", response_model=OrderDetailRead)
def read_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = crud_orders.get_order(db, order_id)
    if order is None:
        raise NotFoundError("Order not found.")
    _check_order_party(order, current_user)
    return order


@router.post("/{order_id}/transition", response_model=OrderDetailRead)
def transition_order_status(
    order_id: int,
    data: OrderTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = order_state_machine.transition_order(db, order_id, data.new_status, current_user, data.note)
    return order
