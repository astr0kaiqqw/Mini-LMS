# Резервирование и восстановление

<!-- TODO(W15, Руслан): DB-05 — восстановить дамп в отдельную БД, сверить данные и проверить ограниченную роль приложения. -->

Сейчас подготовлена инструкция, а не доказательство работающего резервирования. Не используйте её без проверки имён окружения. Команды ниже рассчитаны на локальный compose с ролью mini_lms и БД mini_lms. Дамп содержит данные — не коммитить и хранить с ограниченными правами.

```bash
mkdir -p work/backups
chmod 700 work/backups
(umask 077; docker compose exec -T postgres pg_dump -U mini_lms -d mini_lms -Fc > work/backups/mini_lms.dump)
docker compose exec postgres createdb -U mini_lms mini_lms_test_restore
docker compose exec -T postgres pg_restore -U mini_lms -d mini_lms_test_restore --no-owner --no-privileges --exit-on-error < work/backups/mini_lms.dump
docker compose exec postgres psql -U mini_lms -d mini_lms_test_restore -c 'SELECT count(*) FROM users; SELECT version_num FROM alembic_version;'
```

Восстановление выполняется в новую пустую mini_lms_test_restore, не в исходную БД. Если имя занято — создайте новое; не удаляйте существующую БД автоматически. Проверить exit code каждой команды и размер дампа, затем сравнить количество и ключевые значения строк, FK/UNIQUE/CHECK и доступность чтения через backend с новым DATABASE_URL. Зафиксировать дату, версию PostgreSQL, объём, время и результаты. Проверить не только count, но и контрольный набор пользователей/ролей.

Перед реальным размещением: отдельная роль миграций, роль API с минимальными GRANT, запрет DDL роли API, отдельная read-only роль для отчётов. Протестировать, что SELECT/разрешённые записи работают, а ALTER/DROP и доступ к закрытым данным запрещены. Эти роли сейчас не созданы. Локальный compose использует роль-владельца для удобства разработки.
