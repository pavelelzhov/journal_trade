from __future__ import annotations

from datetime import date, datetime
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from src.api.auth import AuthUser, create_jwt, verify_jwt, verify_telegram_login
from src.api.deps import get_current_user, get_db_session
from src.api.rbac import enforce_trader_scope, ensure_admin
from src.db.models import Trade, TradeSide, TradeStatus, User, UserRole

BOT_TOKEN = os.getenv("BOT_TOKEN", "dev-bot-token")

app = FastAPI(title="Journal API v1")


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = verify_jwt(token)
            request.state.user = AuthUser(
                id=int(payload["id"]),
                tg_user_id=int(payload["tg_user_id"]),
                role=str(payload["role"]),
            )
        except Exception:
            request.state.user = None
    else:
        request.state.user = None
    return await call_next(request)


class TelegramLoginPayload(BaseModel):
    id: int
    first_name: str | None = None
    username: str | None = None
    auth_date: int
    hash: str


class TradeIn(BaseModel):
    trader_id: int
    symbol: str
    side: TradeSide
    entry_price: float
    size_pct: float
    leverage: float = 1.0
    sl: float | None = None
    tp1: float | None = None
    tp2: float | None = None
    tp3: float | None = None
    status: TradeStatus = TradeStatus.DRAFT
    raw_text: str = ""
    parsed_json: dict = Field(default_factory=dict)


class TradeOut(BaseModel):
    id: int
    trader_id: int
    symbol: str
    side: TradeSide
    entry_price: float
    size_pct: float
    leverage: float
    sl: float | None
    tp1: float | None
    tp2: float | None
    tp3: float | None
    status: TradeStatus
    raw_text: str
    parsed_json: dict
    created_at: datetime


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/telegram")
def auth_telegram(payload: TelegramLoginPayload, db: Annotated[Session, Depends(get_db_session)]):
    data = payload.model_dump()
    if not verify_telegram_login(data, BOT_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid telegram payload")

    user = db.execute(select(User).where(User.tg_user_id == payload.id)).scalar_one_or_none()
    if not user:
        user = User(
            tg_user_id=payload.id,
            role=UserRole.TRADER,
            display_name=payload.username or payload.first_name or f"tg-{payload.id}",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_jwt({"id": user.id, "tg_user_id": user.tg_user_id, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me")
def me(user: Annotated[AuthUser, Depends(get_current_user)], db: Annotated[Session, Depends(get_db_session)]):
    db_user = db.execute(select(User).where(User.id == user.id)).scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": db_user.id, "tg_user_id": db_user.tg_user_id, "role": db_user.role.value, "display_name": db_user.display_name}


@app.post("/trades", response_model=TradeOut)
def create_trade(
    payload: TradeIn,
    user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    enforce_trader_scope(user, payload.trader_id)
    trade = Trade(**payload.model_dump())
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


@app.get("/trades", response_model=list[TradeOut])
def list_trades(
    user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    symbol: str | None = None,
    status: TradeStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    trader_id: int | None = None,
):
    stmt = select(Trade)
    filters = []
    if symbol:
        filters.append(func.lower(Trade.symbol) == symbol.lower())
    if status:
        filters.append(Trade.status == status)
    if date_from:
        filters.append(Trade.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        filters.append(Trade.created_at <= datetime.combine(date_to, datetime.max.time()))

    if user.role == "admin":
        if trader_id is not None:
            filters.append(Trade.trader_id == trader_id)
    else:
        filters.append(Trade.trader_id == user.id)

    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(Trade.created_at.desc(), Trade.id.desc())

    return list(db.execute(stmt).scalars().all())


@app.get("/trades/{trade_id}", response_model=TradeOut)
def get_trade(
    trade_id: int,
    user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    trade = db.execute(select(Trade).where(Trade.id == trade_id)).scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    enforce_trader_scope(user, trade.trader_id)
    return trade


@app.put("/trades/{trade_id}", response_model=TradeOut)
def update_trade(
    trade_id: int,
    payload: TradeIn,
    user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    trade = db.execute(select(Trade).where(Trade.id == trade_id)).scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    enforce_trader_scope(user, trade.trader_id)
    enforce_trader_scope(user, payload.trader_id)

    for k, v in payload.model_dump().items():
        setattr(trade, k, v)
    db.commit()
    db.refresh(trade)
    return trade


@app.delete("/trades/{trade_id}")
def delete_trade(
    trade_id: int,
    user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    trade = db.execute(select(Trade).where(Trade.id == trade_id)).scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    enforce_trader_scope(user, trade.trader_id)
    db.delete(trade)
    db.commit()
    return {"deleted": True}


@app.get("/metrics/basic")
def metrics_basic(
    user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    trader_id: int | None = None,
):
    if trader_id is not None and user.role != "admin":
        raise HTTPException(status_code=403, detail="trader_id filter allowed for admin only")

    stmt = select(Trade)
    if user.role == "admin":
        if trader_id is not None:
            stmt = stmt.where(Trade.trader_id == trader_id)
    else:
        stmt = stmt.where(Trade.trader_id == user.id)

    trades = list(db.execute(stmt).scalars().all())
    total = len(trades)
    closed = [t for t in trades if t.status == TradeStatus.CLOSED]

    win_count = 0
    r_values: list[float] = []
    for t in closed:
        if t.sl is None or t.tp1 is None:
            continue
        risk = abs(t.entry_price - t.sl)
        if risk <= 0:
            continue
        reward = abs(t.tp1 - t.entry_price)
        r = reward / risk
        if (t.side == TradeSide.LONG and t.tp1 > t.entry_price) or (t.side == TradeSide.SHORT and t.tp1 < t.entry_price):
            win_count += 1
            r_values.append(r)
        else:
            r_values.append(-1.0)

    denom = len(r_values)
    winrate = (win_count / denom * 100.0) if denom else 0.0
    avg_r = (sum(r_values) / denom) if denom else 0.0

    return {
        "total_trades": total,
        "closed_trades": len(closed),
        "winrate": round(winrate, 4),
        "avg_r": round(avg_r, 4),
    }


@app.get("/admin/users")
def admin_users(
    user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    ensure_admin(user)
    users = db.execute(select(User).order_by(User.id.asc())).scalars().all()
    return [
        {"id": u.id, "tg_user_id": u.tg_user_id, "role": u.role.value, "display_name": u.display_name}
        for u in users
    ]
