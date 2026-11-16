"""Registration visibility, role selection and auth schema constraints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.main import app
from app.models import LoginAttempt, User
from app.learning import now
from test_learning import env, pytestmark  # noqa: F401


@pytest.mark.parametrize("role", ["student", "teacher"])
def test_registered_account_is_visible_and_searchable(env, role):
    s, login = env
    client = TestClient(app)
    email = f"new.{role}@example.test"
    body = {"email": email, "display_name": "Новый аккаунт", "password": "Secret123", "role": role}
    response = client.post("/api/auth/register", json=body)
    assert response.status_code == 201, response.text
    uid = response.json()["id"]
    assert s.get(User, uid).email == email
    admin = login("administrator@demo.example.test")
    assert uid in [u["id"] for u in admin.get("/api/admin/users").json()]
    found = admin.get("/api/admin/students", params={"q": email.upper()}).json()
    assert [u["id"] for u in found] == ([uid] if role == "student" else [])
    assert all(u["role"] == "student" for u in admin.get("/api/admin/students").json())
    assert all("password" not in u and "password_hash" not in u for u in found)
    assert client.post("/api/auth/login", json={"email": email, "password": "Secret123", "role": role}).status_code == 200
    other = "teacher" if role == "student" else "student"
    assert TestClient(app).post("/api/auth/login", json={"email": email, "password": "Secret123", "role": other}).status_code == 403
    assert login("instructor@demo.example.test").get("/api/admin/students").status_code == 403
    assert TestClient(app).get("/api/admin/students").status_code == 401


def test_failed_logins_are_counted_and_success_clears_counter(env):
    s, _ = env
    client = TestClient(app)
    email = "instructor@demo.example.test"
    for count in (1, 2):
        assert client.post("/api/auth/login", json={"email": email.upper(), "password": "wrong"}).status_code == 401
        s.expire_all()
        assert s.get(LoginAttempt, email).failed_count == count
    assert client.post("/api/auth/login", json={"email": email, "password": "LearnDemo2026!", "role": "teacher"}).status_code == 200
    s.expire_all()
    assert s.get(LoginAttempt, email) is None
    unknown = "unknown@example.test"
    assert client.post("/api/auth/login", json={"email": unknown, "password": "wrong"}).status_code == 401
    assert s.scalar(select(LoginAttempt).where(LoginAttempt.email == unknown)).failed_count == 1


def test_login_attempt_constraints(env):
    s, _ = env
    with pytest.raises(IntegrityError), s.begin_nested():
        s.add(LoginAttempt(email="negative@example.test", failed_count=-1, first_failed_at=now()))
        s.flush()
    s.add(LoginAttempt(email="duplicate@example.test", failed_count=0, first_failed_at=now()))
    s.flush()
    with pytest.raises(IntegrityError), s.begin_nested():
        s.add(LoginAttempt(email="duplicate@example.test", failed_count=1, first_failed_at=now()))
        s.flush()
    with pytest.raises(IntegrityError), s.begin_nested():
        s.add(LoginAttempt(email="UPPER@example.test", failed_count=0, first_failed_at=now()))
        s.flush()
