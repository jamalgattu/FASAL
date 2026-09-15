from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError
from app.core.security import decode_access_token
from app.crud.identity import get_user
from app.database import get_db
from app.models.enums import UserRole
from app.models.identity import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class CredentialsError(Exception):
    pass


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise ForbiddenError("Invalid or expired authentication token.")
    user = get_user(db, int(payload["sub"]))
    if user is None or not user.is_active:
        raise ForbiddenError("Invalid or expired authentication token.")
    return user


def require_role(*roles: UserRole):
    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles and current_user.role != UserRole.ADMIN:
            raise ForbiddenError(f"This action requires one of these roles: {[r.value for r in roles]}.")
        return current_user

    return _checker
