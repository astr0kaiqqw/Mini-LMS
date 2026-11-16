"""Failed login attempts and expiry index; user_id index exists since 0003."""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "login_attempts",
        sa.Column("email", sa.String(254), primary_key=True),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("first_failed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("email = lower(email)", name="ck_login_attempts_email"),
        sa.CheckConstraint("failed_count >= 0", name="ck_login_attempts_failed_count"),
    )
    op.create_index("ix_login_sessions_expires_at", "login_sessions", ["expires_at"])


def downgrade():
    op.drop_index("ix_login_sessions_expires_at", table_name="login_sessions")
    op.drop_table("login_attempts")
