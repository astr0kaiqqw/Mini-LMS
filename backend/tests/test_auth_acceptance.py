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
