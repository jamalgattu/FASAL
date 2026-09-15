from typing import Generic, TypeVar, Type, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """Minimal generic CRUD — entity-specific business rules live in their
    own crud/*.py functions or in app/services/, not here."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def create(self, db: Session, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, db_obj: ModelType, updates: dict) -> ModelType:
        for field, value in updates.items():
            if value is not None:
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: ModelType) -> None:
        db.delete(db_obj)
        db.commit()
