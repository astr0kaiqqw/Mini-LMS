# Mini LMS · Учебная мастерская

Учебный проект команды из четырёх человек. Самостоятельный макет с маршрутами обучения: студент выбирает курс, изучает урок, проходит тест и видит результат; преподаватель управляет материалами. **Полный сценарий пока не реализован.**

Репозиторий: https://github.com/astr0kaiqqw/Mini-LMS

## Текущий статус
Неделя 10, каркас 0.1.0. План развития — недели 11–15. Интерфейс использует вымышленные локальные примеры. Переключение ролей — просмотр макетов, не авторизация. Формы не создают аккаунт; тест не сохраняет попытку; кнопки будущих функций отмечены неделей. В БД только roles, users, user_profiles. Курсов, заданий и оценок в БД пока нет.

Demo API не записывает данные и не требует входа. Никакие защищённые реальные данные через него не публикуются. Подробности: [состояние](docs/PROJECT_STATUS.md), [намеренно не сделано](docs/NOT_DONE_ON_PURPOSE.md).

## Команда
| Участник | Зона |
|---|---|
| Ануар | Frontend и backend |
| Ерасыл | Frontend и backend, интеграция quizzes |
| Олжас | Аналитика, требования, распределение задач, техническое описание |
| Руслан | Только БД: схема, миграции, запросы, индексы, проверки, права, backup и документация |

На ближайший отчёт Руслан готовит **optimization errors and test report** по БД. Исходные обещания и зависимости зафиксированы в PROJECT_STATUS; помощник не объявляет их выполненными за участников.

## Стек
React 19 + TypeScript + Vite; Python 3.13+ + FastAPI; PostgreSQL 17 + SQLAlchemy 2 + Alembic. SQLAlchemy связывает код с таблицами; Alembic хранит версии схемы. Redis, брокеры сообщений и другие сервисы пока не нужны.

## Быстрый просмотр frontend
Нужен Node.js 22.12+ (рекомендуется 24). Из корня:
```bash
cd frontend
npm ci
npm run dev
```
Открыть http://127.0.0.1:5173. Макет работает и без backend; каталог явно сообщает об этом. Маршруты: /, /courses, /courses/data-thinking, /courses/data-thinking/lessons/1, /assignments, /quiz, /profile, /login, /register, /teacher, /admin, /roadmap. Для панелей выберите соответствующую demo-роль в меню. Роль и ответы при перезагрузке сбрасываются.

## Полный локальный запуск
Нужны Docker Desktop и Make. Frontend, backend и PostgreSQL запускаются одной командой из корня проекта:
```bash
make up
```
`make up` создаёт `.env` из примера, собирает и запускает весь проект. Frontend: http://127.0.0.1:5173, backend: http://127.0.0.1:8000, PostgreSQL: порт 55432. Порты можно изменить в `.env`. Миграции и demo seed выполняются при старте backend.

Основные команды: `make logs`, `make ps`, `make test`, `make restart`, `make down`. Полный список: `make help`. Данные PostgreSQL сохраняются после `make down`.

API docs: http://127.0.0.1:8000/docs
- GET /health/live — процесс работает, режим demo.
- GET /health/ready — проверка соединения и наличия начальной таблицы users; 503 при недоступной БД/схеме. Это не полная проверка всех миграций.
- GET /api/demo/courses — три примера, persisted=false.
- GET /api/demo/courses/{id} — пример курса или 404.

В seed три записи: student@example.test, teacher@example.test, admin@example.test. **Паролей и входа у них нет.** Это строки для проверки схемы, а не работающие аккаунты.

В `backend/requirements.txt` перечислены прямые зависимости, в `requirements.lock.txt` — проверенные точные версии всей цепочки. При обновлении зависимостей обновляйте оба файла и повторяйте проверки.

## Проверки
Из корня с активированной .venv:
```bash
PYTHONPATH=backend pytest backend/tests -q
alembic upgrade head --sql
cd frontend
npm run build
```
Проверки PostgreSQL без специального флага пропускаются. Настоящий прогон: [DB_WORKFLOW](docs/DB_WORKFLOW.md); использовать только mini_lms_test_*.

GitHub Actions собирает frontend, запускает API-тесты, миграции, seed и проверки на PostgreSQL 17. Наличие workflow не означает успешный удалённый запуск: результат смотреть во вкладке Actions. Фактический локальный отчёт — [VALIDATION](docs/VALIDATION.md).

Остановка: `make down`. Данные PostgreSQL остаются в volume. Не используйте `docker compose down -v`, если хотите сохранить их.

## Структура
```text
frontend/                 React, страницы и локальные mock-данные
backend/app/              FastAPI, настройки, модели и demo API
backend/tests/            API и отдельные PostgreSQL-проверки
database/migrations/      единственный каталог миграций Alembic
database/seeds/           небольшой повторяемый seed
database/queries/         SQL для проверок и исходного плана
database/docs/            инструкция backup/restore
docs/                     план, обучение, workflow и отчёты
.github/                  PR, Issues, CI
```

## Документация
- [План недель 11–15](docs/WEEKLY_PLAN.md)
- [Реестр будущих задач](docs/NOT_DONE_ON_PURPOSE.md)
- [Обучение БД](docs/DATABASE_GUIDE.md)
- [Командная работа с БД](docs/DB_WORKFLOW.md)
- [Техническое описание quizzes](docs/QUIZ_TECHNICAL_DESCRIPTION.md)
- [Проверки БД](docs/DB_TEST_PLAN.md), [отчёт](docs/DB_TEST_REPORT.md), [ошибки](docs/DB_ERROR_LOG.md)
- [Промпт для Codex в VS Code](docs/CODEX_HANDOFF.md)
- [GitHub для новичков](docs/GITHUB_FLOW.md), [Issues W11](docs/WEEK_11_ISSUES.md)

## Git
Рабочие ветки: main → develop → feature/<name>-<task>; БД — feature/db-<task>. Коммиты на английском, Conventional Commits: `feat(db): add courses table`. Схему меняет Руслан через миграции. Новые функции идут через PR в develop, выпуск — через PR в main. Защита веток включается отдельно в GitHub.

Если первый коммит ещё не создан:
```bash
git status
git add README.md .gitignore .env.example compose.yaml alembic.ini frontend backend database docs .github
git commit -m "feat: scaffold Mini LMS workshop"
git branch -M main
git push -u origin main
git switch -c develop
git push -u origin develop
```
Эти команды только для первоначально пустого репозитория; если коммит/ветки уже существуют, сначала проверьте `git log` и `git branch -a`. Не повторяйте создание и не используйте force push.
