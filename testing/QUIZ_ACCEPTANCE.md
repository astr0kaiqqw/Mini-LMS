# Итоговый квиз: сценарии приёмки

Автор: Олжас. Основание: [техническое описание](../docs/QUIZ_TECHNICAL_DESCRIPTION.md), правила R1–R12 и пробелы GAP-1…GAP-6.
Автотесты: `backend/tests/test_quiz_acceptance.py` (ID сценария в имени теста).

## Прогон 9 ноября 2026

- Код: `main`, коммит `0ee0a96`, миграция `0005`.
- Окружение: Windows 11, PostgreSQL 17.3 (отдельная БД `mini_lms_test_quiz`), Python 3.14.3.
- Команда:

```bash
export DATABASE_URL=postgresql+psycopg://mini_lms@127.0.0.1:55433/mini_lms_test_quiz
alembic upgrade head
RUN_DB_TESTS=1 PYTHONPATH=backend pytest backend/tests/test_quiz_acceptance.py -q -rx
```

- Итог: **17 passed, 2 xfailed** (xfail — подтверждённые пробелы GAP-1 и GAP-2). Весь набор backend: 41 passed до добавления файла.

Подготовка в каждом тесте: seed `learning_demo` + `course_quizzes`, курс Calculus 1 (10 уроков, 10 вопросов), ученик `calculus-1.student2` (50% прогресса), ученик другого курса `english.student1`, преподаватель `instructor`. Всё в транзакции, которая откатывается.

## Доступ и открытие квиза

| ID | Приор. | Правило | Шаги | Ожидается | Факт 09.11 | Статус |
|---|---|---|---|---|---|---|
| QZ-01 | P1 | — | GET и POST без cookie | 401 | 401 / 401 | пройдено |
| QZ-02 | P1 | R3 | Ученик с 50% открывает квиз и отправляет ответы | `unlocked=false`, вопросов нет, POST 403, попыток 0 | так и есть | пройдено |
| QZ-03 | P1 | R5 | Ученик завершил все уроки и открывает квиз | 10 вопросов, нет `correct_index` и `explanation` | 10 вопросов, ключей нет | пройдено |
| QZ-08 | P1 | R3 | Ученик другого курса: GET и POST | 403 | 403 / 403 | пройдено |
| QZ-09 | P1 | R11 | Преподаватель: GET и POST | Видит ключи; POST 403 | так и есть | пройдено |
| QZ-10 | P2 | R3 | Курс переведён в черновик, записанный ученик открывает квиз | 403 | 403 | пройдено |

