"""Idempotent content seed; run from repository root with PYTHONPATH=backend."""
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.db import SessionLocal
from app.models import Course, Module, Lesson, User
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("demo_users", Path(__file__).with_name("demo_users.py"))
users_seed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(users_seed)
seed_users = users_seed.seed


def seed(session):
    seed_users(session)
    teacher_id = session.scalar(select(User.id).where(User.email == "teacher@example.test"))
    session.execute(insert(Course).values(
        slug="data-thinking", title="Данные вокруг нас", description="Учимся моделировать данные и проверять связи.",
        teacher_id=teacher_id, status="published",
    ).on_conflict_do_nothing(index_elements=[Course.slug]))
    course_id = session.scalar(select(Course.id).where(Course.slug == "data-thinking"))
    session.execute(insert(Module).values(course_id=course_id, title="Основы данных", position=1)
                    .on_conflict_do_nothing(index_elements=[Module.course_id, Module.position]))
    module_id = session.scalar(select(Module.id).where(Module.course_id == course_id, Module.position == 1))
    for position, title, content in (
        (1, "Зачем нам данные", "Данные описывают пользователей, курсы и связи между ними."),
        (2, "Сущности и связи", "Курс содержит модули, а каждый модуль содержит уроки."),
    ):
        session.execute(insert(Lesson).values(module_id=module_id, title=title, content=content, position=position)
                        .on_conflict_do_nothing(index_elements=[Lesson.module_id, Lesson.position]))


if __name__ == "__main__":
    with SessionLocal.begin() as session:
        seed(session)
    print("Демо-содержание готово: курс, модуль и два урока. Существующие записи не перезаписаны.")
