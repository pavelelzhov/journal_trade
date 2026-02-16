"""init schema"""

from alembic import op
import sqlalchemy as sa


revision = "20260216_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_user_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("role", sa.Enum("ADMIN", "TRADER", name="userrole"), nullable=False),
    )
    op.create_index("ix_users_telegram_user_id", "users", ["telegram_user_id"])

    op.create_table(
        "traders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
    )
    op.create_index("ix_traders_user_id", "traders", ["user_id"])

    op.create_table(
        "raw_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trader_id", sa.Integer(), sa.ForeignKey("traders.id"), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_raw_messages_trader_id", "raw_messages", ["trader_id"])
    op.create_index("ix_raw_messages_chat_id", "raw_messages", ["chat_id"])
    op.create_index("ix_raw_messages_message_id", "raw_messages", ["message_id"])

    op.create_table(
        "parsed_signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("raw_message_id", sa.Integer(), sa.ForeignKey("raw_messages.id"), nullable=False),
        sa.Column("status", sa.Enum("READY", "DRAFT", "REJECT", name="signalstatus"), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("errors_json", sa.JSON(), nullable=False),
        sa.Column("warnings_json", sa.JSON(), nullable=False),
        sa.Column("parser_version", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_parsed_signals_raw_message_id", "parsed_signals", ["raw_message_id"])

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trader_id", sa.Integer(), sa.ForeignKey("traders.id"), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("entries_json", sa.JSON(), nullable=False),
        sa.Column("sl", sa.Float(), nullable=True),
        sa.Column("tps_json", sa.JSON(), nullable=False),
        sa.Column("position_pct", sa.Float(), nullable=True),
        sa.Column("status", sa.Enum("OPEN", "CLOSED", "DRAFT", name="tradestatus"), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_trades_trader_id", "trades", ["trader_id"])
    op.create_index("ix_trades_symbol", "trades", ["symbol"])


def downgrade() -> None:
    op.drop_index("ix_trades_symbol", table_name="trades")
    op.drop_index("ix_trades_trader_id", table_name="trades")
    op.drop_table("trades")

    op.drop_index("ix_parsed_signals_raw_message_id", table_name="parsed_signals")
    op.drop_table("parsed_signals")

    op.drop_index("ix_raw_messages_message_id", table_name="raw_messages")
    op.drop_index("ix_raw_messages_chat_id", table_name="raw_messages")
    op.drop_index("ix_raw_messages_trader_id", table_name="raw_messages")
    op.drop_table("raw_messages")

    op.drop_index("ix_traders_user_id", table_name="traders")
    op.drop_table("traders")

    op.drop_index("ix_users_telegram_user_id", table_name="users")
    op.drop_table("users")

    sa.Enum(name="tradestatus").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="signalstatus").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=False)
