import secrets

from fastapi.testclient import TestClient
from sqlalchemy import select

from app import learning
from app.main import app
from app.models import PasswordReset, User
from app.security import verify_password
from test_learning import env, pytestmark


def test_account_ids_and_admin_password_status(env):
    session, login = env
    existing = session.scalars(select(User)).all()
    ids = {user.account_id for user in existing}
    assert len(ids) == len(existing)
    assert all(len(value) == 12 and value.isascii() and value.isdecimal() for value in ids)

    admin = login("administrator@demo.example.test")
    for role in ("student", "teacher"):
        email = f"{role}-{secrets.token_hex(5)}@example.test"
        with TestClient(app) as client:
            result = client.post("/api/auth/register", json={
                "email": email, "display_name": "Account ID test",
                "password": "OldPassword2026!", "role": role,
            })
            assert result.status_code == 201, result.text
            account = result.json()
            assert account["account_id"] not in ids
            ids.add(account["account_id"])
            assert client.get("/api/me").json()["account_id"] == account["account_id"]
            assert client.get("/api/admin/users").status_code == 403
        row = next(user for user in admin.get("/api/admin/users").json() if user["email"] == email)
        assert row["account_id"] == account["account_id"]
        assert row["has_password"] is True
        assert "password_hash" not in row and "password" not in row


def test_admin_reset_code_replacement_expiry_and_single_use(env):
    session, login = env
    email = "instructor@demo.example.test"
    teacher = login(email)
    admin = login("administrator@demo.example.test")
    account = teacher.get("/api/me").json()
    issue_url = f"/api/admin/users/{account['id']}/password-reset-code"
    confirm_url = "/api/auth/password-reset/confirm"

    with TestClient(app) as client:
        assert client.post(issue_url).status_code == 401
        assert teacher.post(issue_url).status_code == 403
        own_id = admin.get("/api/me").json()["id"]
        assert admin.post(f"/api/admin/users/{own_id}/password-reset-code").status_code == 403

        first = admin.post(issue_url)
        assert first.status_code == 200
        assert first.headers["Cache-Control"] == "no-store"
        first_code = first.json()["code"]
        assert len(first_code) == 4 and set(first_code) <= set(learning.RESET_CODE_ALPHABET)
        reset = session.get(PasswordReset, account["id"])
        assert verify_password(first_code, reset.code_hash)

        second_code = admin.post(issue_url).json()["code"]
        assert second_code != first_code
        payload = {"account_id": account["account_id"], "code": first_code, "password": "Replacement2026!"}
        assert client.post(confirm_url, json=payload).status_code == 400
        reset = session.get(PasswordReset, account["id"], populate_existing=True)
        reset.expires_at = learning.now()
        session.flush()
        assert client.post(confirm_url, json=dict(payload, code=second_code)).status_code == 400

        unlucky_code = admin.post(issue_url).json()["code"]
        wrong = "ZZZZ" if unlucky_code != "ZZZZ" else "YYYY"
        for _ in range(learning.MAX_RESET_ATTEMPTS):
            assert client.post(confirm_url, json=dict(payload, code=wrong)).status_code == 400
        assert client.post(confirm_url, json=dict(payload, code=unlucky_code)).status_code == 400

        payload["code"] = admin.post(issue_url).json()["code"].lower()
        assert client.post(confirm_url, json=payload).status_code == 200
        assert client.post(confirm_url, json=payload).status_code == 400
        assert teacher.get("/api/me").status_code == 401
        assert client.post("/api/auth/login", json={"email": email, "password": "LearnDemo2026!"}).status_code == 401
        assert client.post("/api/auth/login", json={"email": email, "password": payload["password"]}).status_code == 200
