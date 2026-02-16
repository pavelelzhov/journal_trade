from __future__ import annotations

from fastapi import HTTPException

from src.api.auth import AuthUser


def ensure_admin(user: AuthUser) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")


def enforce_trader_scope(requester: AuthUser, target_trader_id: int) -> None:
    if requester.role == "admin":
        return
    if requester.id != target_trader_id:
        raise HTTPException(status_code=403, detail="forbidden")
