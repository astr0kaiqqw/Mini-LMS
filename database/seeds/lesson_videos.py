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
    'linear-algebra': {
        'Векторы': Video('LaR0W-uLi5k', 635, 'МЕКТЕП OnLine ГЕОМЕТРИЯ', 'Координаты вектора. 9 класс.'),
        'Операции с векторами': Video('6dhIlY1DH_M', 468, 'МЕКТЕП OnLine ГЕОМЕТРИЯ', 'Сложение, вычитание, умножение на число векторов через координату. 9 класс.'),
        'Скалярное произведение': Video('KC3wfa8p_8U', 523, 'МЕКТЕП OnLine ГЕОМЕТРИЯ', 'Скалярное произведение векторов. 9 класс.'),
        'Матрицы': Video('vAxpptpYAJo', 556, 'Видеокурсы DA VINCI', 'Линейная алгебра, 1 урок, Матрицы'),
        'Умножение матриц': Video('Ye4lx98j71w', 511, 'физика ОГЭ математика ЕГЭ - Романов Владимир', 'МАТРИЦЫ математика УМНОЖЕНИЕ МАТРИЦ и простейшие операции с матрицами'),
        'Системы линейных уравнений': Video('AWrczMDGTac', 1125, 'Valery Volkov', 'Матричный метод решения систем уравнений'),
        'Метод Гаусса': Video('hZcxW4sgW64', 600, 'Кафедра математики. On-line', 'Решение системы уравнений методом Гаусса'),
        'Определитель и обратимость': Video('UikJ3Gma6H0', 814, 'физика ОГЭ математика ЕГЭ - Романов Владимир', 'ОПРЕДЕЛИТЕЛЬ МАТРИЦЫ 2х2 3х3 4x4 свойства определителя'),
        'Линейная независимость': Video('LaXL4QgQBig', 975, 'Виктор Глазнев', 'Линейная зависимость и  линейная независимость  векторов.'),
        'Собственные векторы': Video('khMBBxLJLcw', 1034, 'Vert Dider', 'Суть линейной алгебры: #14. Собственные векторы и собственные значения [3Blue1Brown]'),
    },
    'english': {
        'Приветствия и представление': Video('zFzek_xKaLA', 487, 'ED', 'Английский для начинающих. Приветствие'),
        'Личные местоимения и be': Video('gZE0DdpwRew', 268, 'Инглиш Шоу: грамматика', 'Урок 1. Глагол To Be в настоящем времени. A1 Elementary. #НЗА'),
        'Артикли и множественное число': Video('eJnejBp9edA', 446, 'Инглекс', 'Артикли в английском | Грамматика английского | Онлайн-школа «Инглекс»'),
        'Present Simple': Video('6Qd1xAikoQc', 322, 'Инглиш Шоу', 'Present Simple. ВСЕ ПРОЩЕ, чем вы думаете!'),
        'Вопросы и отрицания': Video('GOqIL8gYEf0', 465, 'Английский с Еленой Дубровченко', 'Вспомогательные глаголы DO или DOES - Present Simple'),
        'Предлоги места и времени': Video('cgYMtuFa8Iw', 484, 'Skyeng – онлайн-школа иностранных языков', '5 минут, чтобы разобраться в предлогах на английском: метод треугольника'),
        'Present Continuous': Video('wB9Wwizcgvc', 460, 'Английский с Ириной Кузьминой', 'Present Continuous | Простое объяснение для начинающих'),
        'Past Simple': Video('H_q9D6NHEuI', 820, 'ED', 'Past Simple — просто, понятно, быстро | Грамматика английского языка | EnglishDom'),
        'Планы на будущее': Video('MrbUPmpESVY', 824, 'Инглекс', 'Will vs be going to | Грамматика английского | Онлайн-школа «Инглекс»'),
        'Короткое связное письмо': Video('xqBPNN8S2dQ', 415, 'Pro English', 'ЕГЭ Английский - Раздел 4 - личное письмо другу - универсальный шаблон'),
    },
}
