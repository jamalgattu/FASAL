from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import identity as crud_identity
from app.database import get_db
from app.models.identity import Farmer
from app.schemas.identity import FarmerRead

router = APIRouter(prefix="/fpos", tags=["fpos"])


def _to_read(farmer: Farmer) -> FarmerRead:
    read = FarmerRead.model_validate(farmer)
    read.full_name = farmer.user.full_name
    return read


@router.get("/", response_model=list[FarmerRead])
def list_fpos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    fpos = crud_identity.list_farmers(db, only_fpo=True, skip=skip, limit=limit)
    return [_to_read(f) for f in fpos]


@router.get("/{fpo_id}", response_model=FarmerRead)
def read_fpo(fpo_id: int, db: Session = Depends(get_db)):
    farmer = db.get(Farmer, fpo_id)
    if farmer is None or not farmer.is_fpo:
        raise NotFoundError("FPO not found.")
    return _to_read(farmer)
