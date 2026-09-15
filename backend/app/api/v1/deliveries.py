from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import logistics as crud_logistics
from app.crud import orders as crud_orders
from app.database import get_db
from app.models.enums import UserRole
from app.models.identity import User
from app.schemas.logistics import DeliveryAssignRequest, DeliveryStatusUpdate, DeliveryRead

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.post("/{order_id}/assign", response_model=DeliveryRead)
def assign_vehicle(
    order_id: int,
    data: DeliveryAssignRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    order = crud_orders.get_order(db, order_id)
    if order is None:
        raise NotFoundError("Order not found.")
    return crud_logistics.assign_vehicle(db, order, data.vehicle_id, data.sequence)


@router.get("/{order_id}", response_model=DeliveryRead)
def read_delivery(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = crud_orders.get_order(db, order_id)
    if order is None:
        raise NotFoundError("Order not found.")
    if current_user.role != UserRole.ADMIN and order.farmer.user_id != current_user.id and order.buyer.user_id != current_user.id:
        raise ForbiddenError("You are not a party to this order.")
    delivery = crud_logistics.get_or_create_delivery(db, order)
    return delivery


@router.patch("/{order_id}/status", response_model=DeliveryRead)
def update_delivery_status(
    order_id: int,
    data: DeliveryStatusUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    order = crud_orders.get_order(db, order_id)
    if order is None:
        raise NotFoundError("Order not found.")
    delivery = crud_logistics.get_or_create_delivery(db, order)
    return crud_logistics.update_delivery_status(db, delivery, data.status, data.notes)
