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

---

# Проверка регистрации и миграции 0006

Дата: 16 ноября 2026. PostgreSQL 17, отдельная БД `mini_lms_test_auth_0006`.

## Изменения

- Гость на главной странице переходит к регистрации. Регистрация и обычный вход предлагают роли `student` / `teacher`. Для администратора — `/admin/login`.
- Регистрация создаёт `users`, `credentials`, `user_profiles`, `login_sessions`; выбранная роль записывается через внешний ключ `users.role_id → roles.id`. Пароль хранится только как хеш PBKDF2.
- Администратор во вкладке «Ученики» видит всех пользователей с ролью `student`, в том числе без зачислений. Поиск работает по имени и email, без учёта регистра. Учитель сохраняет доступ только к ученикам своих курсов.
- Миграция `0006_auth_hardening`: таблица `login_attempts`, PK `email`, ограничения нижнего регистра и неотрицательного счётчика; индекс `login_sessions(expires_at)`. Индекс `login_sessions(user_id)` уже создан миграцией `0003` и сохраняется при downgrade `0006`.
- Неудачный пароль увеличивает счётчик по нормализованному email, включая неизвестные email. Успешный вход очищает счётчик. Выбранная при входе роль проверяется по БД и не меняет роль аккаунта. Автоматическая блокировка по `locked_until` в эту задачу не входит.

## Миграции

Проверено: `upgrade head → downgrade 0005 → upgrade head` и `alembic check`.
Результат: `No new upgrade operations detected.` При downgrade таблица попыток и индекс срока удаляются, прежний индекс пользователя остаётся.
После проверки миграция применена к локальной учебной БД; `alembic check` также чистый.

## Очистка сессий и EXPLAIN

Команда: `psql ... -f database/queries/session_cleanup.sql`.
Файл сначала показывает план, затем удаляет только сессии с `expires_at <= now()`.

Для сравнения в тестовой транзакции создано 100 000 сессий: 100 просроченных и 99 900 активных, выполнен `analyze login_sessions`.
Индекс срока временно удалён только внутри этой тестовой транзакции, затем создан снова. Принудительное отключение Seq Scan не использовалось.

До индекса:

```text
Delete on login_sessions  (cost=0.00..2834.00 rows=0 width=0)
  ->  Seq Scan on login_sessions  (cost=0.00..2834.00 rows=117 width=6)
        Filter: (expires_at <= now())
```

После индекса:

```text
Delete on login_sessions  (cost=0.29..11.34 rows=0 width=0)
  ->  Index Scan using ix_login_sessions_expires_at on login_sessions  (cost=0.29..11.34 rows=117 width=6)
        Index Cond: (expires_at <= now())
```

Удалено ровно 100 просроченных сессий; осталось 99 900 активных. Тестовые данные откачены. Это оценка стоимости плана, а не измерение времени. На маленькой таблице PostgreSQL может выбрать Seq Scan.

## Проверки приложения

```bash
RUN_DB_TESTS=1 DATABASE_URL=postgresql+psycopg://mini_lms@127.0.0.1:55434/mini_lms_test_auth_0006 PYTHONPATH=backend .venv/bin/pytest backend/tests/test_registration_roles.py backend/tests/test_learning.py backend/tests/test_auth_acceptance.py -q -rxX
```

Результат: **34 passed, 5 xfailed**, 80.13 с. Проверены обе роли регистрации, видимость незачисленного ученика администратору, поиск по email, запрет доступа учителю/гостю, проверка роли при входе, счётчик неудачных входов, сброс счётчика после успеха, запреты отрицательного счётчика, повторного email и email в верхнем регистре.
Пять прежних xfail: автоматическая блокировка, сложность и смена пароля, автоматическая очистка сессий, запрет самостоятельного зачисления персоналу.

`npm run build` прошёл. Через работающий Vite проверены вход администратора с ролью `admin`, список всех учеников (38 записей), поиск по email и HTTP 200 страницы регистрации. Визуальная проверка браузера не выполнена: управление браузером недоступно в этой сессии.
