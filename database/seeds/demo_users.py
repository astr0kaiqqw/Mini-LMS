"""Run from repository root: PYTHONPATH=backend python database/seeds/demo_users.py"""
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.db import SessionLocal
from app.models import Role, User, UserProfile

def seed(session):
    for name in ("student", "teacher", "admin"):
        session.execute(insert(Role).values(name=name).on_conflict_do_nothing(index_elements=[Role.name]))
    for role, name in (("student", "Демо студент"), ("teacher", "Демо преподаватель"), ("admin", "Демо администратор")):
        role_id = session.scalar(select(Role.id).where(Role.name == role))
        email = f"{role}@example.test"
        session.execute(insert(User).values(email=email, display_name=name, role_id=role_id).on_conflict_do_nothing(index_elements=[User.email]))
        user_id = session.scalar(select(User.id).where(User.email == email))
        session.execute(insert(UserProfile).values(user_id=user_id, bio="Демонстрационная запись").on_conflict_do_nothing(index_elements=[UserProfile.user_id]))

if __name__ == "__main__":
    with SessionLocal.begin() as session:
        seed(session)
    print("Демо-записи готовы. Паролей и входа в этом скелете нет.")
