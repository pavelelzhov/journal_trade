from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import String, and_, cast, func, or_, select
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.api.rbac import CurrentUser
from src.db.models import Trade, TradeStatus, Trader, User
from src.db.session import get_db

app = FastAPI(title="Cloud Journal v1")


def _apply_trade_filters(stmt, *, date_from: date | None, date_to: date | None, symbol: str | None, side: str | None, status: str | None, search: str | None):
    if date_from:
        stmt = stmt.where(Trade.ts >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        stmt = stmt.where(Trade.ts <= datetime.combine(date_to, datetime.max.time()))
    if symbol:
        stmt = stmt.where(func.lower(Trade.symbol) == symbol.lower())
    if side:
        stmt = stmt.where(func.lower(Trade.side) == side.lower())
    if status:
        stmt = stmt.where(Trade.status == TradeStatus(status.upper()))
    if search:
        pattern = f"%{search.lower()}%"
        stmt = stmt.where(or_(func.lower(Trade.symbol).like(pattern), func.lower(Trade.side).like(pattern), cast(Trade.id, String).like(pattern)))
    return stmt


def _rbac_trade_stmt(stmt, user: CurrentUser, trader_id: int | None):
    if user.role == "ADMIN":
        if trader_id is not None:
            stmt = stmt.where(Trade.trader_id == trader_id)
        return stmt

    stmt = stmt.join(Trader, Trader.id == Trade.trader_id).join(User, User.id == Trader.user_id).where(User.telegram_user_id == user.telegram_user_id)
    if trader_id is not None:
        stmt = stmt.where(Trade.trader_id == trader_id)
    return stmt


def _serialize_trade_row(row: tuple[Trade, int | None]) -> dict:
    trade, telegram_user_id = row
    return {
        "id": trade.id,
        "trader_id": trade.trader_id,
        "telegram_user_id": telegram_user_id,
        "symbol": trade.symbol,
        "side": trade.side,
        "entries": trade.entries_json,
        "sl": trade.sl,
        "tps": trade.tps_json,
        "position_pct": trade.position_pct,
        "status": trade.status.value if hasattr(trade.status, "value") else str(trade.status),
        "ts": trade.ts.isoformat() if trade.ts else None,
    }


def _get_trade_rows(db: Session, user: CurrentUser, *, date_from: date | None = None, date_to: date | None = None, symbol: str | None = None, side: str | None = None, status: str | None = None, search: str | None = None, trader_id: int | None = None, limit: int = 50, offset: int = 0):
    base = select(Trade, User.telegram_user_id).join(Trader, Trader.id == Trade.trader_id).join(User, User.id == Trader.user_id)
    base = _rbac_trade_stmt(base, user, trader_id)
    base = _apply_trade_filters(base, date_from=date_from, date_to=date_to, symbol=symbol, side=side, status=status, search=search)

    total_stmt = select(func.count()).select_from(base.subquery())
    total = db.execute(total_stmt).scalar_one()

    rows = db.execute(base.order_by(Trade.ts.desc(), Trade.id.desc()).limit(limit).offset(offset)).all()
    return [_serialize_trade_row(x) for x in rows], int(total)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/trades")
def get_trades(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    symbol: str | None = Query(default=None),
    side: str | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    trader_id: int | None = Query(default=None),
) -> dict:
    items, total = _get_trade_rows(
        db,
        user,
        limit=limit,
        offset=offset,
        date_from=date_from,
        date_to=date_to,
        symbol=symbol,
        side=side,
        status=status,
        search=search,
        trader_id=trader_id,
    )
    return {"items": items, "total": total}


@app.get("/trades/{trade_id}")
def get_trade(
    trade_id: int,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    stmt = (
        select(Trade, User.telegram_user_id)
        .join(Trader, Trader.id == Trade.trader_id)
        .join(User, User.id == Trader.user_id)
        .where(Trade.id == trade_id)
    )
    stmt = _rbac_trade_stmt(stmt, user, trader_id=None)
    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(status_code=404, detail="Trade not found")
    return _serialize_trade_row(row)


@app.get("/metrics")
def metrics(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    symbol: str | None = Query(default=None),
    side: str | None = Query(default=None),
    status: str | None = Query(default=None),
    trader_id: int | None = Query(default=None),
) -> dict:
    items, total = _get_trade_rows(
        db,
        user,
        limit=5000,
        offset=0,
        date_from=date_from,
        date_to=date_to,
        symbol=symbol,
        side=side,
        status=status,
        search=None,
        trader_id=trader_id,
    )

    closed = [x for x in items if x["status"] == "CLOSED"]
    wins = [x for x in closed if x.get("tps")]
    losses = [x for x in closed if not x.get("tps")]
    winrate = (len(wins) / len(closed) * 100.0) if closed else 0.0
    pf = (len(wins) / len(losses)) if losses else float(len(wins))
    expectancy = ((len(wins) - len(losses)) / len(closed)) if closed else 0.0

    equity_curve = [{"index": idx + 1, "equity": idx + 1} for idx in range(total)]
    by_symbol: dict[str, int] = {}
    for item in items:
        by_symbol[item["symbol"]] = by_symbol.get(item["symbol"], 0) + 1

    return {
        "kpi": {
            "total_trades": total,
            "winrate": round(winrate, 2),
            "profit_factor": round(pf, 2),
            "expectancy": round(expectancy, 4),
        },
        "equity_curve": equity_curve,
        "r_histogram": [],
        "breakdown_by_symbol": [{"symbol": k, "count": v} for k, v in sorted(by_symbol.items())],
    }


@app.get("/export")
def export_data(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    format: Literal["csv", "json"] = Query(default="json"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    symbol: str | None = Query(default=None),
    side: str | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    trader_id: int | None = Query(default=None),
):
    items, _ = _get_trade_rows(
        db,
        user,
        limit=10000,
        offset=0,
        date_from=date_from,
        date_to=date_to,
        symbol=symbol,
        side=side,
        status=status,
        search=search,
        trader_id=trader_id,
    )
    if format == "json":
        return {"items": items}

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "trader_id", "telegram_user_id", "symbol", "side", "sl", "position_pct", "status", "ts"])
    writer.writeheader()
    for item in items:
        writer.writerow({k: item.get(k) for k in writer.fieldnames})
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=trades.csv"})


@app.post("/import")
def import_data(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    format: Literal["csv", "json"] = Query(default="json"),
    file: UploadFile = File(...),
) -> dict:
    raw = file.file.read().decode("utf-8")
    rows: list[dict]
    if format == "json":
        import json

        payload = json.loads(raw)
        rows = payload if isinstance(payload, list) else payload.get("items", [])
    else:
        reader = csv.DictReader(io.StringIO(raw))
        rows = list(reader)

    imported = 0
    failed = 0
    errors: list[dict] = []
    for idx, row in enumerate(rows, start=1):
        try:
            trader_id = int(row.get("trader_id") or 0)
            if trader_id <= 0:
                raise ValueError("trader_id is required")

            if user.role != "ADMIN":
                owner_stmt = select(Trader.id).join(User, User.id == Trader.user_id).where(and_(Trader.id == trader_id, User.telegram_user_id == user.telegram_user_id))
                if not db.execute(owner_stmt).scalar_one_or_none():
                    raise ValueError("forbidden trader_id")

            trade = Trade(
                trader_id=trader_id,
                symbol=str(row.get("symbol") or "").upper(),
                side=str(row.get("side") or "").lower(),
                entries_json=row.get("entries") if isinstance(row.get("entries"), list) else [],
                sl=float(row["sl"]) if row.get("sl") not in (None, "") else None,
                tps_json=row.get("tps") if isinstance(row.get("tps"), list) else [],
                position_pct=float(row["position_pct"]) if row.get("position_pct") not in (None, "") else None,
                status=TradeStatus((row.get("status") or "DRAFT").upper()),
            )
            if not trade.symbol or not trade.side:
                raise ValueError("symbol and side are required")
            db.add(trade)
            imported += 1
        except Exception as exc:  # deterministic error report
            failed += 1
            errors.append({"row": idx, "error": str(exc)})

    db.commit()
    return {"imported": imported, "failed": failed, "errors": errors}


@app.get("/admin/users")
def admin_users(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="admin only")
    rows = db.execute(select(User.id, User.telegram_user_id, User.role, Trader.id).outerjoin(Trader, Trader.user_id == User.id)).all()
    return {
        "items": [
            {
                "user_id": r[0],
                "telegram_user_id": r[1],
                "role": r[2].value if hasattr(r[2], "value") else str(r[2]),
                "trader_id": r[3],
            }
            for r in rows
        ]
    }
