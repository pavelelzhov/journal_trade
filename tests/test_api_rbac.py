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


def _auth(uid: int, tg: int, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_jwt({'id': uid, 'tg_user_id': tg, 'role': role})}"}


def _client() -> TestClient:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        u1 = User(tg_user_id=11, role=UserRole.TRADER, display_name="u1")
        u2 = User(tg_user_id=22, role=UserRole.TRADER, display_name="u2")
        admin = User(tg_user_id=99, role=UserRole.ADMIN, display_name="admin")
        db.add_all([u1, u2, admin])
        db.flush()
        db.add(
            Trade(
                trader_id=u2.id,
                symbol="BTCUSDT",
                side=TradeSide.LONG,
                entry_price=100,
                size_pct=1,
                leverage=1,
                status=TradeStatus.OPEN,
                raw_text="",
                parsed_json={},
                created_at=datetime.utcnow(),
            )
        )
        db.commit()

    def override_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def test_trader_cannot_access_foreign_trade() -> None:
    client = _client()
    res = client.get("/trades/1", headers=_auth(1, 11, "trader"))
    assert res.status_code == 403


def test_admin_can_filter_by_trader_id() -> None:
    client = _client()
    res = client.get("/trades?trader_id=2", headers=_auth(3, 99, "admin"))
    assert res.status_code == 200
    assert len(res.json()) == 1
