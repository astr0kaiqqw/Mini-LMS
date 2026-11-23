# Видео YouTube: сценарии приёмки

Автор: Олжас. Основание: [техническое описание](../docs/VIDEO_TECHNICAL_DESCRIPTION.md), правила V1–V8, требования Y1–Y12, пробелы VID-GAP-1…6.
Автотесты: `backend/tests/test_video_acceptance.py` (ID сценария в имени теста). Доступность видео: `testing/check_lesson_videos.py`.

## Прогон 23 ноября 2026

- Код: `main`, коммит `6769e34`, миграция `0008`.
- Окружение: Windows 11, PostgreSQL 17 (отдельная БД `mini_lms_test_video`), Python 3.14.3.
- Команды:

```bash
export DATABASE_URL=postgresql+psycopg://mini_lms@127.0.0.1:55433/mini_lms_test_video
alembic upgrade head
RUN_DB_TESTS=1 PYTHONPATH=backend pytest backend/tests/test_video_acceptance.py -q -rxX
python testing/check_lesson_videos.py
```

- Итог: **4 passed, 8 xfailed** за 1 мин 35 с; доступность **120 / 120**.
- VD-01…03 не требуют БД и проходят и без `RUN_DB_TESTS`.

## Каталог

| ID | Приор. | Критерий | Проверка | Ожидается | Факт 23.11 | Статус |
|---|---|---|---|---|---|---|
| VD-01 | P1 | K7 | Сверить каталог с `curriculum.py` | 12 курсов, у каждого урока ровно одно видео, названия совпадают | так и есть | пройдено |
| VD-02 | P1 | K4, K7 | ID, длительность, автор, название, повторы | ID из 11 символов, 180–1500 с, повторов нет | 120 уникальных, 216–1297 с | пройдено |
| VD-03 | P2 | K5 | Сумма видео на курс | ≤ 150 мин | 83–139 мин | пройдено |
| VD-04 | P1 | K3 | `check_lesson_videos.py` | Все 200 | 120 / 120 | пройдено |
| VD-05 | P1 | K3 | Видео с запретом встраивания (`fcvTxTUVRsM`) и несуществующее | 401 и 404 — скрипт их ловит | 401, 404 | пройдено, видео заменено |

