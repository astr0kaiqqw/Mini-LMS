import secrets

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import User
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
