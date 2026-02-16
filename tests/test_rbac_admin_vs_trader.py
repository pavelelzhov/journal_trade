from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")

from fastapi import HTTPException

from src.api.auth import AuthUser
from src.api.rbac import enforce_trader_scope, ensure_admin


def test_admin_can_access_any_trader_scope() -> None:
    admin = AuthUser(id=1, tg_user_id=111, role="admin")
    enforce_trader_scope(admin, target_trader_id=999)


def test_trader_cannot_access_foreign_scope() -> None:
    trader = AuthUser(id=2, tg_user_id=222, role="trader")
    with pytest.raises(HTTPException):
        enforce_trader_scope(trader, target_trader_id=999)


def test_ensure_admin_rejects_trader() -> None:
    trader = AuthUser(id=2, tg_user_id=222, role="trader")
    with pytest.raises(HTTPException):
        ensure_admin(trader)
