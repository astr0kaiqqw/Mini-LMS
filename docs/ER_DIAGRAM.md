# ER-диаграмма Mini LMS

Автор: Олжас. Снято с `backend/app/models.py` на `main` (миграция `0005`, коммит `0ee0a96`) 9 ноября 2026. Источник правды — модели и миграции; при изменении схемы диаграмму обновлять в том же PR.

GitHub показывает диаграмму сразу. В VS Code нужно расширение с поддержкой Mermaid (например, «Markdown Preview Mermaid Support»).

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

