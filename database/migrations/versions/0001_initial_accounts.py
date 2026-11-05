"""Initial accounts only; no learning tables yet."""
from alembic import op
import sqlalchemy as sa
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("roles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(30), nullable=False, unique=True), sa.CheckConstraint("name IN ('student', 'teacher', 'admin')", name="ck_roles_name"))
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint("email = lower(email) AND position('@' in email) > 1", name="ck_users_email"),
        sa.CheckConstraint("length(trim(display_name)) > 0", name="ck_users_display_name"))
    op.create_index("ix_users_role_id", "users", ["role_id"])
    op.create_table("user_profiles", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("bio", sa.String(500), nullable=False, server_default=""))

def downgrade():
    op.drop_table("user_profiles")
    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_table("users")
    op.drop_table("roles")
