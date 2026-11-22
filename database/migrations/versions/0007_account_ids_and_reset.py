"""Assign public account IDs and store expiring password reset tokens."""

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("account_id", sa.String(12)))
    op.execute("CREATE SEQUENCE user_account_id_seq MAXVALUE 9999999")
    op.execute("""
        CREATE FUNCTION next_user_account_id(registered_at timestamptz)
        RETURNS text LANGUAGE sql VOLATILE AS $$
            SELECT to_char(registered_at AT TIME ZONE 'Asia/Almaty', 'YY')
                || lpad(floor(random() * 1000)::integer::text, 3, '0')
                || lpad(nextval('user_account_id_seq')::text, 7, '0')
        $$
    """)
    op.execute("UPDATE users SET account_id = next_user_account_id(created_at)")
    op.execute("""
        CREATE FUNCTION assign_user_account_id() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            NEW.account_id := next_user_account_id(NEW.created_at);
            RETURN NEW;
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER assign_user_account_id BEFORE INSERT ON users
        FOR EACH ROW EXECUTE FUNCTION assign_user_account_id()
    """)
    op.alter_column("users", "account_id", nullable=False)
    op.create_unique_constraint("uq_users_account_id", "users", ["account_id"])
    op.create_table(
        "password_resets",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("password_resets")
    op.execute("DROP TRIGGER assign_user_account_id ON users")
    op.execute("DROP FUNCTION assign_user_account_id()")
    op.execute("DROP FUNCTION next_user_account_id(timestamptz)")
    op.execute("DROP SEQUENCE user_account_id_seq")
    op.drop_column("users", "account_id")
