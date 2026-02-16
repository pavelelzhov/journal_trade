from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.auth import AuthUser
from src.db.session import get_db


def get_current_user(request: Request) -> AuthUser:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db
