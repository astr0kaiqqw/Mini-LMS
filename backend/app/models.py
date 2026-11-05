from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (CheckConstraint("name IN ('student', 'teacher', 'admin')", name="ck_roles_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint("email = lower(email) AND position('@' in email) > 1", name="ck_users_email"),
        CheckConstraint("length(trim(display_name)) > 0", name="ck_users_display_name"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254))
    display_name: Mapped[str] = mapped_column(String(100))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # TODO(W12, Ануар): AUTH-01 — добавить вход и хеширование пароля после миграции Руслана.

class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    bio: Mapped[str] = mapped_column(String(500), default="", server_default="")

# TODO(W12, Руслан): DB-02 — добавить courses, modules, lessons и миграцию учётных данных.
# TODO(W13, Руслан): DB-03 — добавить enrollments, quizzes, questions, options, attempts, answers.
# TODO(W14, Руслан): DB-04 — добавить assignments, submissions, grades и измерить запросы на тестовых данных.
