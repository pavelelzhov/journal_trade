from __future__ import annotations

from src.api.rbac import CurrentUser, apply_trade_scope


def test_admin_sees_all_trades() -> None:
    items = [
        {"id": 1, "telegram_user_id": 101},
        {"id": 2, "telegram_user_id": 202},
    ]
    admin = CurrentUser(telegram_user_id=999, role="ADMIN")

    assert apply_trade_scope(items, admin) == items


def test_trader_sees_only_own_trades() -> None:
    items = [
        {"id": 1, "telegram_user_id": 101},
        {"id": 2, "telegram_user_id": 202},
        {"id": 3, "telegram_user_id": 101},
    ]
    trader = CurrentUser(telegram_user_id=101, role="TRADER")

    assert apply_trade_scope(items, trader) == [
        {"id": 1, "telegram_user_id": 101},
        {"id": 3, "telegram_user_id": 101},
    ]
