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


# ---------- Roles

def test_au11_role_change_applies_to_existing_session(env):
    admin, _ = raw_login(ADMIN)
    user, r = register("future.teacher@demo.example.test")
    uid = r.json()["id"]
    assert user.get("/api/staff/courses").status_code == 403
    assert admin.put(f"/api/admin/users/{uid}/role", json={"role": "teacher"}).status_code == 200
    assert user.get("/api/staff/courses").status_code == 200
    assert admin.put(f"/api/admin/users/{uid}/role", json={"role": "student"}).status_code == 200
    assert user.get("/api/staff/courses").status_code == 403


def test_au12_role_management_rules(env):
    admin, _ = raw_login(ADMIN)
    teacher, _ = raw_login(TEACHER)
    _, r = register("target@demo.example.test")
    target = r.json()["id"]
    admin_id = admin.get("/api/me").json()["id"]
    assert teacher.put(f"/api/admin/users/{target}/role", json={"role": "teacher"}).status_code == 403
    assert admin.put(f"/api/admin/users/{admin_id}/role", json={"role": "student"}).status_code == 403
    assert admin.put(f"/api/admin/users/{target}/role", json={"role": "root"}).status_code == 422
    assert admin.put("/api/admin/users/99999999/role", json={"role": "teacher"}).status_code == 404


ROLES = ("anon", "student", "other", "teacher", "foreign", "admin")


@pytest.fixture
def actors(env):
    s, login = env
    admin = login(ADMIN)
    foreign, r = register("foreign.teacher@demo.example.test", name="Чужой преподаватель")
    assert admin.put(f"/api/admin/users/{r.json()['id']}/role", json={"role": "teacher"}).status_code == 200
    clients = dict(anon=TestClient(app), student=login(STUDENT), other=login(OTHER),
                   teacher=login(TEACHER), foreign=foreign, admin=admin)
    c = course(s)
    ids = dict(c=c.id, m=s.scalar(select(Module.id).where(Module.course_id == c.id).order_by(Module.position)),
               l=lessons_for(s, c.id)[0].id, sid=clients["student"].get("/api/me").json()["id"])
    return s, clients, c, ids


def test_au13_permission_matrix(actors):
    """Every role against every protected endpoint; see AUTH_TECHNICAL_DESCRIPTION, section 5."""
    s, clients, c, ids = actors
    course_body = dict(slug=c.slug, title=c.title, description=c.description, status=c.status)
    lesson = dict(title="Урок", position=1, summary="", content="", practice="", duration_minutes=15)
    grade = dict(user_id=ids["sid"], kind="course", lesson_id=None, score=80, comment="")
    #            method, path,                                             body,         anon student other teacher foreign admin
    matrix = [
        ("GET", "/api/me", None,                                                         (401, 200, 200, 200, 200, 200)),
        ("PATCH", "/api/me", dict(display_name="Имя", bio=""),                           (401, 200, 200, 200, 200, 200)),
        ("GET", "/api/courses", None,                                                    (200, 200, 200, 200, 200, 200)),
        ("GET", "/api/courses/{c}", None,                                                (401, 200, 403, 200, 403, 200)),
        ("GET", "/api/lessons/{l}", None,                                                (401, 200, 403, 200, 403, 200)),
        ("POST", "/api/lessons/{l}/complete", None,                                      (401, 200, 403, 200, 403, 200)),
        ("GET", "/api/me/courses", None,                                                 (401, 200, 200, 200, 200, 200)),
        ("GET", "/api/me/gradebook", None,                                               (401, 200, 200, 200, 200, 200)),
        ("GET", "/api/courses/{c}/quiz", None,                                           (401, 200, 403, 200, 403, 200)),
        ("GET", "/api/staff/courses", None,                                              (401, 403, 403, 200, 200, 200)),
        ("GET", "/api/staff/students", None,                                             (401, 403, 403, 200, 200, 200)),
        ("GET", "/api/staff/students?course_id={c}", None,                               (401, 403, 403, 200, 403, 200)),
        ("GET", "/api/staff/courses/{c}/students/{sid}", None,                           (401, 403, 403, 200, 403, 200)),
        ("PUT", "/api/staff/courses/{c}/grades", grade,                                  (401, 403, 403, 200, 403, 200)),
        ("POST", "/api/staff/courses", dict(slug="matrix-probe", title="Probe"),         (401, 403, 403, 200, 200, 200)),
        ("PUT", "/api/staff/courses/{c}", course_body,                                   (401, 403, 403, 200, 403, 200)),
        ("PUT", "/api/staff/modules/{m}", dict(title="Модуль", position=1),              (401, 403, 403, 200, 403, 200)),
        ("PUT", "/api/staff/lessons/{l}", lesson,                                        (401, 403, 403, 200, 403, 200)),
        ("DELETE", "/api/staff/courses/{c}", None,                                       (401, 403, 403, None, 403, None)),
        ("GET", "/api/admin/users", None,                                                (401, 403, 403, 403, 403, 200)),
        ("PUT", "/api/admin/users/{sid}/role", dict(role="student"),                     (401, 403, 403, 403, 403, 200)),
    ]
    mismatches = []
    for method, path, body, expected in matrix:
        url = path.format(**ids)
        for who, want in zip(ROLES, expected):
            if want is None:  # destructive call for an authorized role: not part of the access check
                continue
            savepoint = s.begin_nested()
            got = clients[who].request(method, url, json=body).status_code
            savepoint.rollback()
            if got != want:
                mismatches.append(f"{method} {url} as {who}: expected {want}, got {got}")
    assert not mismatches, "\n".join(mismatches)


# ---------- Confirmed gaps (AUTH_TECHNICAL_DESCRIPTION, section 8)

@pytest.mark.xfail(strict=True, reason="AUTH-GAP-1: no brute-force protection on login")
def test_au20_login_locked_after_five_failures(env):
    for i in range(5):
        _, r = raw_login(STUDENT, f"guess-{i}")
        assert r.status_code == 401
    _, r = raw_login(STUDENT, "guess-6")
    assert r.status_code == 429


def test_au21_trivial_password_rejected(env):
    _, r = register("weak@demo.example.test", password="11111111")
    assert r.status_code == 422


def test_au22_user_can_change_password(env):
    client, _ = raw_login(STUDENT)
    r = client.post("/api/me/password", json={"current_password": PW, "new_password": "NewPass2026!"})
    assert r.status_code == 200
    assert raw_login(STUDENT, "NewPass2026!")[1].status_code == 200


def test_au23_expired_sessions_cleaned_on_login(env):
    s, _ = env
    client, _ = raw_login(STUDENT)
    uid = client.get("/api/me").json()["id"]
    for row in s.scalars(select(LoginSession).where(LoginSession.user_id == uid)):
        row.expires_at = now() - timedelta(days=1)
    s.flush()
    raw_login(STUDENT)
    assert sessions_of(s, uid, expired_only=True) == 0


def test_au24_staff_cannot_self_enroll(actors):
    s, clients, c, ids = actors
    assert clients["foreign"].post(f"/api/courses/{c.id}/enroll").status_code == 403
