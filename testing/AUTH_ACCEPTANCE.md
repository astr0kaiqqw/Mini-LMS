# Авторизация: сценарии приёмки

Автор: Олжас. Основание: [техническое описание](../docs/AUTH_TECHNICAL_DESCRIPTION.md), правила A1–A16, пробелы AUTH-GAP-1…7.
Автотесты: `backend/tests/test_auth_acceptance.py` (ID сценария в имени теста).

## Прогон 16 ноября 2026

- Код: `main`, коммит `0ab8cc0`, миграция `0005`.
- Окружение: Windows 11, PostgreSQL 17.3 (отдельная БД `mini_lms_test_auth`), Python 3.14.3.
- Команда:

```bash
export DATABASE_URL=postgresql+psycopg://mini_lms@127.0.0.1:55433/mini_lms_test_auth
alembic upgrade head
RUN_DB_TESTS=1 PYTHONPATH=backend pytest backend/tests/test_auth_acceptance.py -q -rxX
```

- Итог: **16 passed, 5 xfailed** за 3 мин 31 с. xfail — подтверждённые пробелы AUTH-GAP-1…5.

Подготовка в каждом тесте: seed `learning_demo` в транзакции, которая откатывается. Пароль demo-аккаунтов `LearnDemo2026!`.

## Вход

| ID | Приор. | Правило | Шаги | Ожидается | Факт 16.11 | Статус |
|---|---|---|---|---|---|---|
| AU-01 | P1 | A5 | Неверный пароль; несуществующий email | Оба 401, одинаковый текст | 401 / 401, «Неверный email или пароль» | пройдено |
| AU-02 | P2 | A2 | Вход с `  CALCULUS-1.Student1@... ` | 200 | 200 | пройдено |
| AU-03 | P1 | A6 | Вход старым seed-аккаунтом без пароля | 401 | 401 | пройдено |
| AU-04 | P1 | A7, A8 | Проверить `Set-Cookie` и тело ответа | `HttpOnly`, `SameSite=Strict`, `Max-Age=604800`; нет пароля, хеша, токена | так и есть | пройдено |

