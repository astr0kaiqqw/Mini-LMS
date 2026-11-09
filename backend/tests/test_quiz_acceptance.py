"""Acceptance scenarios for the course quiz (testing/QUIZ_ACCEPTANCE.md).

Each test name carries the scenario ID. xfail(strict=True) marks a confirmed gap:
the test documents the agreed requirement and starts failing loudly once the gap
is closed, so the marker must then be removed.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from app.learning import lessons_for
from app.main import app
from app.models import LessonProgress, QuizAttempt
from test_learning import env, course, pytestmark  # noqa: F401  (fixture + DB skip marker)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "database/seeds"))
from course_quizzes import seed  # noqa: E402

STUDENT = "calculus-1.student2@demo.example.test"
OTHER_STUDENT = "english.student1@demo.example.test"
TEACHER = "instructor@demo.example.test"


@pytest.fixture
def quiz(env):
    s, login = env
    seed(s)
    c = course(s)
    url = f"/api/courses/{c.id}/quiz"
    teacher = login(TEACHER)
    key = {str(q["id"]): q["correct_index"] for q in teacher.get(url).json()["questions"]}
    student = login(STUDENT)
    uid = student.get("/api/me").json()["id"]

    def finish_lessons():
        for lesson in lessons_for(s, c.id):
            p = s.get(LessonProgress, (uid, lesson.id))
            if p is None:
                p = LessonProgress(user_id=uid, lesson_id=lesson.id)
                s.add(p)
            p.completed = True
        s.flush()

    return dict(s=s, login=login, c=c, url=url, teacher=teacher, key=key,
                student=student, uid=uid, finish=finish_lessons)


def attempts(q):
    return q["s"].scalar(select(func.count()).select_from(QuizAttempt)
                         .where(QuizAttempt.user_id == q["uid"]))


def test_qz01_requires_session(quiz):
    anon = TestClient(app)
    assert anon.get(quiz["url"]).status_code == 401
    assert anon.post(quiz["url"] + "/attempts", json={"answers": quiz["key"]}).status_code == 401


def test_qz02_locked_until_all_lessons_completed(quiz):
    data = quiz["student"].get(quiz["url"]).json()
    assert data["unlocked"] is False and data["questions"] == []
    assert quiz["student"].post(quiz["url"] + "/attempts", json={"answers": quiz["key"]}).status_code == 403
    assert attempts(quiz) == 0


def test_qz03_unlocked_quiz_hides_answer_keys(quiz):
    quiz["finish"]()
    data = quiz["student"].get(quiz["url"]).json()
    assert data["unlocked"] and data["ready"] and len(data["questions"]) == 10
    for q in data["questions"]:
        assert "correct_index" not in q and "explanation" not in q


@pytest.mark.parametrize("wrong_count, percent", [(0, 100), (3, 70), (10, 0)])
def test_qz04_server_scores_attempt(quiz, wrong_count, percent):
    quiz["finish"]()
    answers = dict(quiz["key"])
    for qid in list(answers)[:wrong_count]:
        answers[qid] = (answers[qid] + 1) % 4
    r = quiz["student"].post(quiz["url"] + "/attempts", json={"answers": answers})
    assert r.status_code == 200, r.text
    body = r.json()
    assert (body["correct"], body["total"], body["percent"]) == (10 - wrong_count, 10, percent)


def test_qz05_result_survives_reload(quiz):
    quiz["finish"]()
    saved = quiz["student"].post(quiz["url"] + "/attempts", json={"answers": quiz["key"]}).json()
    again = quiz["login"](STUDENT).get(quiz["url"]).json()["attempts"]
    assert again[0]["id"] == saved["id"] and again[0]["percent"] == 100


def test_qz06_client_cannot_send_score(quiz):
    quiz["finish"]()
    r = quiz["student"].post(quiz["url"] + "/attempts", json={"answers": quiz["key"], "score": 10})
    assert r.status_code == 422
    assert attempts(quiz) == 0


@pytest.mark.parametrize("case", ["partial", "index_out_of_range", "string_index", "bool_index", "foreign_question"])
def test_qz07_invalid_answer_sets_rejected(quiz, case):
    quiz["finish"]()
    answers = dict(quiz["key"])
    first = next(iter(answers))
    if case == "partial":
        answers = {first: answers[first]}
    elif case == "index_out_of_range":
        answers[first] = 4
    elif case == "string_index":
        answers[first] = "1"
    elif case == "bool_index":
        answers[first] = True
    else:
        answers["999999"] = 0
    assert quiz["student"].post(quiz["url"] + "/attempts", json={"answers": answers}).status_code == 422
    assert attempts(quiz) == 0


def test_qz08_other_course_student_has_no_access(quiz):
    other = quiz["login"](OTHER_STUDENT)
    assert other.get(quiz["url"]).status_code == 403
    assert other.post(quiz["url"] + "/attempts", json={"answers": quiz["key"]}).status_code == 403


def test_qz09_staff_sees_keys_but_cannot_submit(quiz):
    data = quiz["teacher"].get(quiz["url"]).json()
    assert data["staff"] and all("correct_index" in q for q in data["questions"])
    assert quiz["teacher"].post(quiz["url"] + "/attempts", json={"answers": quiz["key"]}).status_code == 403


def test_qz10_draft_course_quiz_closed(quiz):
    quiz["finish"]()
    quiz["c"].status = "draft"
    quiz["s"].flush()
    assert quiz["student"].get(quiz["url"]).status_code == 403


def test_qz11_each_submit_is_a_new_attempt(quiz):
    """Agreed behaviour for now: attempts are unlimited, history is kept newest first."""
    quiz["finish"]()
    for _ in range(2):
        assert quiz["student"].post(quiz["url"] + "/attempts", json={"answers": quiz["key"]}).status_code == 200
    listed = quiz["student"].get(quiz["url"]).json()["attempts"]
    assert len(listed) == attempts(quiz) == 2
    assert listed[0]["id"] > listed[1]["id"]


@pytest.mark.xfail(strict=True, reason="GAP-1: teacher cannot see students' quiz results (QUIZ_TECHNICAL_DESCRIPTION, раздел 7)")
def test_qz20_teacher_sees_student_quiz_result(quiz):
    quiz["finish"]()
    quiz["student"].post(quiz["url"] + "/attempts", json={"answers": quiz["key"]})
    card = quiz["teacher"].get(f"/api/staff/courses/{quiz['c'].id}/students/{quiz['uid']}").json()
    assert "quiz" in card


@pytest.mark.xfail(strict=True, reason="GAP-2: student gradebook has no quiz result (QUIZ_TECHNICAL_DESCRIPTION, раздел 7)")
def test_qz21_gradebook_shows_best_quiz_result(quiz):
    quiz["finish"]()
    quiz["student"].post(quiz["url"] + "/attempts", json={"answers": quiz["key"]})
    assert "quiz" in quiz["student"].get("/api/me/gradebook").json()
