from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.exceptions import NotFoundError
from app.crud import logistics as crud_logistics
from app.database import get_db
from app.models.enums import UserRole
from app.models.identity import User
from app.schemas.logistics import VehicleCreate, VehicleUpdate, VehicleRead

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("/", response_model=VehicleRead, status_code=201)
def create_vehicle(
    data: VehicleCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    return crud_logistics.create_vehicle(db, data)


@router.get("/", response_model=list[VehicleRead])
def list_vehicles(active_only: bool = False, db: Session = Depends(get_db)):
    return crud_logistics.list_vehicles(db, active_only)


@router.get("/{vehicle_id}", response_model=VehicleRead)
def read_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = crud_logistics.get_vehicle(db, vehicle_id)
    if vehicle is None:
        raise NotFoundError("Vehicle not found.")
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(
    vehicle_id: int,
    updates: VehicleUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    vehicle = crud_logistics.get_vehicle(db, vehicle_id)
    if vehicle is None:
        raise NotFoundError("Vehicle not found.")
    return crud_logistics.update_vehicle(db, vehicle, updates.model_dump(exclude_unset=True))
