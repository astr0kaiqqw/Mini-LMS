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

# Content schema checks run inside the same isolated, rolled-back transaction.
from app.models import Course, Module, Lesson


def content_seed(session):
    path = Path(__file__).resolve().parents[2] / 'database/seeds/demo_content.py'
    spec = importlib.util.spec_from_file_location('content_seed', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.seed(session)
    course = session.scalar(select(Course).where(Course.slug == 'data-thinking'))
    section = session.scalar(select(Module).where(Module.course_id == course.id, Module.position == 1))
    return course, section


def test_content_seed_is_idempotent(session):
    content_seed(session)
    before = [session.scalar(select(func.count()).select_from(m)) for m in (Course, Module, Lesson)]
    course, section = content_seed(session)
    assert before == [session.scalar(select(func.count()).select_from(m)) for m in (Course, Module, Lesson)]
    assert session.scalars(select(Lesson.position).where(Lesson.module_id == section.id).order_by(Lesson.position)).all() == [1, 2]
    assert course.status == 'published'


@pytest.mark.parametrize('case', ['slug', 'status', 'title', 'teacher_fk', 'module_position', 'lesson_position', 'module_order', 'lesson_order', 'course_fk', 'module_fk', 'module_title', 'lesson_title'])
def test_content_constraints(session, case):
    course, section = content_seed(session)
    missing_user = session.scalar(select(func.max(User.id))) + 1000
    missing_course = session.scalar(select(func.max(Course.id))) + 1000
    missing_module = session.scalar(select(func.max(Module.id))) + 1000
    candidates = {
        'slug': Course(slug=course.slug, title='Duplicate', teacher_id=course.teacher_id),
        'status': Course(slug='invalid-status', title='Test', teacher_id=course.teacher_id, status='unknown'),
        'title': Course(slug='empty-title', title=' ', teacher_id=course.teacher_id),
        'teacher_fk': Course(slug='missing-teacher', title='Test', teacher_id=missing_user),
        'module_position': Module(course_id=course.id, title='Test', position=1),
        'lesson_position': Lesson(module_id=section.id, title='Test', position=1),
        'module_order': Module(course_id=course.id, title='Test', position=0),
        'lesson_order': Lesson(module_id=section.id, title='Test', position=-1),
        'course_fk': Module(course_id=missing_course, title='Test', position=1),
        'module_fk': Lesson(module_id=missing_module, title='Test', position=1),
        'module_title': Module(course_id=course.id, title=' ', position=2),
        'lesson_title': Lesson(module_id=section.id, title=' ', position=3),
    }
    with pytest.raises(IntegrityError):
        with session.begin_nested():
            session.add(candidates[case])
            session.flush()


def test_course_delete_cascades_and_teacher_is_restricted(session):
    course, section = content_seed(session)
    with pytest.raises(IntegrityError):
        with session.begin_nested():
            session.execute(delete(User).where(User.id == course.teacher_id))
    session.execute(delete(Course).where(Course.id == course.id))
    assert session.scalar(select(func.count()).select_from(Module).where(Module.course_id == course.id)) == 0
    assert session.scalar(select(func.count()).select_from(Lesson).where(Lesson.module_id == section.id)) == 0
    assert session.get(User, course.teacher_id) is not None


def test_order_is_scoped_to_parent(session):
    course, section = content_seed(session)
    other = Course(slug='another-course', title='Another course', teacher_id=course.teacher_id)
    session.add(other)
    session.flush()
    other_module = Module(course_id=other.id, title='First module', position=1)
    session.add(other_module)
    session.flush()
    session.add(Lesson(module_id=other_module.id, title='First lesson', position=1))
    session.flush()
