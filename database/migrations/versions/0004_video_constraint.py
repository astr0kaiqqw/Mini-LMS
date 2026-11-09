"""Require both video URL and a non-null positive duration."""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("ck_lessons_video", "lessons")
    op.create_check_constraint(
        "ck_lessons_video",
        "lessons",
        "(video_url IS NULL AND video_duration IS NULL) OR "
        "(video_url IS NOT NULL AND video_duration IS NOT NULL AND video_duration > 0)",
    )


def downgrade():
    op.drop_constraint("ck_lessons_video", "lessons")
    op.create_check_constraint(
        "ck_lessons_video",
        "lessons",
        "(video_url IS NULL AND video_duration IS NULL) OR (video_url IS NOT NULL AND video_duration > 0)",
    )
