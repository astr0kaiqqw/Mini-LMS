"""AUTH-PASSWORD-RULES (decision D2): rule cases beyond test_au21."""
import pytest

from test_auth_acceptance import register
from test_learning import env, pytestmark  # noqa: F401  (fixture + DB skip marker)


@pytest.mark.parametrize("case, password", [
    ("no_letter", "12345678"),
    ("no_digit", "onlyletters"),
    ("too_short", "abc1234"),
    ("same_as_email", "rule1@demo.example.test"),
])
def test_au21_password_rules(env, case, password):
    _, r = register("rule1@demo.example.test", password=password)
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], str)  # readable message for the form, not a field dump
    _, r = register("rule1@demo.example.test", password="Letters2026")
    assert r.status_code == 201
