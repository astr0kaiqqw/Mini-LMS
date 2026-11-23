# Видео YouTube: задания команде

Автор: Олжас. Основание: пробелы VID-GAP-1…6 из [технического описания](VIDEO_TECHNICAL_DESCRIPTION.md).
Срок: до отчёта W14, если на встрече не решим иначе. Перед началом — встреча по решениям D1–D6 (15 минут).

**Готовый вклад аналитика:** каталог из 120 видео ([LESSON_VIDEOS.md](LESSON_VIDEOS.md), данные — `database/seeds/lesson_videos.py`), скрипт проверки доступности, приёмочные тесты.

**Как понять, что задание готово:** у задания есть тест в `backend/tests/test_video_acceptance.py` с пометкой `xfail(strict=True)` или ручной сценарий в [VIDEO_ACCEPTANCE.md](../testing/VIDEO_ACCEPTANCE.md). Сделал задание — тест падает с **XPASS**. Удали строку `@pytest.mark.xfail(...)`, прогони файл, тест должен пройти. Это доказательство в PR.

```bash
RUN_DB_TESTS=1 PYTHONPATH=backend pytest backend/tests/test_video_acceptance.py -q -rxX
```

```mermaid
flowchart LR
    C[VIDEO-CATALOG · 120 видео<br/>Олжас · готово] --> R2
    M[MEET-03 · решения D1–D6<br/>Олжас] --> A1[VIDEO-URL · ссылки и поля API<br/>Ануар]
    M --> R1[DB-VIDEO-1 · миграция 0009<br/>Руслан]
    A1 --> R1
    A1 --> E1[UI-VIDEO-PLAYER · плеер YouTube<br/>Ерасыл]
    A1 --> E2[UI-VIDEO-FORM · форма урока<br/>Ерасыл]
    E1 --> R2[DB-VIDEO-2 · видео в seed<br/>Руслан]
    R1 --> T1[TEST-VIDEO-DB · проверки БД<br/>tilektes-ismail]
    R2 --> Q[ANALYSIS-05 · повторная приёмка<br/>Олжас]
    E2 --> Q
    T1 --> Q
```

> **Порядок важен.** DB-VIDEO-2 вливать только после UI-VIDEO-PLAYER. Урок с видео нельзя завершить кнопкой (V3). Если видео появятся в БД раньше плеера, все 120 уроков станут незавершаемыми, и квизы не откроются.

