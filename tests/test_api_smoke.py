from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")

from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.auth import create_jwt
from src.api.main import app
from src.db.models import Base, Trade, TradeSide, TradeStatus, User, UserRole
from src.db.session import get_db


def _auth_header(user_id: int, tg_user_id: int, role: str) -> dict[str, str]:
    token = create_jwt({"id": user_id, "tg_user_id": tg_user_id, "role": role})
    return {"Authorization": f"Bearer {token}"}


def _make_client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        trader = User(tg_user_id=1001, role=UserRole.TRADER, display_name="Trader A")
        other = User(tg_user_id=1002, role=UserRole.TRADER, display_name="Trader B")
        db.add_all([trader, other])
        db.flush()
        db.add_all(
            [
                Trade(
                    trader_id=trader.id,
                    symbol="BTCUSDT",
                    side=TradeSide.LONG,
                    entry_price=100,
                    size_pct=1,
                    leverage=1,
                    sl=95,
                    tp1=110,
                    status=TradeStatus.CLOSED,
                    raw_text="",
                    parsed_json={},
                    created_at=datetime.utcnow(),
                ),
                Trade(
                    trader_id=other.id,
                    symbol="ETHUSDT",
                    side=TradeSide.SHORT,
                    entry_price=200,
                    size_pct=1,
                    leverage=1,
                    sl=210,
                    tp1=190,
                    status=TradeStatus.OPEN,
                    raw_text="",
                    parsed_json={},
                    created_at=datetime.utcnow(),
                ),
            ]
        )
        db.commit()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_trades_smoke_200() -> None:
    client = _make_client()
    res = client.get("/trades", headers=_auth_header(1, 1001, "trader"))
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_metrics_smoke_200() -> None:
    client = _make_client()
    res = client.get("/metrics/basic", headers=_auth_header(1, 1001, "trader"))
    assert res.status_code == 200
    assert "winrate" in res.json()
