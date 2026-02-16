from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TRADER = "TRADER"


class SignalStatus(str, Enum):
    READY = "READY"
    DRAFT = "DRAFT"
    REJECT = "REJECT"


class TradeStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.TRADER, nullable=False)

    trader: Mapped[Trader | None] = relationship(back_populates="user", uselist=False)


class Trader(Base):
    __tablename__ = "traders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)

    user: Mapped[User] = relationship(back_populates="trader")
    raw_messages: Mapped[list[RawMessage]] = relationship(back_populates="trader")
    trades: Mapped[list[Trade]] = relationship(back_populates="trader")


class RawMessage(Base):
    __tablename__ = "raw_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey("traders.id"), index=True)
    chat_id: Mapped[int] = mapped_column(Integer, index=True)
    message_id: Mapped[int] = mapped_column(Integer, index=True)
    text: Mapped[str] = mapped_column(Text)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    trader: Mapped[Trader] = relationship(back_populates="raw_messages")
    parsed_signals: Mapped[list[ParsedSignal]] = relationship(back_populates="raw_message")


class ParsedSignal(Base):
    __tablename__ = "parsed_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_message_id: Mapped[int] = mapped_column(ForeignKey("raw_messages.id"), index=True)
    status: Mapped[SignalStatus] = mapped_column(SAEnum(SignalStatus), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    errors_json: Mapped[list] = mapped_column(JSON, default=list)
    warnings_json: Mapped[list] = mapped_column(JSON, default=list)
    parser_version: Mapped[str] = mapped_column(String(32), default="v1", nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    raw_message: Mapped[RawMessage] = relationship(back_populates="parsed_signals")


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey("traders.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    side: Mapped[str] = mapped_column(String(16))
    entries_json: Mapped[list] = mapped_column(JSON, default=list)
    sl: Mapped[float | None] = mapped_column(Float)
    tps_json: Mapped[list] = mapped_column(JSON, default=list)
    position_pct: Mapped[float | None] = mapped_column(Float)
    status: Mapped[TradeStatus] = mapped_column(SAEnum(TradeStatus), default=TradeStatus.DRAFT, nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    trader: Mapped[Trader] = relationship(back_populates="trades")
