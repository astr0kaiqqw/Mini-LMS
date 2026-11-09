"""One topic-matching question per lesson; preserve existing authored questions."""
import random
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Course, Module, Lesson, QuizQuestion


def seed(s):
    for course in s.scalars(select(Course).order_by(Course.id)):
        lessons = s.scalars(select(Lesson).join(Module).where(Module.course_id == course.id).order_by(Module.position, Lesson.position)).all()
        for lesson in lessons:
            if s.scalar(select(QuizQuestion).where(QuizQuestion.lesson_id == lesson.id)):
                continue
            answer = lesson.content.split('\n\nПример')[0].strip() or lesson.summary.strip()
            if not answer:
                continue
            others = list(dict.fromkeys((l.content.split('\n\nПример')[0].strip() or l.summary.strip()) for l in lessons if l.id != lesson.id))
            others = [v for v in others if v and v != answer]
            rng = random.Random(lesson.id)
            rng.shuffle(others)
            distractors = others[:3]
            for fallback in ["В этой теме любые исходные данные всегда дают одинаковый результат.", "Для этой темы не требуется проверять условия применения правил.", "Примеры этой темы заменяют общее правило и подходят без ограничений."]:
                if len(distractors) < 3:
                    distractors.append(fallback)
            options = [answer, *distractors]
            rng.shuffle(options)
            s.add(QuizQuestion(lesson_id=lesson.id, prompt=f'Какое объяснение соответствует теме «{lesson.title}»?', options=options, correct_index=options.index(answer), explanation=answer))
    s.flush()


if __name__ == '__main__':
    with SessionLocal.begin() as s:
        seed(s)
    print('Course quiz questions seeded (existing questions preserved).')
