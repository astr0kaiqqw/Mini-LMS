"""Run: PYTHONPATH=backend .venv/bin/python database/seeds/learning_demo.py"""

from datetime import datetime, timedelta, timezone
import random
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from app.db import SessionLocal
from app.models import (
    Role,
    User,
    UserProfile,
    Credential,
    Course,
    Module,
    Lesson,
    Enrollment,
    LessonProgress,
    Grade,
    CourseTeacher,
)
from app.security import hash_password
from curriculum import COURSES, lessons_for

PASSWORD = "LearnDemo2026!"
FIRST = [
    "Алина",
    "Данияр",
    "Мария",
    "Тимур",
    "София",
    "Арман",
    "Айша",
    "Дамир",
    "Анна",
    "Никита",
    "Диана",
    "Артём",
]
LAST = [
    "Садыкова",
    "Ибраев",
    "Ким",
    "Сериков",
    "Иванова",
    "Ахметов",
    "Омарова",
    "Беков",
    "Петрова",
    "Соколов",
    "Ли",
    "Волков",
]


def seed(s):
    for name in ("student", "teacher", "admin"):
        s.execute(insert(Role).values(name=name).on_conflict_do_nothing())
    roles = dict(s.execute(select(Role.name, Role.id)).all())

    # Credential insertion happens ONLY when this seed creates the user.
    # Existing accounts without passwords are deliberately left untouched.
    def account(email, name, user_role):
        uid = s.scalar(
            insert(User)
            .values(email=email, display_name=name, role_id=roles[user_role])
            .on_conflict_do_nothing()
            .returning(User.id)
        )
        if uid:
            s.add(Credential(user_id=uid, password_hash=hash_password(PASSWORD)))
            s.add(UserProfile(user_id=uid, bio="Учебная тестовая запись"))
            s.flush()
        else:
            uid = s.scalar(select(User.id).where(User.email == email))
            if s.get(User, uid).role_id != roles[user_role]:
                raise ValueError(f"Seed email collision with another role: {email}")
        return uid

    # Demo accounts share a published password but receive independent random salts.
    teacher_id = account("instructor@demo.example.test", "Алия Нурланова", "teacher")
    account("administrator@demo.example.test", "Администратор демо", "admin")
    rng = random.Random(2026)
    names = [(FIRST[i % 12], LAST[(i % 12 + 2 * (i // 12)) % 12]) for i in range(36)]
    rng.shuffle(names)
    for course_index, (slug, (title, _)) in enumerate(COURSES.items()):
        c = s.scalar(select(Course).where(Course.slug == slug))
        if not c:
            c = Course(
                slug=slug,
                title=title,
                description=f"Вводный курс {title}: объяснения, примеры и небольшие практические задания.",
                teacher_id=teacher_id,
                status="published",
            )
            s.add(c)
            s.flush()
        # Do not take courses away from existing teachers. For an existing course,
        # grading belongs to its current owner; the seed warns rather than overwrites.
        if c.teacher_id != teacher_id:
            print(f"Сохранён автор курса {slug}: user_id={c.teacher_id}")
        s.execute(
            insert(CourseTeacher)
            .values(course_id=c.id, user_id=teacher_id)
            .on_conflict_do_nothing()
        )
        existing = s.scalars(
            select(Lesson)
            .join(Module)
            .where(Module.course_id == c.id)
            .order_by(Module.position, Lesson.position)
        ).all()
        module = s.scalar(
            select(Module).where(Module.course_id == c.id).order_by(Module.position)
        )
        if not module:
            module = Module(course_id=c.id, title="Базовый маршрут", position=1)
            s.add(module)
            s.flush()
        topics = lessons_for(slug)
        # Preserve useful existing lessons; add only the missing count up to ten.
        titles = {l.title for l in existing}
        for data in topics:
            if len(existing) >= 10:
                break
            if data["title"] in titles:
                continue
            position = (
                s.scalar(
                    select(func.max(Lesson.position)).where(
                        Lesson.module_id == module.id
                    )
                )
                or 0
            ) + 1
            l = Lesson(module_id=module.id, position=position, **data)
            s.add(l)
            s.flush()
            existing.append(l)
            titles.add(l.title)
        for lesson in existing:
            if not lesson.summary:
                lesson.summary = (
                    lesson.content[:250] or f"Введение в тему «{lesson.title}»."
                )
            if not lesson.practice:
                lesson.practice = f"Повтори пример из урока «{lesson.title}» и объясни результат своими словами."
        for student_index in range(3):
            first, last = names[course_index * 3 + student_index]
            uid = account(
                f"{slug}.student{student_index+1}@demo.example.test",
                f"{first} {last}",
                "student",
            )
            s.execute(
                insert(Enrollment)
                .values(user_id=uid, course_id=c.id)
                .on_conflict_do_nothing()
            )
            # Fixed timestamps keep reruns stable; these are explicitly simulated records.
            stamp = datetime(2026, 11, 9, 5, tzinfo=timezone.utc) - timedelta(
                days=student_index
            )
            completed = (1, 5, 9)[student_index]
            for l in existing[:completed]:
                s.execute(
                    insert(LessonProgress)
                    .values(
                        user_id=uid,
                        lesson_id=l.id,
                        completed=True,
                        demo=True,
                        updated_at=stamp,
                    )
                    .on_conflict_do_nothing()
                )
            if student_index > 0:
                s.execute(
                    insert(Grade)
                    .values(
                        user_id=uid,
                        course_id=c.id,
                        lesson_id=existing[0].id,
                        kind="practice",
                        score=(0 if student_index == 1 else 92),
                        comment="Демонстрационная оценка для проверки интерфейса.",
                        author_id=teacher_id,
                        demo=True,
                        updated_at=stamp,
                    )
                    .on_conflict_do_nothing()
                )
    s.flush()


if __name__ == "__main__":
    with SessionLocal.begin() as session:
        seed(session)
    print(
        "Готово: 12 учебных курсов, по 10 уроков и 3 ученика. Исходные записи сохранены."
    )
    print("Преподаватель: instructor@demo.example.test; пароль: " + PASSWORD)
