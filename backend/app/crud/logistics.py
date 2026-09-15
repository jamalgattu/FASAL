from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.logistics import Vehicle, Delivery
from app.models.orders import Order
from app.models.enums import DeliveryStatus, OrderStatus


def create_vehicle(db: Session, data) -> Vehicle:
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def list_vehicles(db: Session, active_only: bool = False) -> list[Vehicle]:
    stmt = select(Vehicle)
    if active_only:
        stmt = stmt.where(Vehicle.is_active.is_(True))
    return list(db.scalars(stmt).all())


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.get(Vehicle, vehicle_id)


def update_vehicle(db: Session, vehicle: Vehicle, updates: dict) -> Vehicle:
    for field, value in updates.items():
        if value is not None:
            setattr(vehicle, field, value)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def get_or_create_delivery(db: Session, order: Order) -> Delivery:
    delivery = db.scalar(select(Delivery).where(Delivery.order_id == order.id))
    if delivery is None:
        delivery = Delivery(order_id=order.id, status=DeliveryStatus.PENDING)
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
    return delivery


def assign_vehicle(db: Session, order: Order, vehicle_id: int, sequence: int | None) -> Delivery:
    if order.status != OrderStatus.PICKUP_ASSIGNED:
        raise ConflictError("A vehicle can only be assigned once the order is in PICKUP_ASSIGNED status.")

    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise NotFoundError("Vehicle not found.")
    if not vehicle.is_active:
        raise ConflictError("This vehicle is not active.")

    projected_load = float(vehicle.current_load_kg) + float(order.quantity)
    if projected_load > float(vehicle.capacity_kg):
        raise ConflictError(
            f"Assigning this order would exceed the vehicle's capacity "
            f"({projected_load}kg > {vehicle.capacity_kg}kg)."
        )

    delivery = get_or_create_delivery(db, order)
    delivery.vehicle_id = vehicle_id
    delivery.status = DeliveryStatus.ASSIGNED
    delivery.sequence = sequence
    vehicle.current_load_kg = projected_load

    db.add(delivery)
    db.add(vehicle)
    db.commit()
    db.refresh(delivery)
    return delivery


def update_delivery_status(db: Session, delivery: Delivery, new_status: DeliveryStatus, notes: str | None) -> Delivery:
    now = datetime.now(timezone.utc)
    if new_status == DeliveryStatus.PICKED_UP:
        delivery.picked_up_at = now
    elif new_status == DeliveryStatus.DELIVERED:
        delivery.delivered_at = now
        if delivery.vehicle_id:
            vehicle = db.get(Vehicle, delivery.vehicle_id)
            if vehicle:
                vehicle.current_load_kg = max(0.0, float(vehicle.current_load_kg) - float(delivery.order.quantity))
                db.add(vehicle)

    delivery.status = new_status
    if notes:
        delivery.notes = notes
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery
