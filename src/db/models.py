from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    ADMIN = "admin"
    TRADER = "trader"


class TradeSide(str, Enum):
    LONG = "long"
    SHORT = "short"


class TradeStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.TRADER, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), default="", nullable=False)

    trades: Mapped[list[Trade]] = relationship(back_populates="trader", cascade="all, delete-orphan")


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (
        Index("ix_trades_trader_id", "trader_id"),
        Index("ix_trades_symbol", "symbol"),
        Index("ix_trades_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[TradeSide] = mapped_column(SAEnum(TradeSide), nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    size_pct: Mapped[float] = mapped_column(Float, nullable=False)
    leverage: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sl: Mapped[float | None] = mapped_column(Float)
    tp1: Mapped[float | None] = mapped_column(Float)
    tp2: Mapped[float | None] = mapped_column(Float)
    tp3: Mapped[float | None] = mapped_column(Float)
    status: Mapped[TradeStatus] = mapped_column(SAEnum(TradeStatus), default=TradeStatus.DRAFT, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    parsed_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    trader: Mapped[User] = relationship(back_populates="trades")
