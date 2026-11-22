"""Replace pending email reset tokens with short admin-issued codes."""

from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM password_resets")
    op.alter_column("password_resets", "token_hash", new_column_name="code_hash", type_=sa.String(300))
    op.add_column("password_resets", sa.Column("failed_attempts", sa.Integer(), server_default="0", nullable=False))


def downgrade():
    op.execute("DELETE FROM password_resets")
    op.drop_column("password_resets", "failed_attempts")
    op.alter_column("password_resets", "code_hash", new_column_name="token_hash", type_=sa.String(64))
