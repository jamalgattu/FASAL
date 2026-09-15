from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import catalog as crud_catalog
from app.database import get_db
from app.models.identity import User
from app.schemas.catalog import CropCreate, CropRead

router = APIRouter(prefix="/crops", tags=["crops"])


@router.get("/", response_model=list[CropRead])
def list_crops(db: Session = Depends(get_db)):
    return crud_catalog.list_crops(db)


@router.post("/", response_model=CropRead, status_code=201)
def create_crop(data: CropCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud_catalog.get_or_create_crop(db, data.name)
