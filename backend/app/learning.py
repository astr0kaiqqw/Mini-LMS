from datetime import datetime, timedelta, timezone
from typing import Literal
import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator
from sqlalchemy import select, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import (
    User,
    Role,
    UserProfile,
    Credential,
    LoginSession,
    Course,
    Module,
    Lesson,
    Enrollment,
    LessonProgress,
    Grade,
    CourseTeacher,
    QuizQuestion,
    QuizAttempt,
)
from .security import hash_password, verify_password, token_hash

router = APIRouter(prefix="/api")


def now():
    return datetime.now(timezone.utc)


def db():
    with SessionLocal() as session:
        try:
            yield session
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                409, "Запись уже существует или связана с другими данными"
            ) from None


def current(request: Request, s: Session = Depends(db)):
    token = request.cookies.get("lms_session", "")
    record = s.get(LoginSession, token_hash(token)) if token else None
    if not record or record.expires_at <= now():
        raise HTTPException(401, "Войдите в аккаунт")
    return s.get(User, record.user_id)


def role(s, user):
    return s.get(Role, user.role_id).name


def staff(user=Depends(current), s: Session = Depends(db)):
    if role(s, user) not in ("teacher", "admin"):
        raise HTTPException(403, "Раздел доступен преподавателю")
    return user


def owned(s, course_id, user):
    course = s.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Курс не найден")
    if (
        role(s, user) != "admin"
        and course.teacher_id != user.id
        and not s.get(CourseTeacher, (course_id, user.id))
    ):
        raise HTTPException(403, "Это чужой курс")
    return course


def access(s, course_id, user):
    course = s.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Курс не найден")
    if (
        role(s, user) == "admin"
        or course.teacher_id == user.id
        or (role(s, user) == "teacher" and s.get(CourseTeacher, (course_id, user.id)))
    ):
        return course
    if course.status != "published" or not s.get(Enrollment, (user.id, course_id)):
        raise HTTPException(403, "Вы не записаны на опубликованный курс")
    return course


def lesson_course(s, lesson_id):
    lesson = s.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Урок не найден")
    return lesson, s.get(Module, lesson.module_id).course_id


def user_dict(s, u):
    profile = s.get(UserProfile, u.id)
    return dict(
        id=u.id,
        email=u.email,
        display_name=u.display_name,
        role=role(s, u),
        bio=profile.bio if profile else "",
    )


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Login(Strict):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=200)


@router.post("/auth/login")
def login(data: Login, response: Response, s: Session = Depends(db)):
    user = s.scalar(select(User).where(User.email == data.email.strip().lower()))
    credential = s.get(Credential, user.id) if user else None
    # Perform a password derivation even when the account has no credential.
    valid = (
        verify_password(data.password, credential.password_hash)
        if credential
        else verify_password(data.password, "pbkdf2_sha256$600000$dummy$invalid")
    )
    if not valid:
        raise HTTPException(401, "Неверный email или пароль")
    return start_session(s, response, user)


def start_session(s, response, user):
    token = secrets.token_urlsafe(32)
    s.add(
        LoginSession(
            token_hash=token_hash(token),
            user_id=user.id,
            expires_at=now() + timedelta(days=7),
        )
    )
    response.set_cookie(
        "lms_session",
        token,
        httponly=True,
        samesite="strict",
        secure=os.getenv("COOKIE_SECURE") == "1",
        max_age=604800,
    )
    return user_dict(s, user)


class Register(Login):
    email: str = Field(max_length=254, pattern=r"^\s*[^@\s]+@[^@\s]+\s*$")
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=200)


@router.post("/auth/register", status_code=201)
def register(data: Register, response: Response, s: Session = Depends(db)):
    email, name = data.email.strip().lower(), data.display_name.strip()
    if not name:
        raise HTTPException(422, "Укажите имя")
    if s.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(409, "Этот email уже зарегистрирован")
    student = s.scalar(select(Role.id).where(Role.name == "student"))
    user = User(email=email, display_name=name, role_id=student)
    s.add(user)
    s.flush()
    s.add(Credential(user_id=user.id, password_hash=hash_password(data.password)))
    s.add(UserProfile(user_id=user.id))
    return start_session(s, response, user)


@router.post("/auth/logout")
def logout(request: Request, response: Response, s: Session = Depends(db)):
    s.execute(
        delete(LoginSession).where(
            LoginSession.token_hash
            == token_hash(request.cookies.get("lms_session", ""))
        )
    )
    response.delete_cookie("lms_session")
    return {"ok": True}


@router.get("/me")
def me(user=Depends(current), s: Session = Depends(db)):
    return user_dict(s, user)


class ProfileInput(Strict):
    display_name: str = Field(min_length=1, max_length=100)
    bio: str = Field(max_length=500)


@router.patch("/me")
def profile(data: ProfileInput, user=Depends(current), s: Session = Depends(db)):
    user.display_name = data.display_name
    p = s.get(UserProfile, user.id)
    if not p:
        p = UserProfile(user_id=user.id)
        s.add(p)
    p.bio = data.bio
    s.flush()
    return user_dict(s, user)


def lessons_for(s, course_id):
    return s.scalars(
        select(Lesson)
        .join(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.position, Lesson.position)
    ).all()


def progress_dict(p, lesson):
    percent = (
        round(min(100, p.watched_seconds / lesson.video_duration * 100), 1)
        if p and lesson.video_duration
        else None
    )
    return dict(
        completed=bool(p and p.completed),
        video_percent=percent,
        status="Завершён" if p and p.completed else "В процессе" if p else "Не начат",
        demo=bool(p and p.demo),
        updated_at=p.updated_at if p else None,
    )


def summary(s, course_id, user_id):
    lessons = lessons_for(s, course_id)
    records = {
        p.lesson_id: p
        for p in s.scalars(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id.in_([l.id for l in lessons]),
            )
        )
    }
    complete = sum(bool(records.get(l.id) and records[l.id].completed) for l in lessons)
    return dict(
        completed=complete,
        total=len(lessons),
        percent=round(complete / len(lessons) * 100) if lessons else 0,
        last_activity=max((p.updated_at for p in records.values()), default=None),
        demo=any(p.demo for p in records.values()),
    )


def course_dict(s, c):
    return dict(
        id=c.id,
        slug=c.slug,
        title=c.title,
        description=c.description,
        status=c.status,
        teacher_id=c.teacher_id,
        teacher=s.get(User, c.teacher_id).display_name,
        lessons=len(lessons_for(s, c.id)),
    )


@router.get("/courses")
def catalog(s: Session = Depends(db)):
    return [
        course_dict(s, c)
        for c in s.scalars(
            select(Course).where(Course.status == "published").order_by(Course.id)
        )
    ]


@router.get("/courses/{course_id}")
def course_detail(course_id: int, user=Depends(current), s: Session = Depends(db)):
    c = access(s, course_id, user)
    result = course_dict(s, c)
    result["progress"] = summary(s, c.id, user.id)
    result["modules"] = [
        dict(id=m.id, title=m.title, position=m.position)
        for m in s.scalars(
            select(Module).where(Module.course_id == c.id).order_by(Module.position)
        )
    ]
    result["items"] = [
        dict(
            id=l.id,
            module_id=l.module_id,
            title=l.title,
            summary=l.summary,
            position=l.position,
            duration_minutes=l.duration_minutes,
            video=bool(l.video_url),
            **progress_dict(s.get(LessonProgress, (user.id, l.id)), l),
        )
        for l in lessons_for(s, c.id)
    ]
    return result


@router.post("/courses/{course_id}/enroll")
def enroll(course_id: int, user=Depends(current), s: Session = Depends(db)):
    course = s.get(Course, course_id)
    if not course or course.status != "published":
        raise HTTPException(404, "Курс не найден")
    s.execute(
        insert(Enrollment)
        .values(user_id=user.id, course_id=course_id)
        .on_conflict_do_nothing()
    )
    return {"enrolled": True}


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int, user=Depends(current), s: Session = Depends(db)):
    l, course_id = lesson_course(s, lesson_id)
    access(s, course_id, user)
    return dict(
        id=l.id,
        course_id=course_id,
        title=l.title,
        summary=l.summary,
        content=l.content,
        practice=l.practice,
        duration_minutes=l.duration_minutes,
        video_url=l.video_url,
        video_duration=l.video_duration,
        **progress_dict(s.get(LessonProgress, (user.id, l.id)), l),
    )


def locked_progress(s, user_id, lesson_id):
    s.execute(
        insert(LessonProgress)
        .values(user_id=user_id, lesson_id=lesson_id)
        .on_conflict_do_nothing()
    )
    return s.scalar(
        select(LessonProgress)
        .where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id)
        .with_for_update()
    )


@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(lesson_id: int, user=Depends(current), s: Session = Depends(db)):
    lesson, course_id = lesson_course(s, lesson_id)
    access(s, course_id, user)
    if lesson.video_url:
        raise HTTPException(
            422, "Видео завершается после просмотра 90% уникальных участков"
        )
    p = locked_progress(s, user.id, lesson.id)
    p.completed, p.demo, p.updated_at = True, False, now()
    return progress_dict(p, lesson)


def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return merged


class WatchInput(Strict):
    start: float = Field(ge=0, allow_inf_nan=False)
    end: float = Field(gt=0, allow_inf_nan=False)


@router.post("/lessons/{lesson_id}/watch")
def watch(
    lesson_id: int, data: WatchInput, user=Depends(current), s: Session = Depends(db)
):
    lesson, course_id = lesson_course(s, lesson_id)
    access(s, course_id, user)
    if (
        not lesson.video_url
        or not lesson.video_duration
        or not 0 < data.end - data.start <= 10
        or data.end > lesson.video_duration + 0.5
    ):
        raise HTTPException(422, "Неверный участок видео")
    p = locked_progress(s, user.id, lesson.id)
    p.intervals = merge_intervals(
        p.intervals + [[data.start, min(data.end, lesson.video_duration)]]
    )
    p.watched_seconds = sum(end - start for start, end in p.intervals)
    p.completed = p.watched_seconds >= lesson.video_duration * 0.9
    p.demo, p.updated_at = False, now()
    return progress_dict(p, lesson)


@router.get("/me/courses")
def my_courses(user=Depends(current), s: Session = Depends(db)):
    return [
        dict(**course_dict(s, c), progress=summary(s, c.id, user.id))
        for c in s.scalars(
            select(Course).join(Enrollment).where(Enrollment.user_id == user.id)
        )
    ]


def grade_dict(s, g):
    return dict(
        id=g.id,
        course_id=g.course_id,
        course=s.get(Course, g.course_id).title,
        user_id=g.user_id,
        lesson_id=g.lesson_id,
        lesson=s.get(Lesson, g.lesson_id).title if g.lesson_id else None,
        kind=g.kind,
        score=g.score,
        comment=g.comment,
        author=s.get(User, g.author_id).display_name,
        updated_at=g.updated_at,
        demo=g.demo,
    )


@router.get("/me/grades")
def own_grades(user=Depends(current), s: Session = Depends(db)):
    return [
        grade_dict(s, g)
        for g in s.scalars(
            select(Grade).where(Grade.user_id == user.id).order_by(Grade.id)
        )
    ]


@router.get("/me/gradebook")
def gradebook(user=Depends(current), s: Session = Depends(db)):
    result = []
    for c in s.scalars(
        select(Course).join(Enrollment).where(Enrollment.user_id == user.id)
    ):
        grades = s.scalars(
            select(Grade).where(Grade.user_id == user.id, Grade.course_id == c.id)
        ).all()
        by_target = {(g.lesson_id, g.kind): g for g in grades}
        targets = [(None, "course", None)]
        for l in lessons_for(s, c.id):
            targets.extend([(l.id, "lesson", l.title), (l.id, "practice", l.title)])
        for lid, kind, title in targets:
            g = by_target.get((lid, kind))
            result.append(
                grade_dict(s, g)
                if g
                else dict(
                    id=f"{c.id}-{lid}-{kind}",
                    course=c.title,
                    course_id=c.id,
                    lesson_id=lid,
                    lesson=title,
                    kind=kind,
                    score=None,
                    comment="",
                    author=None,
                    updated_at=None,
                    demo=False,
                )
            )
    return result


@router.get("/staff/courses")
def staff_courses(user=Depends(staff), s: Session = Depends(db)):
    query = select(Course).order_by(Course.id)
    if role(s, user) != "admin":
        query = query.where(
            (Course.teacher_id == user.id)
            | Course.id.in_(
                select(CourseTeacher.course_id).where(CourseTeacher.user_id == user.id)
            )
        )
    return [course_dict(s, c) for c in s.scalars(query)]


@router.get("/staff/students")
def students(
    course_id: int | None = None,
    q: str = "",
    user=Depends(staff),
    s: Session = Depends(db),
):
    query = (
        select(User, Course)
        .join(Enrollment, Enrollment.user_id == User.id)
        .join(Course, Enrollment.course_id == Course.id)
    )
    if course_id:
        owned(s, course_id, user)
        query = query.where(Course.id == course_id)
    if role(s, user) != "admin":
        query = query.where(
            (Course.teacher_id == user.id)
            | Course.id.in_(
                select(CourseTeacher.course_id).where(CourseTeacher.user_id == user.id)
            )
        )
    if q:
        query = query.where(User.display_name.ilike("%" + q + "%"))
    return [
        dict(
            user_id=u.id,
            name=u.display_name,
            course_id=c.id,
            course=c.title,
            **summary(s, c.id, u.id),
        )
        for u, c in s.execute(query.order_by(Course.id, User.display_name))
    ]


@router.get("/staff/courses/{course_id}/students/{user_id}")
def student_detail(
    course_id: int, user_id: int, user=Depends(staff), s: Session = Depends(db)
):
    owned(s, course_id, user)
    if not s.get(Enrollment, (user_id, course_id)):
        raise HTTPException(404, "Ученик не записан на курс")
    return dict(
        name=s.get(User, user_id).display_name,
        **summary(s, course_id, user_id),
        lessons=[
            dict(
                id=l.id,
                title=l.title,
                video=bool(l.video_url),
                **progress_dict(s.get(LessonProgress, (user_id, l.id)), l),
            )
            for l in lessons_for(s, course_id)
        ],
        grades=[
            grade_dict(s, g)
            for g in s.scalars(
                select(Grade).where(
                    Grade.user_id == user_id, Grade.course_id == course_id
                )
            )
        ],
    )


class GradeInput(Strict):
    user_id: int
    lesson_id: int | None = None
    kind: Literal["lesson", "practice", "course"]
    score: int = Field(ge=0, le=100, strict=True)
    comment: str = Field(default="", max_length=2000)


@router.put("/staff/courses/{course_id}/grades")
def set_grade(
    course_id: int, data: GradeInput, user=Depends(staff), s: Session = Depends(db)
):
    owned(s, course_id, user)
    if not s.get(Enrollment, (data.user_id, course_id)):
        raise HTTPException(422, "Ученик не записан на этот курс")
    if (
        data.kind == "course"
        and data.lesson_id is not None
        or data.kind != "course"
        and data.lesson_id is None
    ):
        raise HTTPException(422, "Выберите верный тип оценки")
    if data.lesson_id:
        _, lesson_course_id = lesson_course(s, data.lesson_id)
        if lesson_course_id != course_id:
            raise HTTPException(422, "Урок другого курса")
    target = (
        Grade.user_id == data.user_id,
        Grade.course_id == course_id,
        Grade.lesson_id == data.lesson_id,
        Grade.kind == data.kind,
    )
    # Serialize concurrent upserts through the enrollment row.
    s.scalar(
        select(Enrollment)
        .where(Enrollment.user_id == data.user_id, Enrollment.course_id == course_id)
        .with_for_update()
    )
    g = s.scalar(select(Grade).where(*target))
    if not g:
        g = Grade(course_id=course_id, **data.model_dump(), author_id=user.id)
        s.add(g)
    g.score, g.comment, g.author_id, g.updated_at, g.demo = (
        data.score,
        data.comment,
        user.id,
        now(),
        False,
    )
    s.flush()
    return grade_dict(s, g)


class CourseInput(Strict):
    slug: str = Field(
        min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    status: Literal["draft", "published"] = "draft"


@router.post("/staff/courses")
def create_course(data: CourseInput, user=Depends(staff), s: Session = Depends(db)):
    c = Course(**data.model_dump(), teacher_id=user.id)
    s.add(c)
    s.flush()
    return course_dict(s, c)


@router.put("/staff/courses/{course_id}")
def update_course(
    course_id: int, data: CourseInput, user=Depends(staff), s: Session = Depends(db)
):
    c = owned(s, course_id, user)
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    s.flush()
    return course_dict(s, c)


@router.delete("/staff/courses/{course_id}")
def delete_course(course_id: int, user=Depends(staff), s: Session = Depends(db)):
    s.delete(owned(s, course_id, user))
    return {"ok": True}


class ModuleInput(Strict):
    title: str = Field(min_length=1, max_length=200)
    position: int = Field(gt=0)


@router.post("/staff/courses/{course_id}/modules")
def create_module(
    course_id: int, data: ModuleInput, user=Depends(staff), s: Session = Depends(db)
):
    owned(s, course_id, user)
    m = Module(course_id=course_id, **data.model_dump())
    s.add(m)
    s.flush()
    return dict(id=m.id)


@router.put("/staff/modules/{module_id}")
def update_module(
    module_id: int, data: ModuleInput, user=Depends(staff), s: Session = Depends(db)
):
    m = s.get(Module, module_id)
    if not m:
        raise HTTPException(404, "Модуль не найден")
    owned(s, m.course_id, user)
    m.title, m.position = data.title, data.position
    return {"ok": True}


@router.delete("/staff/modules/{module_id}")
def delete_module(module_id: int, user=Depends(staff), s: Session = Depends(db)):
    m = s.get(Module, module_id)
    if not m:
        raise HTTPException(404, "Модуль не найден")
    owned(s, m.course_id, user)
    s.delete(m)
    return {"ok": True}


class LessonInput(ModuleInput):
    summary: str = Field(default="", max_length=1000)
    content: str = Field(default="", max_length=20000)
    practice: str = Field(default="", max_length=3000)
    duration_minutes: int = Field(default=15, gt=0, le=600)
    video_url: str | None = Field(default=None, max_length=2000)
    video_duration: int | None = Field(default=None, gt=0, le=86400)

    @model_validator(mode="after")
    def video(self):
        if bool(self.video_url) != bool(self.video_duration):
            raise ValueError("Видео требует URL и точную длительность в секундах")
        if self.video_url and not self.video_url.startswith(
            ("https://", "http://localhost:", "http://127.0.0.1:")
        ):
            raise ValueError("Нужна ссылка HTTPS на HTML5 видео")
        return self


@router.post("/staff/modules/{module_id}/lessons")
def create_lesson(
    module_id: int, data: LessonInput, user=Depends(staff), s: Session = Depends(db)
):
    m = s.get(Module, module_id)
    if not m:
        raise HTTPException(404, "Модуль не найден")
    owned(s, m.course_id, user)
    l = Lesson(module_id=module_id, **data.model_dump())
    s.add(l)
    s.flush()
    return dict(id=l.id)


@router.put("/staff/lessons/{lesson_id}")
def update_lesson(
    lesson_id: int, data: LessonInput, user=Depends(staff), s: Session = Depends(db)
):
    l, cid = lesson_course(s, lesson_id)
    owned(s, cid, user)
    if l.video_url != data.video_url or l.video_duration != data.video_duration:
        s.execute(delete(LessonProgress).where(LessonProgress.lesson_id == lesson_id))
    for k, v in data.model_dump().items():
        setattr(l, k, v)
    return {"ok": True}


@router.delete("/staff/lessons/{lesson_id}")
def delete_lesson(lesson_id: int, user=Depends(staff), s: Session = Depends(db)):
    l, cid = lesson_course(s, lesson_id)
    owned(s, cid, user)
    s.delete(l)
    return {"ok": True}


@router.get("/admin/users")
def admin_users(user=Depends(staff), s: Session = Depends(db)):
    if role(s, user) != "admin":
        raise HTTPException(403, "Только администратор")
    return [user_dict(s, u) for u in s.scalars(select(User).order_by(User.id))]


class RoleInput(Strict):
    role: Literal["student", "teacher", "admin"]


@router.put("/admin/users/{user_id}/role")
def set_role(
    user_id: int, data: RoleInput, user=Depends(staff), s: Session = Depends(db)
):
    if role(s, user) != "admin":
        raise HTTPException(403, "Только администратор")
    if user_id == user.id:
        raise HTTPException(403, "Нельзя менять собственную роль")
    target = s.get(User, user_id)
    if not target:
        raise HTTPException(404, "Пользователь не найден")
    target.role_id = s.scalar(select(Role.id).where(Role.name == data.role))
    s.flush()
    return user_dict(s, target)


# Answer keys are serialized only for authorized course staff.
def quiz_data(s, course_id, user, require_open=False):
    access(s, course_id, user)
    is_staff = role(s, user) in ("teacher", "admin")
    if is_staff:
        owned(s, course_id, user)
    progress = summary(s, course_id, user.id)
    unlocked = is_staff or (progress["total"] > 0 and progress["completed"] == progress["total"])
    if require_open and not unlocked:
        raise HTTPException(403, "Завершите все уроки курса, чтобы открыть итоговый квиз")
    lessons = lessons_for(s, course_id)
    questions = {q.lesson_id: q for q in s.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id.in_([l.id for l in lessons])))}
    ready = bool(lessons) and all(l.id in questions for l in lessons)
    return is_staff, unlocked, ready, lessons, questions


@router.get("/courses/{course_id}/quiz")
def get_quiz(course_id: int, user=Depends(current), s: Session = Depends(db)):
    is_staff, unlocked, ready, lessons, questions = quiz_data(s, course_id, user)
    attempts = s.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user.id, QuizAttempt.course_id == course_id).order_by(QuizAttempt.id.desc())).all()
    return dict(unlocked=unlocked, ready=ready, staff=is_staff, total=len(lessons),
        attempts=[dict(id=a.id, correct=a.correct, total=a.total, percent=round(a.correct/a.total*100), created_at=a.created_at) for a in attempts],
        questions=[dict(id=questions[l.id].id, topic=l.title, prompt=questions[l.id].prompt, options=questions[l.id].options,
            **(dict(correct_index=questions[l.id].correct_index, explanation=questions[l.id].explanation) if is_staff else {}))
            for l in lessons if l.id in questions] if unlocked and ready else [])


class QuizSubmission(Strict):
    answers: dict[int, StrictInt] = Field(max_length=500)


@router.post("/courses/{course_id}/quiz/attempts")
def submit_quiz(course_id: int, body: QuizSubmission, user=Depends(current), s: Session = Depends(db)):
    is_staff, _, ready, lessons, questions = quiz_data(s, course_id, user, require_open=True)
    if is_staff:
        raise HTTPException(403, "Попытки доступны ученикам; для преподавателя открыт просмотр ответов")
    if not ready:
        raise HTTPException(409, "Квиз ещё не подготовлен для всех уроков")
    ordered = [questions[l.id] for l in lessons]
    if set(body.answers) != {q.id for q in ordered} or any(type(v) is not int or v not in range(4) for v in body.answers.values()):
        raise HTTPException(422, "Выберите один ответ на каждый вопрос")
    correct = sum(body.answers[q.id] == q.correct_index for q in ordered)
    attempt = QuizAttempt(user_id=user.id, course_id=course_id, correct=correct, total=len(ordered),
        answers=[dict(question_id=q.id, selected=body.answers[q.id], correct=body.answers[q.id] == q.correct_index, prompt=q.prompt, options=q.options) for q in ordered])
    s.add(attempt)
    s.flush()
    return dict(id=attempt.id, correct=correct, total=attempt.total, percent=round(correct/attempt.total*100))
