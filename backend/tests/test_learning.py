"""Integration tests: real PostgreSQL with an outer rollback, actual cookie login."""

import importlib.util
import os
from pathlib import Path
import sys
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from app.main import app
from app.learning import db, merge_intervals
from app.models import (
    User,
    Role,
    Course,
    Module,
    Lesson,
    Enrollment,
    LessonProgress,
    Grade,
    Credential,
)
from app.security import hash_password, verify_password

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DB_TESTS") != "1", reason="Requires isolated PostgreSQL"
)


def seed_module():
    path = Path(__file__).resolve().parents[2] / "database/seeds"
    sys.path.insert(0, str(path))
    import learning_demo

    return learning_demo


@pytest.fixture
def env():
    url = os.environ.get("DATABASE_URL", "")
    if not (make_url(url).database or "").startswith("mini_lms_test_"):
        pytest.fail("Only mini_lms_test_* databases allowed")
    engine = create_engine(url)
    with engine.connect() as conn:
        tx = conn.begin()
        with Session(bind=conn, join_transaction_mode="create_savepoint") as s:
            seed_module().seed(s)
            s.flush()

            def override():
                try:
                    yield s
                    s.flush()
                except Exception:
                    raise

            app.dependency_overrides[db] = override
            clients = []

            def login(email):
                client = TestClient(app)
                clients.append(client)
                response = client.post(
                    "/api/auth/login",
                    json={"email": email, "password": "LearnDemo2026!"},
                )
                assert response.status_code == 200, response.text
                return client

            try:
                yield s, login
            finally:
                app.dependency_overrides.clear()
                for c in clients:
                    c.close()
        tx.rollback()
    engine.dispose()


def course(s, slug="calculus-1"):
    return s.scalar(select(Course).where(Course.slug == slug))


def test_seed_counts_idempotence_and_preservation(env):
    s, _ = env
    models = (
        User,
        Course,
        Module,
        Lesson,
        Enrollment,
        LessonProgress,
        Grade,
        Credential,
    )
    before = [s.scalar(select(func.count()).select_from(m)) for m in models]
    u = s.scalar(
        select(User).where(User.email == "calculus-1.student1@demo.example.test")
    )
    cred = s.get(Credential, u.id)
    cred.password_hash = hash_password("OriginalPass!")
    c = course(s)
    c.description = "Preserved description"
    seed_module().seed(s)
    assert before == [s.scalar(select(func.count()).select_from(m)) for m in models]
    assert verify_password("OriginalPass!", s.get(Credential, u.id).password_hash)
    assert c.description == "Preserved description"
    for slug in seed_module().COURSES:
        c = course(s, slug)
        lessons = s.scalars(
            select(Lesson).join(Module).where(Module.course_id == c.id)
        ).all()
        assert len(lessons) == 10
        assert all(
            l.title
            and l.summary
            and l.content
            and l.practice
            and l.duration_minutes > 0
            for l in lessons
        )
        assert (
            s.scalar(
                select(func.count())
                .select_from(Enrollment)
                .where(Enrollment.course_id == c.id)
            )
            == 3
        )
    assert (
        s.scalar(
            select(func.count())
            .select_from(User)
            .where(User.email.like("%.student%@demo.example.test"))
        )
        == 36
    )


def test_student_isolation_and_role_protection(env):
    s, login = env
    client = login("calculus-1.student1@demo.example.test")
    c = course(s)
    assert len(client.get("/api/me/courses").json()) == 1
    assert client.get("/api/courses/" + str(c.id)).status_code == 200
    assert client.get("/api/courses/" + str(course(s, "english").id)).status_code == 403
    for path in ("/api/staff/courses", "/api/staff/students", "/api/admin/users"):
        assert client.get(path).status_code == 403
    assert (
        client.patch(
            "/api/me", json={"display_name": "Changed", "bio": "Bio", "role": "admin"}
        ).status_code
        == 422
    )
    assert (
        client.patch(
            "/api/me", json={"display_name": "Changed", "bio": "Bio"}
        ).status_code
        == 200
    )
    assert client.get("/api/me").json()["role"] == "student"
    assert (
        client.post(
            "/api/staff/courses", json={"slug": "hacked", "title": "Hacked"}
        ).status_code
        == 403
    )
    assert client.delete("/api/staff/courses/" + str(c.id)).status_code == 403
    assert (
        client.put(
            f"/api/staff/courses/{c.id}/grades",
            json={"user_id": 1, "kind": "course", "score": 100},
        ).status_code
        == 403
    )


def test_teacher_student_filter_and_other_teacher_denied(env):
    s, login = env
    t = login("instructor@demo.example.test")
    c = course(s)
    assert len(t.get("/api/staff/students").json()) == 36
    assert len(t.get("/api/staff/students", params={"course_id": c.id}).json()) == 3
    assert t.get("/api/staff/students?q=doesnotexist").json() == []
    uid = s.scalar(
        select(User.id).where(User.email == "english.student1@demo.example.test")
    )
    assert t.get(f"/api/staff/courses/{c.id}/students/{uid}").status_code == 404
    role = s.scalar(select(Role).where(Role.name == "teacher"))
    stranger = User(
        email=f"{uuid.uuid4()}@example.test",
        display_name="Other teacher",
        role_id=role.id,
    )
    s.add(stranger)
    s.flush()
    s.add(
        Credential(user_id=stranger.id, password_hash=hash_password("LearnDemo2026!"))
    )
    s.flush()
    other = login(stranger.email)
    assert other.get("/api/staff/students").json() == []
    assert other.get(f"/api/staff/students?course_id={c.id}").status_code == 403
    assert other.get(f"/api/staff/courses/{c.id}/students/{uid}").status_code == 403
    assert (
        other.put(
            f"/api/staff/courses/{c.id}", json={"slug": "stolen", "title": "Stolen"}
        ).status_code
        == 403
    )


def test_grades_zero_update_and_private_read(env):
    s, login = env
    t = login("instructor@demo.example.test")
    student = login("calculus-1.student1@demo.example.test")
    other = login("calculus-1.student2@demo.example.test")
    c = course(s)
    uid = student.get("/api/me").json()["id"]
    payload = {"user_id": uid, "kind": "course", "score": 0, "comment": "First"}
    a = t.put(f"/api/staff/courses/{c.id}/grades", json=payload)
    assert a.status_code == 200, a.text
    assert student.get("/api/me/grades").json()[0]["score"] == 0
    payload.update(score=85, comment="Updated")
    b = t.put(f"/api/staff/courses/{c.id}/grades", json=payload)
    assert b.json()["id"] == a.json()["id"]
    assert b.json()["comment"] == "Updated" and b.json()["author"] == "Алия Нурланова"
    assert all(g["user_id"] != uid for g in other.get("/api/me/grades").json())
    for score in (-1, 101, 90.5):
        assert (
            t.put(
                f"/api/staff/courses/{c.id}/grades", json={**payload, "score": score}
            ).status_code
            == 422
        )
    foreign_lesson = s.scalar(
        select(Lesson).join(Module).where(Module.course_id == course(s, "english").id)
    )
    assert (
        t.put(
            f"/api/staff/courses/{c.id}/grades",
            json={**payload, "kind": "lesson", "lesson_id": foreign_lesson.id},
        ).status_code
        == 422
    )


def test_completion_survives_new_login_and_is_private(env):
    s, login = env
    a = login("calculus-1.student1@demo.example.test")
    b = login("calculus-1.student2@demo.example.test")
    c = course(s)
    lessons = a.get(f"/api/courses/{c.id}").json()["items"]
    lid = lessons[-1]["id"]
    assert a.post(f"/api/lessons/{lid}/complete").status_code == 200
    a.post("/api/auth/logout")
    assert a.get("/api/me").status_code == 401
    a = login("calculus-1.student1@demo.example.test")
    assert a.get(f"/api/lessons/{lid}").json()["completed"] is True
    assert b.get(f"/api/lessons/{lid}").json()["completed"] is False
    assert a.get("/api/me/courses").json()[0]["progress"]["percent"] == 20


def test_video_unique_ranges_and_threshold(env):
    s, login = env
    a = login("calculus-1.student1@demo.example.test")
    c = course(s)
    l = s.scalar(
        select(Lesson)
        .join(Module)
        .where(Module.course_id == c.id)
        .order_by(Lesson.id.desc())
    )
    l.video_url = "http://127.0.0.1:8000/test.mp4"
    l.video_duration = 100
    s.flush()
    assert a.post(f"/api/lessons/{l.id}/complete").status_code == 422

    def report(start, end):
        return a.post(f"/api/lessons/{l.id}/watch", json={"start": start, "end": end})

    assert report(0, 100).status_code == 422
    assert report(90, 100).json()["video_percent"] == 10
    assert report(90, 100).json()["video_percent"] == 10
    assert report(85, 95).json()["video_percent"] == 15
    assert report(0, 10).json()["completed"] is False
    for start in range(10, 80, 10):
        report(start, start + 10)
    final = report(80, 90).json()
    assert final["completed"] is True and final["video_percent"] == 100
    assert merge_intervals([[1, 3], [2, 4], [4, 5], [8, 9]]) == [[1, 5], [8, 9]]


def test_staff_crud_and_admin(env):
    s, login = env
    t = login("instructor@demo.example.test")
    admin = login("administrator@demo.example.test")
    c = t.post(
        "/api/staff/courses",
        json={"slug": "test-" + uuid.uuid4().hex, "title": "Test", "status": "draft"},
    ).json()
    assert all(x["id"] != c["id"] for x in t.get("/api/courses").json())
    m = t.post(
        f"/api/staff/courses/{c['id']}/modules",
        json={"title": "Section", "position": 1},
    ).json()
    l = t.post(
        f"/api/staff/modules/{m['id']}/lessons",
        json={"title": "Lesson", "position": 1, "content": "Body", "practice": "Task"},
    ).json()
    assert (
        t.put(
            f"/api/staff/lessons/{l['id']}", json={"title": "Updated", "position": 1}
        ).status_code
        == 200
    )
    assert t.get(f"/api/lessons/{l['id']}").json()["title"] == "Updated"
    assert t.delete(f"/api/staff/lessons/{l['id']}").status_code == 200
    assert t.delete(f"/api/staff/modules/{m['id']}").status_code == 200
    assert t.delete(f"/api/staff/courses/{c['id']}").status_code == 200
    assert admin.get("/api/admin/users").status_code == 200
    assert t.get("/api/admin/users").status_code == 403
    assert TestClient(app).get("/api/me").status_code == 401


def test_gradebook_and_expired_session(env):
    from datetime import timedelta
    from app.models import LoginSession
    from app.security import token_hash
    from app.learning import now

    s, login = env
    a = login("calculus-1.student1@demo.example.test")
    rows = a.get("/api/me/gradebook").json()
    assert len(rows) == 21 and all(g["score"] is None for g in rows)
    token = a.cookies.get("lms_session")
    record = s.get(LoginSession, token_hash(token))
    record.expires_at = now() - timedelta(seconds=1)
    s.flush()
    assert a.get("/api/me").status_code == 401


def test_lesson_permissions_and_video_constraint(env):
    from sqlalchemy.exc import IntegrityError

    s, login = env
    a = login("calculus-1.student1@demo.example.test")
    c = course(s)
    lesson = s.scalar(select(Lesson).join(Module).where(Module.course_id == c.id))
    assert (
        a.put(
            f"/api/staff/lessons/{lesson.id}", json={"title": "Wrong", "position": 1}
        ).status_code
        == 403
    )
    assert a.delete(f"/api/staff/lessons/{lesson.id}").status_code == 403
    assert (
        a.post(
            f"/api/staff/modules/{lesson.module_id}/lessons",
            json={"title": "Wrong", "position": 50},
        ).status_code
        == 403
    )
    assert a.delete(f"/api/staff/modules/{lesson.module_id}").status_code == 403
    foreign = s.scalar(
        select(Lesson).join(Module).where(Module.course_id == course(s, "english").id)
    )
    assert a.get(f"/api/lessons/{foreign.id}").status_code == 403
    assert a.post(f"/api/lessons/{foreign.id}/complete").status_code == 403
    with pytest.raises(IntegrityError):
        with s.begin_nested():
            s.add(
                Lesson(
                    module_id=lesson.module_id,
                    title="Broken video",
                    position=999,
                    video_url="https://example.test/video.mp4",
                )
            )
            s.flush()


def test_register_creates_student_session(env):
    s, _ = env
    client = TestClient(app)
    email = f"new-{uuid.uuid4().hex[:8]}@example.test"
    body = {"email": f" {email.upper()} ", "display_name": "Новый", "password": "Secret123"}
    r = client.post("/api/auth/register", json=body)
    assert r.status_code == 201, r.text
    assert r.json()["email"] == email and r.json()["role"] == "student"
    assert client.get("/api/me").json()["email"] == email
    assert TestClient(app).post("/api/auth/register", json=body).status_code == 409
    assert TestClient(app).post("/api/auth/login", json={"email": email, "password": "Secret123"}).status_code == 200
    bad = (
        {**body, "email": "x" + email, "password": "short"},
        {**body, "email": "no-at-sign"},
        {**body, "email": "y" + email, "role": "admin"},
    )
    for payload in bad:
        assert TestClient(app).post("/api/auth/register", json=payload).status_code == 422


def test_enroll_is_idempotent_and_opens_course(env):
    s, login = env
    client = login("calculus-1.student1@demo.example.test")
    english = course(s, "english")
    assert client.get(f"/api/courses/{english.id}").status_code == 403
    assert client.post(f"/api/courses/{english.id}/enroll").status_code == 200
    assert client.post(f"/api/courses/{english.id}/enroll").status_code == 200
    assert client.get(f"/api/courses/{english.id}").status_code == 200
    user_id = client.get("/api/me").json()["id"]
    count = select(func.count()).select_from(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == english.id)
    assert s.scalar(count) == 1
    assert client.post("/api/courses/999999/enroll").status_code == 404
    assert TestClient(app).post(f"/api/courses/{english.id}/enroll").status_code == 401


def test_admin_changes_roles_but_not_own(env):
    s, login = env
    admin = login("administrator@demo.example.test")
    student = login("calculus-1.student1@demo.example.test")
    sid, aid = student.get("/api/me").json()["id"], admin.get("/api/me").json()["id"]
    assert student.put(f"/api/admin/users/{sid}/role", json={"role": "admin"}).status_code == 403
    assert admin.put(f"/api/admin/users/{aid}/role", json={"role": "student"}).status_code == 403
    assert admin.put(f"/api/admin/users/{sid}/role", json={"role": "superuser"}).status_code == 422
    assert admin.put("/api/admin/users/999999/role", json={"role": "teacher"}).status_code == 404
    assert admin.put(f"/api/admin/users/{sid}/role", json={"role": "teacher"}).json()["role"] == "teacher"
    assert student.get("/api/staff/courses").status_code == 200
