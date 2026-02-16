from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CurrentUser:
    telegram_user_id: int
    role: str


def apply_trade_scope(items: list[dict[str, Any]], user: CurrentUser) -> list[dict[str, Any]]:
    if user.role.upper() == "ADMIN":
        return items
    return [x for x in items if x.get("telegram_user_id") == user.telegram_user_id]
