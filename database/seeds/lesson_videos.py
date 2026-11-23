"""YouTube video for every seeded lesson (W13, analyst: Olzhas).

One video per lesson, keyed by course slug and exact lesson title from curriculum.py.
Video fields: YouTube id, exact duration in seconds (the 90% watch rule depends on it),
channel and original title. Selection rules and check results: docs/LESSON_VIDEOS.md.
Re-check availability before a demo: python testing/check_lesson_videos.py
"""
from typing import NamedTuple

CHECKED_ON = "2026-11-23"


class Video(NamedTuple):
    youtube_id: str
    seconds: int
    channel: str
    title: str


def watch_url(youtube_id: str) -> str:
    """Canonical form stored in lessons.video_url (see VIDEO_TECHNICAL_DESCRIPTION, Y2)."""
    return f"https://www.youtube.com/watch?v={youtube_id}"


VIDEOS: dict[str, dict[str, Video]] = {
    'calculus-1': {
        'Функции и область определения': Video('FENzriAjRP4', 363, 'Видеокурсы DA VINCI', '9 класс, 15 урок, Определение числовой функции. Область определения, область значения функции'),
        'Графики и преобразования': Video('XbstdyaZop0', 519, 'INTENSIVKURS - Учебный Центр для Школьников', 'ГРАФИК ФУНКЦИЙ — Сдвиги Графика Функции, Как строить Графики Функции // Алгебра 8 класс'),
        'Предел последовательности': Video('q8XtKMiBISc', 677, 'Riemann', 'Как понять предел последовательности за 10 минут?'),
        'Предел функции': Video('5QCVBpIntcs', 528, 'MEKTEП OnLine MATEMATИKA', 'Предел функции в точке. 10 класс.'),
        'Непрерывность': Video('nXUEw07DWkw', 944, 'Борис Трушин', '✓ Непрерывность функции в точке. Непрерывность многочленов | матан #019 | Борис Трушин'),
        'Производная как скорость': Video('qrVpZGVXRuo', 690, 'INTENSIVKURS - Учебный Центр для Школьников', 'АЛГЕБРА С НУЛЯ — Что такое Производная?'),
        'Правила дифференцирования': Video('6N6c-sKRLEw', 465, 'физика ОГЭ математика ЕГЭ - Романов Владимир', 'ПРОИЗВОДНАЯ СТЕПЕННОЙ ФУНКЦИИ решение производных функций'),
        'Цепное правило': Video('QLffopgx7uc', 741, 'MEKTEП OnLine MATEMATИKA', 'Производная сложной функции. 10 класс.'),
        'Экстремумы': Video('j5r6AVv9h2Q', 775, 'INTENSIVKURS - Учебный Центр для Школьников', 'АЛГЕБРА С НУЛЯ — Точки Экстремума Функции'),
        'Определённый интеграл': Video('5xFJBunQYSI', 538, 'MEKTEП OnLine MATEMATИKA', 'Определенный интеграл. 11 класс.'),
    },
}
