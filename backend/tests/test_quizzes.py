"""Course completion gate, answer-key isolation and persisted scoring."""
from sqlalchemy import select, func
from app.models import LessonProgress, QuizQuestion, QuizAttempt
from app.learning import lessons_for
from test_learning import env, course, pytestmark
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'database/seeds'))
from course_quizzes import seed


def test_quiz_gate_keys_scoring_and_seed(env):
    s, login = env
    seed(s)
    count = s.scalar(select(func.count()).select_from(QuizQuestion))
    seed(s)
    assert s.scalar(select(func.count()).select_from(QuizQuestion)) == count
    c = course(s)
    url = f'/api/courses/{c.id}/quiz'
    student = login('calculus-1.student1@demo.example.test')
    data = student.get(url).json()
    assert not data['unlocked'] and data['questions'] == []
    assert student.post(url + '/attempts', json={'answers': {}}).status_code == 403
    teacher = login('instructor@demo.example.test')
    key = teacher.get(url).json()
    assert key['staff'] and key['unlocked'] and key['ready']
    assert len(key['questions']) == len(lessons_for(s, c.id)) == 10
    assert all('correct_index' in q for q in key['questions'])
    admin = login('administrator@demo.example.test')
    assert admin.get(url).json()['questions'] == key['questions']
    assert teacher.post(url + '/attempts', json={'answers': {}}).status_code == 403
    uid = student.get('/api/me').json()['id']
    for lesson in lessons_for(s, c.id):
        p = s.get(LessonProgress, (uid, lesson.id))
        if p is None:
            p = LessonProgress(user_id=uid, lesson_id=lesson.id)
            s.add(p)
        p.completed = True
    s.flush()
    data = student.get(url).json()
    assert data['unlocked'] and data['ready']
    assert all('correct_index' not in q and 'explanation' not in q for q in data['questions'])
    assert student.post(url + '/attempts', json={'answers': {}}).status_code == 422
    answers = {str(q['id']): q['correct_index'] for q in key['questions']}
    response = student.post(url + '/attempts', json={'answers': answers})
    assert response.status_code == 200, response.text
    assert response.json()['percent'] == 100
    assert s.get(QuizAttempt, response.json()['id']).correct == 10
    assert len(student.get(url).json()['attempts']) == 1
    other = login('english.student1@demo.example.test')
    assert other.get(url).status_code == 403
    # Completion is rechecked on every submission, including after a lesson is added/reset.
    p.completed = False
    s.flush()
    assert student.post(url + '/attempts', json={'answers': answers}).status_code == 403
