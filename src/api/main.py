from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Query

from src.api.deps import get_current_user
from src.api.rbac import CurrentUser, apply_trade_scope

app = FastAPI(title="Cloud Journal v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/trades")
def get_trades(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    symbol: str | None = Query(default=None),
    status: str | None = Query(default=None),
    trader_telegram_user_id: int | None = Query(default=None),
) -> dict:
    _ = (date_from, date_to, symbol, status, trader_telegram_user_id)
    records: list[dict] = []
    scoped = apply_trade_scope(records, user)
    return {"items": scoped, "count": len(scoped)}


@app.get("/metrics")
def metrics(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> dict:
    _ = (user, date_from, date_to)
    return {"items": []}


@app.get("/export")
def export_data(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    format: Literal["csv", "json"] = Query(default="json"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    symbol: str | None = Query(default=None),
    status: str | None = Query(default=None),
    trader_telegram_user_id: int | None = Query(default=None),
) -> dict:
    _ = (user, format, date_from, date_to, symbol, status, trader_telegram_user_id)
    return {"format": format, "items": []}


@app.post("/import")
def import_data(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    format: Literal["csv", "json"] = Query(default="json"),
) -> dict:
    _ = (user, format)
    return {"format": format, "imported": 0}
