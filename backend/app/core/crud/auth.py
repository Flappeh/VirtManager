import uuid
from typing import Any

from sqlmodel import Session

from app.core.crud.user import get_user_by_email, verify_password
from app.core.db.models.user import User

def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

