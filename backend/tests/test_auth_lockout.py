"""AUTH-LOCKOUT (decision D1): lock details, window reset and parallel attempts beyond test_au20."""
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.engine import make_url

from app.db import SessionLocal
from app.learning import now
from app.main import app
from app.models import LoginAttempt
from test_auth_acceptance import STUDENT, raw_login
from test_learning import env, pytestmark  # noqa: F401  (fixture + DB skip marker)


def test_au20_lock_details_unknown_email_and_expiry(env):
    s, _ = env
    for i in range(5):
        raw_login(STUDENT, f"guess-{i}")
    _, r = raw_login(STUDENT)  # even the right password is not checked while locked
    assert r.status_code == 429
    assert 840 < int(r.headers["Retry-After"]) <= 900
    assert "15 минут" in r.json()["detail"]

    # An email without an account locks the same way, so the lock reveals nothing.
    for i in range(5):
        assert raw_login("nobody@demo.example.test", f"guess-{i}")[1].status_code == 401
    assert raw_login("nobody@demo.example.test")[1].status_code == 429

    # After the lock ends, the right password works and the counter is removed.
    attempt = s.get(LoginAttempt, STUDENT, populate_existing=True)
    attempt.locked_until = now() - timedelta(seconds=1)
    attempt.first_failed_at = now() - timedelta(minutes=16)
    s.flush()
    assert raw_login(STUDENT)[1].status_code == 200
    assert s.get(LoginAttempt, STUDENT, populate_existing=True) is None


def test_au20_failures_outside_the_window_start_a_new_count(env):
    s, _ = env
    for i in range(4):
        raw_login(STUDENT, f"guess-{i}")
    attempt = s.get(LoginAttempt, STUDENT, populate_existing=True)
    attempt.first_failed_at = now() - timedelta(minutes=16)
    s.flush()
    assert raw_login(STUDENT, "guess-5")[1].status_code == 401  # 5th failure, but a new window
    attempt = s.get(LoginAttempt, STUDENT, populate_existing=True)
    assert attempt.failed_count == 1 and attempt.locked_until is None
    assert raw_login(STUDENT)[1].status_code == 200


def test_au20_parallel_failures_cannot_pass_the_limit():
    """Real commits on the mini_lms_test_* DB: 20 wrong passwords at once, at most 5 are checked."""
    assert (make_url(os.environ["DATABASE_URL"]).database or "").startswith("mini_lms_test_")
    email = "parallel-lock@demo.example.test"

    def clean():
        with SessionLocal() as s:
            s.execute(delete(LoginAttempt).where(LoginAttempt.email == email))
            s.commit()

    def attempt(i):
        with TestClient(app) as client:
            return client.post("/api/auth/login", json={"email": email, "password": f"bad-{i}"}).status_code

    clean()
    try:
        with ThreadPoolExecutor(10) as pool:
            codes = Counter(pool.map(attempt, range(20)))
        assert codes == {401: 5, 429: 15}
        with SessionLocal() as s:
            assert s.get(LoginAttempt, email).failed_count == 5
    finally:
        clean()
