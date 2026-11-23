"""AUTH-CHANGE-PASSWORD (decision D3): rules and sessions beyond test_au22."""
from fastapi.testclient import TestClient

from app.main import app
from test_auth_acceptance import PW, STUDENT, raw_login
from test_learning import env, pytestmark  # noqa: F401  (fixture + DB skip marker)


def test_au22_change_password_rules_and_sessions(env):
    current, _ = raw_login(STUDENT)
    other, _ = raw_login(STUDENT)
    url = "/api/me/password"
    assert TestClient(app).post(url, json={"current_password": PW, "new_password": "NewPass2026!"}).status_code == 401
    assert current.post(url, json={"current_password": "wrong", "new_password": "NewPass2026!"}).status_code == 403
    assert current.post(url, json={"current_password": PW, "new_password": "11111111"}).status_code == 422
    assert current.post(url, json={"current_password": PW, "new_password": "NewPass2026!", "role": "admin"}).status_code == 422
    assert other.get("/api/me").status_code == 200  # failed attempts change nothing

    assert current.post(url, json={"current_password": PW, "new_password": "NewPass2026!"}).status_code == 200
    assert current.get("/api/me").status_code == 200  # this device stays signed in
    assert other.get("/api/me").status_code == 401    # every other session is ended
    assert raw_login(STUDENT)[1].status_code == 401   # old password no longer works
