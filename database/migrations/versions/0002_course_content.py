"""Add courses, modules and lessons."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(5000), nullable=False, server_default=""),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_courses_title"),
        sa.CheckConstraint("length(trim(slug)) > 0", name="ck_courses_slug"),
        sa.CheckConstraint("status IN ('draft', 'published')", name="ck_courses_status"),
    )
    op.create_index("ix_courses_teacher_id", "courses", ["teacher_id"])
    op.create_table(
        "modules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("course_id", "position", name="uq_modules_course_position"),
        sa.CheckConstraint("position > 0", name="ck_modules_position"),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_modules_title"),
    )
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.String(20000), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("module_id", "position", name="uq_lessons_module_position"),
        sa.CheckConstraint("position > 0", name="ck_lessons_position"),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_lessons_title"),
    )


def downgrade():
    op.drop_table("lessons")
    op.drop_table("modules")
    op.drop_index("ix_courses_teacher_id", table_name="courses")
    op.drop_table("courses")
