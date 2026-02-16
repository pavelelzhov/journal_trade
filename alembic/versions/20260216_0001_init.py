"""init prod v1 schema"""

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
        sa.Column("tg_user_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("role", sa.Enum("admin", "trader", name="userrole"), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
    )
    op.create_index("ix_users_tg_user_id", "users", ["tg_user_id"])

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trader_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", sa.Enum("long", "short", name="tradeside"), nullable=False),
        sa.Column("entry_price", sa.Float(), nullable=False),
        sa.Column("size_pct", sa.Float(), nullable=False),
        sa.Column("leverage", sa.Float(), nullable=False),
        sa.Column("sl", sa.Float(), nullable=True),
        sa.Column("tp1", sa.Float(), nullable=True),
        sa.Column("tp2", sa.Float(), nullable=True),
        sa.Column("tp3", sa.Float(), nullable=True),
        sa.Column("status", sa.Enum("open", "closed", "draft", name="tradestatus"), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("parsed_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_trades_trader_id", "trades", ["trader_id"])
    op.create_index("ix_trades_symbol", "trades", ["symbol"])
    op.create_index("ix_trades_created_at", "trades", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_trades_created_at", table_name="trades")
    op.drop_index("ix_trades_symbol", table_name="trades")
    op.drop_index("ix_trades_trader_id", table_name="trades")
    op.drop_table("trades")

    op.drop_index("ix_users_tg_user_id", table_name="users")
    op.drop_table("users")

    sa.Enum(name="tradestatus").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="tradeside").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=False)
