# Отчёт аналитика, неделя 13

Олжас, системный аналитик. Тема недели: видео с YouTube к каждому уроку, чтобы курсы были не только текстом.

## Результат

| Документ | Что в нём |
|---|---|
| [LESSON_VIDEOS.md](LESSON_VIDEOS.md) | **Каталог: 120 видео к 120 урокам**, критерии отбора K1–K7, как шёл подбор, таблицы по курсам |
| `database/seeds/lesson_videos.py` | Тот же каталог в виде данных для кода: ID, точная длительность, автор, название |
| `testing/check_lesson_videos.py` | Проверка, что видео не удалены и их можно встраивать на сайт |
| [VIDEO_TECHNICAL_DESCRIPTION.md](VIDEO_TECHNICAL_DESCRIPTION.md) | Как сейчас (V1–V8), требования Y1–Y12, схема учёта просмотра, пробелы VID-GAP-1…6, риски, решения D1–D6 |
| [../testing/VIDEO_ACCEPTANCE.md](../testing/VIDEO_ACCEPTANCE.md) | Сценарии приёмки: 11 автоматических, 11 ручных в браузере |
| `backend/tests/test_video_acceptance.py` | Автотесты: 4 проходят, 8 фиксируют пробелы (xfail) |
| [VIDEO_TASKS.md](VIDEO_TASKS.md) | **Задания команде:** Ануар — ссылки и API, Руслан — миграция и seed, Ерасыл — плеер и форма, tilektes-ismail — проверки БД |
| [ER_DIAGRAM.md](ER_DIAGRAM.md) | Новый раздел «Видео урока», замечания E5, E6 |

