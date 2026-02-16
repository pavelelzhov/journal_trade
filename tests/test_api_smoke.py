from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")

from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.db.models import Base, Trade, TradeStatus, Trader, User, UserRole
from src.db.session import get_db


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
        user = User(telegram_user_id=1001, role=UserRole.TRADER)
        db.add(user)
        db.flush()
        trader = Trader(user_id=user.id)
        db.add(trader)
        db.flush()
        db.add(
            Trade(
                trader_id=trader.id,
                symbol="BTCUSDT",
                side="long",
                entries_json=[{"price": 100.0}],
                sl=95.0,
                tps_json=[110.0],
                position_pct=1.0,
                status=TradeStatus.CLOSED,
                ts=datetime.utcnow(),
            )
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
    res = client.get("/trades", headers={"X-Role": "TRADER", "X-Telegram-User-Id": "1001"})
    assert res.status_code == 200
    assert "items" in res.json()


def test_metrics_smoke_200() -> None:
    client = _make_client()
    res = client.get("/metrics", headers={"X-Role": "TRADER", "X-Telegram-User-Id": "1001"})
    assert res.status_code == 200
    assert "kpi" in res.json()
