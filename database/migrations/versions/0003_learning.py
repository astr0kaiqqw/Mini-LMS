"""Authentication, enrollments, progress, grades and lesson details."""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    for column in (
        sa.Column("summary", sa.String(1000), nullable=False, server_default=""),
        sa.Column("practice", sa.String(3000), nullable=False, server_default=""),
        sa.Column(
            "duration_minutes", sa.Integer(), nullable=False, server_default="15"
        ),
        sa.Column("video_url", sa.String(2000)),
        sa.Column("video_duration", sa.Integer()),
    ):
        op.add_column("lessons", column)
    op.create_check_constraint("ck_lessons_duration", "lessons", "duration_minutes > 0")
    op.create_check_constraint(
        "ck_lessons_video",
        "lessons",
        "(video_url IS NULL AND video_duration IS NULL) OR (video_url IS NOT NULL AND video_duration > 0)",
    )
    op.create_table(
        "course_teachers",
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_index("ix_course_teachers_user_id", "course_teachers", ["user_id"])
    op.create_table(
        "credentials",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("password_hash", sa.String(300), nullable=False),
    )
    op.create_table(
        "login_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_login_sessions_user_id", "login_sessions", ["user_id"])
    op.create_table(
        "enrollments",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"])
    op.create_table(
        "lesson_progress",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "lesson_id",
            sa.Integer(),
            sa.ForeignKey("lessons.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("intervals", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("watched_seconds", sa.Float(), nullable=False, server_default="0"),
        sa.Column("demo", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("watched_seconds >= 0", name="ck_progress_watched"),
    )
    op.create_index("ix_lesson_progress_lesson_id", "lesson_progress", ["lesson_id"])
    op.create_table(
        "grades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "lesson_id", sa.Integer(), sa.ForeignKey("lessons.id", ondelete="CASCADE")
        ),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(2000), nullable=False, server_default=""),
        sa.Column(
            "author_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("demo", sa.Boolean(), nullable=False, server_default="false"),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_grades_score"),
        sa.CheckConstraint(
            "kind IN ('lesson', 'practice', 'course')", name="ck_grades_kind"
        ),
        sa.CheckConstraint(
            "(kind = 'course' AND lesson_id IS NULL) OR (kind != 'course' AND lesson_id IS NOT NULL)",
            name="ck_grades_target",
        ),
    )
    op.create_index("ix_grades_user_id", "grades", ["user_id"])
    op.create_index("ix_grades_course_id", "grades", ["course_id"])
    op.create_index(
        "uq_grade_lesson",
        "grades",
        ["user_id", "course_id", "lesson_id", "kind"],
        unique=True,
        postgresql_where=sa.text("lesson_id IS NOT NULL"),
    )
    op.create_index(
        "uq_grade_course",
        "grades",
        ["user_id", "course_id"],
        unique=True,
        postgresql_where=sa.text("lesson_id IS NULL"),
    )


def downgrade():
    for table in (
        "grades",
        "lesson_progress",
        "enrollments",
        "login_sessions",
        "credentials",
        "course_teachers",
    ):
        op.drop_table(table)
    op.drop_constraint("ck_lessons_video", "lessons")
    op.drop_constraint("ck_lessons_duration", "lessons")
    for column in (
        "video_duration",
        "video_url",
        "duration_minutes",
        "practice",
        "summary",
    ):
        op.drop_column("lessons", column)
