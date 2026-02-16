from __future__ import annotations

from fastapi import Header, HTTPException

from src.api.rbac import CurrentUser


def get_current_user(
    x_telegram_user_id: int | None = Header(default=None),
    x_role: str | None = Header(default=None),
) -> CurrentUser:
    if x_telegram_user_id is None:
        raise HTTPException(status_code=401, detail="x-telegram-user-id header is required")
    role = (x_role or "TRADER").upper()
    if role not in {"ADMIN", "TRADER"}:
        raise HTTPException(status_code=400, detail="x-role must be ADMIN or TRADER")
    return CurrentUser(telegram_user_id=x_telegram_user_id, role=role)
