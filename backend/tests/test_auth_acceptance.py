"""Acceptance scenarios for authentication and authorization (testing/AUTH_ACCEPTANCE.md).

Test names carry scenario IDs. xfail(strict=True) marks a confirmed gap: the test
states the agreed requirement and starts failing once the gap is closed, so the
marker must then be removed by whoever closes it.
"""
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from app.learning import lessons_for, now
from app.main import app
from app.models import LoginSession, Module, User
from test_learning import env, course, pytestmark  # noqa: F401  (fixture + DB skip marker)

PW = "LearnDemo2026!"
STUDENT = "calculus-1.student1@demo.example.test"
OTHER = "english.student1@demo.example.test"
TEACHER = "instructor@demo.example.test"
ADMIN = "administrator@demo.example.test"


def raw_login(email, password=PW):
    client = TestClient(app)
    return client, client.post("/api/auth/login", json={"email": email, "password": password})


def register(email, password="longpass1", name="Новый ученик", **extra):
    client = TestClient(app)
    body = {"email": email, "password": password, "display_name": name, **extra}
    return client, client.post("/api/auth/register", json=body)


def sessions_of(s, uid, expired_only=False):
    q = select(func.count()).select_from(LoginSession).where(LoginSession.user_id == uid)
    if expired_only:
        q = q.where(LoginSession.expires_at <= now())
    return s.scalar(q)


# ---------- Login

def test_au01_wrong_password_and_unknown_email_look_the_same(env):
    _, wrong = raw_login(STUDENT, "wrong-password")
    _, unknown = raw_login("nobody@demo.example.test")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_au02_login_email_is_case_and_space_insensitive(env):
    _, r = raw_login("  CALCULUS-1.Student1@demo.example.test ")
    assert r.status_code == 200


def test_au03_account_without_password_cannot_login(env):
    _, r = raw_login("student@example.test")
    assert r.status_code == 401


def test_au04_session_cookie_is_protected_and_no_secrets_returned(env):
    _, r = raw_login(STUDENT)
    cookie = r.headers["set-cookie"].lower()
    assert "lms_session=" in cookie and "httponly" in cookie
    assert "samesite=strict" in cookie and "max-age=604800" in cookie
    assert not any(word in r.text.lower() for word in ("password", "hash", "token"))


# ---------- Registration

def test_au05_registration_creates_logged_in_student(env):
    client, r = register(" New.User@Demo.Example.Test ", name="  Новый  ")
    assert r.status_code == 201, r.text
    body = r.json()
    assert (body["role"], body["email"], body["display_name"]) == ("student", "new.user@demo.example.test", "Новый")
    assert client.get("/api/me").status_code == 200


def test_au06_duplicate_email_rejected_case_insensitively(env):
    register("dup@demo.example.test")
    _, r = register("DUP@demo.example.test")
    assert r.status_code == 409


@pytest.mark.parametrize("case, body", [
    ("short_password", dict(password="1234567")),
    ("bad_email", dict(email="not-an-email")),
    ("blank_name", dict(name="   ")),
    ("role_escalation", dict(role="admin")),
])
def test_au07_invalid_registration_rejected(env, case, body):
    email = body.pop("email", f"{case}@demo.example.test")
    _, r = register(email, **body)
    assert r.status_code == 422


def test_au08_profile_cannot_change_role_or_email(env):
    client, _ = raw_login(STUDENT)
    for field, value in (("role", "admin"), ("email", "x@demo.example.test")):
        r = client.patch("/api/me", json={"display_name": "Имя", "bio": "", field: value})
        assert r.status_code == 422
    assert client.get("/api/me").json()["role"] == "student"


# ---------- Sessions

def test_au09_logout_kills_the_session(env):
    client, _ = raw_login(STUDENT)
    token = client.cookies.get("lms_session")
    assert client.post("/api/auth/logout").status_code == 200
    stale = TestClient(app)
    stale.cookies.set("lms_session", token)
    assert stale.get("/api/me").status_code == 401
    assert TestClient(app).post("/api/auth/logout").status_code == 200


def test_au10_forged_and_expired_sessions_rejected(env):
    s, _ = env
    forged = TestClient(app)
    forged.cookies.set("lms_session", "forged-token")
    assert forged.get("/api/me").status_code == 401
    client, _ = raw_login(STUDENT)
    uid = client.get("/api/me").json()["id"]
    for row in s.scalars(select(LoginSession).where(LoginSession.user_id == uid)):
        row.expires_at = now() - timedelta(seconds=1)
    s.flush()
    assert client.get("/api/me").status_code == 401
