# ER-диаграмма Mini LMS

Автор: Олжас. Снято с `backend/app/models.py` на `main` (миграция `0005`, коммит `0ee0a96`) 9 ноября 2026. Источник правды — модели и миграции; при изменении схемы диаграмму обновлять в том же PR.

GitHub показывает диаграмму сразу. В VS Code нужно расширение с поддержкой Mermaid (например, «Markdown Preview Mermaid Support»).

## Авторизация (крупно)

Сверено 16 ноября 2026 с `main` (`0ab8cc0`): схема авторизации с 9 ноября не менялась.

```mermaid
erDiagram
    roles ||--o{ users : "одна роль"
    users ||--o| credentials : "пароль (может не быть)"
    users ||--o{ login_sessions : "активные входы"
    users ||--o| user_profiles : "профиль"
    users ||--o{ courses : "автор курса"
    courses ||--o{ course_teachers : "назначенные преподаватели"
    users ||--o{ course_teachers : "назначен"
    users ||--o{ enrollments : "записан"
    courses ||--o{ enrollments : "ученики"

    roles {
        int id PK
        string name "student | teacher | admin"
    }
    users {
        int id PK
        string email "UNIQUE, нижний регистр"
        string display_name
        int role_id FK "меняет только админ"
    }
    credentials {
        int user_id PK,FK "CASCADE"
        string password_hash "pbkdf2_sha256, 600000 итераций, соль"
    }
    login_sessions {
        string token_hash PK "SHA-256 от токена из cookie"
        int user_id FK "CASCADE"
        timestamptz expires_at "вход + 7 дней"
    }
    course_teachers {
        int course_id PK,FK
        int user_id PK,FK
    }
    enrollments {
        int user_id PK,FK
        int course_id PK,FK
    }
```

Как читать: роль одна на пользователя и проверяется по БД при каждом запросе, поэтому смена роли действует сразу. В cookie лежит случайный токен, а в БД только его хеш: утечка таблицы `login_sessions` не даёт войти. У старых seed-аккаунтов нет строки в `credentials`, войти под ними нельзя. Доступ преподавателя к курсу: он автор (`courses.teacher_id`) или назначен (`course_teachers`). Доступ ученика: курс опубликован и есть строка в `enrollments`.

Чего в схеме нет (пробелы AUTH-GAP-1 и AUTH-GAP-4, см. [AUTH_TECHNICAL_DESCRIPTION.md](AUTH_TECHNICAL_DESCRIPTION.md)): учёта неудачных входов и индекса `login_sessions (expires_at)` для очистки просроченных сессий.

## Квиз (крупно)

```mermaid
erDiagram
    users ||--o{ enrollments : "записан"
    courses ||--o{ enrollments : "имеет учеников"
    courses ||--|{ modules : "состоит из"
    modules ||--|{ lessons : "состоит из"
    lessons ||--o| quiz_questions : "1 вопрос на урок"
    users ||--o{ lesson_progress : "проходит"
    lessons ||--o{ lesson_progress : "отмечен"
    users ||--o{ quiz_attempts : "сдаёт"
    courses ||--o{ quiz_attempts : "итоговый квиз курса"

    quiz_questions {
        int id PK
        int lesson_id FK "UNIQUE, CASCADE"
        string prompt "не пустой"
        json options "ровно 4 варианта"
        int correct_index "0..3, не отдаётся ученику"
        string explanation
    }
    quiz_attempts {
        int id PK
        int user_id FK "CASCADE, индекс"
        int course_id FK "CASCADE, индекс"
        json answers "выбор + снимок вопросов"
        int correct "0..total"
        int total "больше 0"
        timestamptz created_at
    }
    lesson_progress {
        int user_id PK,FK
        int lesson_id PK,FK
        bool completed "все true = квиз открыт"
    }
    enrollments {
        int user_id PK,FK
        int course_id PK,FK
    }
```

Как читать: квиз — это не отдельная таблица, а набор `quiz_questions` всех уроков курса. Квиз открывается, когда у ученика `completed = true` по каждому уроку курса и у каждого урока есть вопрос. Каждая отправка — новая строка `quiz_attempts` с подсчитанным сервером результатом.

## Вся схема

```mermaid
erDiagram
    roles ||--o{ users : "роль"
    users ||--o| user_profiles : "профиль"
    users ||--o| credentials : "пароль"
    users ||--o{ login_sessions : "сессии"
    users ||--o{ courses : "автор (teacher_id)"
    courses ||--o{ course_teachers : "назначенные преподаватели"
    users ||--o{ course_teachers : "назначен"
    courses ||--|{ modules : ""
    modules ||--|{ lessons : ""
    users ||--o{ enrollments : ""
    courses ||--o{ enrollments : ""
    users ||--o{ lesson_progress : ""
    lessons ||--o{ lesson_progress : ""
    users ||--o{ grades : "ученик"
    users ||--o{ grades : "автор оценки"
    courses ||--o{ grades : ""
    lessons ||--o{ grades : "урок или практика"
    lessons ||--o| quiz_questions : ""
    users ||--o{ quiz_attempts : ""
    courses ||--o{ quiz_attempts : ""

    roles {
        int id PK
        string name "student | teacher | admin"
    }
    users {
        int id PK
        string email "UNIQUE, нижний регистр"
        string display_name
        int role_id FK
        timestamptz created_at
    }
    user_profiles {
        int user_id PK,FK
        string bio
    }
    credentials {
        int user_id PK,FK
        string password_hash "PBKDF2-SHA256"
    }
    login_sessions {
        string token_hash PK
        int user_id FK
        timestamptz expires_at
    }
    courses {
        int id PK
        string slug "UNIQUE"
        string title
        string description
        int teacher_id FK
        string status "draft | published"
        timestamptz created_at
    }
    course_teachers {
        int course_id PK,FK
        int user_id PK,FK
    }
    modules {
        int id PK
        int course_id FK
        string title
        int position "UNIQUE с course_id"
    }
    lessons {
        int id PK
        int module_id FK
        string title
        string content
        int position "UNIQUE с module_id"
        string summary
        string practice
        int duration_minutes
        string video_url
        int video_duration
    }
    enrollments {
        int user_id PK,FK
        int course_id PK,FK
        timestamptz created_at
    }
    lesson_progress {
        int user_id PK,FK
        int lesson_id PK,FK
        bool completed
        json intervals
        float watched_seconds
        bool demo
        timestamptz updated_at
    }
    grades {
        int id PK
        int user_id FK
        int course_id FK
        int lesson_id FK "NULL для итога курса"
        string kind "lesson | practice | course"
        int score "0..100"
        string comment
        int author_id FK
        bool demo
        timestamptz updated_at
    }
    quiz_questions {
        int id PK
        int lesson_id FK "UNIQUE"
        string prompt
        json options
        int correct_index
        string explanation
    }
    quiz_attempts {
        int id PK
        int user_id FK
        int course_id FK
        json answers
        int correct
        int total
        timestamptz created_at
    }
```

## Замечания аналитика к схеме

| № | Наблюдение | Последствие | Предложение |
|---|---|---|---|
| E1 | Результат квиза живёт в `quiz_attempts`, а не в `grades` | Журнал и карточка ученика его не видят (GAP-1, GAP-2) | Не копировать в `grades`, а показывать лучшую попытку расчётом |
| E2 | `options` и `answers` хранятся в JSON | Нельзя поставить FK на вариант; ограничения проверяет CHECK (`json_array_length = 4`) и сервер | Для объёма курса достаточно; при редакторе вопросов вынести варианты в таблицу |
| E3 | У `quiz_attempts` нет ограничения на число попыток | Попытки бесконечные, это осознанное решение (раздел 3 описания) | Если введут лимит, нужен счётчик под блокировкой, как у оценок |
| E4 | Нет индекса `(user_id, course_id)` у `quiz_attempts`, есть два отдельных | При текущих объёмах не проблема | Добавлять только после EXPLAIN на реальных данных |
