# Исходный отчёт БД

Дата: 5 ноября 2026 года, учебная неделя 10. Проверки выполнены помощником при подготовке каркаса. Руслан должен воспроизвести их, объяснить результат и зафиксировать собственный вклад на неделе 11. Задача: **optimization errors and test report**.

## Окружение
macOS ARM64; Python 3.14.7; PostgreSQL 17.11 aarch64 в Docker; SQLAlchemy 2.0.44; Alembic 1.17.1. Изолированная база mini_lms_test_local на localhost:55432. Основная демо-БД mini_lms. Настоящих пользовательских данных нет.

## Результаты
| Проверка | Ожидалось | Фактически | Статус |
|---|---|---|---|
| DBT-01: upgrade head на новой БД | минимальная схема | roles/users/user_profiles и alembic_version, revision 0001 | пройдено |
| DBT-02: alembic check | нет расхождений ORM/DDL | No new upgrade operations detected | пройдено |
| DBT-03: seed дважды | без дублей | по одному admin/student/teacher, 3 профиля; автоматическая проверка совпадения количества | пройдено |
| DBT-04: повторный email | IntegrityError | отклонён, savepoint откатан | пройдено |
| DBT-05: неизвестный role_id | нарушение FK | запись отклонена | пройдено |
| DBT-06: неверные значения | CHECK запрещает | uppercase email, email без @, пустое имя и superuser отклонены | пройдено |
| DBT-07: удаление временного пользователя | удалён его профиль, роль остаётся | автоматическая проверка подтвердила | пройдено |
| DBT-08: downgrade base → upgrade head | повторяемая схема | обе команды успешны, alembic check без различий, seed повторён | пройдено |
| DBT-09: отчёт ролей и план email | корректный результат | 1 пользователь каждой роли, запрос по email вернул 1 строку | пройдено |
| DBT-10: нагрузка и оптимизация до/после | воспроизводимые замеры | не запускалось: только 3 демонстрационные строки | не запускалось |

## Команды и доказательства
Точный безопасный порядок подготовки: [DB_WORKFLOW](DB_WORKFLOW.md).

```bash
# После создания отдельной mini_lms_test_local:
export DATABASE_URL=postgresql+psycopg://mini_lms:local_demo_only@localhost:55432/mini_lms_test_local
.venv/bin/alembic upgrade head
.venv/bin/alembic check
PYTHONPATH=backend .venv/bin/python database/seeds/demo_users.py
PYTHONPATH=backend .venv/bin/python database/seeds/demo_users.py
RUN_DB_TESTS=1 PYTHONPATH=backend .venv/bin/pytest backend/tests -q
# Результат: 13 passed, 1 warning (5 API + 8 DB).
# Только на этой одноразовой тестовой БД:
.venv/bin/alembic downgrade base
.venv/bin/alembic upgrade head
.venv/bin/alembic check
PYTHONPATH=backend .venv/bin/python database/seeds/demo_users.py
unset DATABASE_URL
```

План из database/queries/account_checks.sql:
```text
Index Scan using uq_users_email on users
Index Cond: ((email)::text = 'student@example.test'::text)
actual time=0.004..0.004 rows=1 loops=1
Buffers: shared hit=2
Planning Time: 0.022 ms
Execution Time: 0.010 ms
```

Это единичный исходный замер на крошечной прогретой БД. Он не доказывает поведение под нагрузкой или ускорение. Изменений индексов по итогам замера не сделано: UNIQUE(email) уже создаёт нужный индекс. Сравнение до/после не применимо, поскольку оптимизации не проводились. Существующий FK-индекс role_id добавлен в скелет без заявления о доказанном ускорении.

## Ошибки и ограничения
Подтверждённых дефектов БД в выполненных сценариях нет; журнал — DB_ERROR_LOG.md. Занятый порт 5432 решён отдельным портом 55432; это проблема локального окружения. Есть неблокирующее предупреждение DeprecationWarning в Starlette TestClient из-за anyio; тесты успешны.

Не проверены: масштабные данные, конкурентное завершение попыток (их таблиц ещё нет), права отдельной ограниченной роли PostgreSQL, backup/restore, рабочие аккаунты. Это задачи W12–15, не результаты текущего отчёта.
