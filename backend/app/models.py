from datetime import datetime
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint(
            "name IN ('student', 'teacher', 'admin')", name="ck_roles_name"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint(
            "email = lower(email) AND position('@' in email) > 1", name="ck_users_email"
        ),
        CheckConstraint("length(trim(display_name)) > 0", name="ck_users_display_name"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254))
    display_name: Mapped[str] = mapped_column(String(100))
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="RESTRICT"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    bio: Mapped[str] = mapped_column(String(500), default="", server_default="")


# TODO: Add quizzes, questions, options, attempts and answers when their contract is agreed.
# TODO: Add assignment submissions and measure query performance.


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="ck_courses_title"),
        CheckConstraint("length(trim(slug)) > 0", name="ck_courses_slug"),
        CheckConstraint("status IN ('draft', 'published')", name="ck_courses_status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(5000), server_default="")
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), server_default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Module(Base):
    __tablename__ = "modules"
    __table_args__ = (
        UniqueConstraint("course_id", "position", name="uq_modules_course_position"),
        CheckConstraint("position > 0", name="ck_modules_position"),
        CheckConstraint("length(trim(title)) > 0", name="ck_modules_title"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column()


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("module_id", "position", name="uq_lessons_module_position"),
        CheckConstraint("position > 0", name="ck_lessons_position"),
        CheckConstraint("duration_minutes > 0", name="ck_lessons_duration"),
        CheckConstraint(
            "(video_url IS NULL AND video_duration IS NULL) OR (video_url IS NOT NULL AND video_duration IS NOT NULL AND video_duration > 0)",
            name="ck_lessons_video",
        ),
        CheckConstraint("length(trim(title)) > 0", name="ck_lessons_title"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(20000), server_default="")
    position: Mapped[int] = mapped_column()
    summary: Mapped[str] = mapped_column(String(1000), server_default="")
    practice: Mapped[str] = mapped_column(String(3000), server_default="")
    duration_minutes: Mapped[int] = mapped_column(server_default="15")
    video_url: Mapped[str | None] = mapped_column(String(2000))
    video_duration: Mapped[int | None] = mapped_column()


# Learning and authentication records. Application roles never come from the client.
from sqlalchemy import Boolean, Integer, Float, JSON, Index, text


class Credential(Base):
    __tablename__ = "credentials"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    password_hash: Mapped[str] = mapped_column(String(300))


class LoginSession(Base):
    __tablename__ = "login_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Enrollment(Base):
    __tablename__ = "enrollments"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        CheckConstraint("watched_seconds >= 0", name="ck_progress_watched"),
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    completed: Mapped[bool] = mapped_column(Boolean, server_default="false")
    intervals: Mapped[list] = mapped_column(JSON, server_default="[]")
    watched_seconds: Mapped[float] = mapped_column(Float, server_default="0")
    demo: Mapped[bool] = mapped_column(Boolean, server_default="false")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_grades_score"),
        CheckConstraint(
            "kind IN ('lesson', 'practice', 'course')", name="ck_grades_kind"
        ),
        CheckConstraint(
            "(kind = 'course' AND lesson_id IS NULL) OR (kind != 'course' AND lesson_id IS NOT NULL)",
            name="ck_grades_target",
        ),
        Index(
            "uq_grade_lesson",
            "user_id",
            "course_id",
            "lesson_id",
            "kind",
            unique=True,
            postgresql_where=text("lesson_id IS NOT NULL"),
        ),
        Index(
            "uq_grade_course",
            "user_id",
            "course_id",
            unique=True,
            postgresql_where=text("lesson_id IS NULL"),
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE")
    )
    kind: Mapped[str] = mapped_column(String(20))
    score: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(String(2000), server_default="")
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    demo: Mapped[bool] = mapped_column(Boolean, server_default="false")


class CourseTeacher(Base):
    __tablename__ = "course_teachers"
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True
    )
