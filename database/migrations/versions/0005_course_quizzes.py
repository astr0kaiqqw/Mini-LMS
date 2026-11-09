"""Final course questions and persistent attempts."""
from alembic import op
import sqlalchemy as sa
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("quiz_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("prompt", sa.String(3000), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("correct_index", sa.Integer(), nullable=False),
        sa.Column("explanation", sa.String(20000), nullable=False),
        sa.CheckConstraint("length(trim(prompt)) > 0", name="ck_quiz_prompt"),
        sa.CheckConstraint("json_array_length(options) = 4", name="ck_quiz_options"),
        sa.CheckConstraint("correct_index BETWEEN 0 AND 3", name="ck_quiz_correct"))
    op.create_table("quiz_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("total > 0 AND correct >= 0 AND correct <= total", name="ck_quiz_attempt_score"))
    op.create_index("ix_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    op.create_index("ix_quiz_attempts_course_id", "quiz_attempts", ["course_id"])


def downgrade():
    op.drop_table("quiz_attempts")
    op.drop_table("quiz_questions")
