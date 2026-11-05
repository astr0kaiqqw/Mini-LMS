"""PostgreSQL only. Opt-in, dedicated test DB, rollback all mutations."""
import importlib.util
import os
from pathlib import Path
import uuid
import pytest
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Role, User, UserProfile

pytestmark = pytest.mark.skipif(os.getenv('RUN_DB_TESTS') != '1', reason='Requires RUN_DB_TESTS=1 and mini_lms_test_* PostgreSQL')

@pytest.fixture
def session():
    url = os.environ.get('DATABASE_URL', '')
    parsed = make_url(url)
    if parsed.get_backend_name() != 'postgresql' or not (parsed.database or '').startswith('mini_lms_test_'):
        pytest.fail('Refusing database tests: explicit mini_lms_test_* PostgreSQL required')
    engine = create_engine(url)
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode='create_savepoint') as s:
            yield s
        transaction.rollback()
    engine.dispose()

def seed_function():
    path = Path(__file__).resolve().parents[2] / 'database/seeds/demo_users.py'
    spec = importlib.util.spec_from_file_location('demo_seed', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.seed

def test_seed_is_idempotent(session):
    seed = seed_function()
    seed(session)
    counts_before = [session.scalar(select(func.count()).select_from(model)) for model in (Role, User, UserProfile)]
    seed(session)
    counts_after = [session.scalar(select(func.count()).select_from(model)) for model in (Role, User, UserProfile)]
    assert counts_before == counts_after
    assert session.scalar(select(func.count()).select_from(User).where(User.email.in_(['student@example.test','teacher@example.test','admin@example.test']))) == 3

def test_unique_email(session):
    seed_function()(session)
    role = session.scalar(select(Role.id).where(Role.name == 'student'))
    with pytest.raises(IntegrityError):
        with session.begin_nested():
            session.add(User(email='student@example.test', display_name='Duplicate', role_id=role))
            session.flush()

def test_invalid_role_fk(session):
    missing = (session.scalar(select(func.max(Role.id))) or 0) + 1000
    with pytest.raises(IntegrityError):
        with session.begin_nested():
            session.add(User(email=f'{uuid.uuid4()}@example.test', display_name='Valid', role_id=missing))
            session.flush()

@pytest.mark.parametrize('email,name', [('UPPER@example.test', 'Name'), ('invalid','Name'), ('valid@example.test','   ')])
def test_user_checks(session, email, name):
    seed_function()(session)
    role = session.scalar(select(Role.id).where(Role.name == 'student'))
    with pytest.raises(IntegrityError):
        with session.begin_nested():
            session.add(User(email=email, display_name=name, role_id=role))
            session.flush()

def test_invalid_role_name(session):
    with pytest.raises(IntegrityError):
        with session.begin_nested():
            session.add(Role(name='superuser'))
            session.flush()

def test_profile_cascades_but_role_remains(session):
    seed_function()(session)
    role = session.scalar(select(Role.id).where(Role.name == 'student'))
    user = User(email=f'{uuid.uuid4()}@example.test', display_name='Temporary', role_id=role)
    session.add(user)
    session.flush()
    session.add(UserProfile(user_id=user.id, bio='Temporary'))
    session.flush()
    user_id = user.id
    session.execute(delete(User).where(User.id == user_id))
    assert session.scalar(select(func.count()).select_from(UserProfile).where(UserProfile.user_id == user_id)) == 0
    assert session.scalar(select(Role.id).where(Role.id == role)) == role
