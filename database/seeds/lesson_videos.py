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
    'python-beginners': {
        'Первый запуск и print': Video('ki6mKMyiCWY', 740, '/coderoffka - Изучение Python c нуля', 'Урок 1. Функция print() - Изучение Python с нуля для начинающих'),
        'Переменные и типы': Video('Wnm8Bk4_lBY', 999, 'Информатика без воды', 'Начало покорения Python / № 2 - Переменные и типы данных. Функция type. | КУРС | Питон'),
        'Ввод и преобразование': Video('8hzpSR_Qaj8', 1069, 'selfedu', '#6. Функции print() и input(). Преобразование строк в числа int() и float() | Python для начинающих'),
        'Условия': Video('bmS1QmE6wYM', 534, 'Изучаем мир ИТ / Олег Шпагин / Программирование', 'Уроки Python / Конструкция if elif else - если то иначе - Условная инструкция'),
        'Циклы': Video('sZ0EIwgLblY', 631, 'Иван Викторович', 'Python с нуля. Урок 4 | Циклы (for, while)'),
        'Списки и срезы': Video('Vx3s01Yb1P8', 817, 'selfedu', '#14. Срезы списков и сравнение списков | Python для начинающих'),
        'Словари и множества': Video('W2oO1Y-QDzo', 969, 'Школа itProger / Программирование', 'Уроки Python с нуля / #10 – Словари (dict) и работа с ними'),
        'Функции': Video('DJAlfolEv9A', 691, 'egoroff_channel', '35 Функции (def) в Python. Определение и вызов функции'),
        'Файлы и исключения': Video('zlp6gD7UdOA', 905, 'Иван Викторович', 'Python с нуля. Урок 9 | Файлы и исключения'),
        'Мини-проект: журнал оценок': Video('rIhygmw9HZM', 987, 'egoroff_channel', 'Работаем с JSON в Python. Парсинг JSON, сохраняем JSON в файл'),
    },
    'cpp-beginners': {
        'Компиляция и первая программа': Video('c7Nb0lJHVtU', 570, 'selfedu', '#1. Первая программа на С++ | Язык С++ для начинающих'),
        'Типы и переменные': Video('pwUNLjgw7lY', 404, '#SimpleCode', 'Типы данных в C++. C++ для начинающих. Урок #4.'),
        'Ввод и операторы': Video('mi1YqRF03IQ', 666, 'selfedu', '#2. Ввод-вывод с помощью объектов cin и cout | Язык С++ для начинающих'),
        'Условия': Video('k_YFH3PezqA', 1165, '#SimpleCode', 'If else. Конструкция логического выбора if.  Лесенка if - else if. Примеры использования. Урок #12.'),
        'Циклы': Video('Fh3huPx-kPI', 616, 'Гоша Дударь', 'Уроки C++ с нуля / Урок #6 - Циклы For, While, Do while'),
        'Функции': Video('HFH65-sNQmI', 1165, '#SimpleCode', 'Функции c++ примеры. Синтаксис. Объявление, реализация функции. Параметры, аргументы.  C++ #33'),
        'Строки и vector': Video('KPV89oSv18E', 467, 'Кирилл «Polchasa» Сапожников', 'C++ | std::vector - векторы, как создать, вывести на печать, добавлять и удалять элементы'),
        'Ссылки и const': Video('hZOX-LlUETE', 1192, '#SimpleCode', 'c++ ссылки что это. c++ ссылки и указатели разница. Указатель на ссылку. Для начинающих. Урок #50'),
        'Структуры': Video('EWJqZN7ifI0', 623, '#SimpleCode', 'Структуры в C++ | struct C++. Разница между структурой и классом. Изучение С++ для начинающих.#129'),
        'Файлы и мини-проект': Video('bTysglLJ8No', 981, '#SimpleCode', 'Чтение и запись в файл с++ используя класс fstream c++. Изучение С++ для начинающих. Урок #118'),
    },
    'philosophy': {
        'Философский вопрос': Video('KshafAmECAo', 748, 'SciOne', 'Что такое философия'),
        'Аргумент и вывод': Video('wsLZDC5WmwU', 501, 'Скептический философ', 'Что такое аргумент? Логика (1)'),
        'Логические ошибки': Video('craWARgRa0g', 540, 'Лобстер Sapiens', 'Все логические ошибки за 9 минут'),
        'Знание и убеждение': Video('09gdiwUV7sU', 296, 'ПоТОК сознания', 'Проблема Гетье'),
        'Скептицизм и сомнение': Video('HeTn8E6G73o', 636, 'Гуманитарщина', 'Философия Декарт'),
        'Личность и идентичность': Video('aLOnKTTRrs4', 834, 'Капитан Дрейк', 'Тебя уже давно НЕТ | Тождество личности'),
        'Свобода и ответственность': Video('KZqwxtSq124', 850, 'Скептический философ', 'Свобода воли и детерминизм. Просто и доступно. Лекции по философии (11).'),
        'Этические подходы': Video('XfQYJOuGgpo', 850, 'Иван Куницын | Про нейросети и не только', 'Этические теории – «этика добродетели», утилитаризм и деонтология'),
        'Справедливость и общество': Video('ug1PZi42MgQ', 544, 'Философия за 10 минут', 'Джон Ролз - теория справедливости (За 10 минут)'),
        'Философское эссе': Video('wA5K2_8IZfA', 285, 'Адукар', 'Как правильно писать эссе | Полезные советы | Пример эссе | Эссе онлайн'),
    },
    'cybersecurity': {
        'Активы и модель угроз': Video('gsUOxAHoxbY', 250, 'Цифровая Благодетель', 'МОДЕЛЬ УГРОЗ | Простым языком на примере'),
        'Пароли и MFA': Video('4yCVx8aQ3nM', 226, 'РосКомСвобода', 'Знай! / Менеджер паролей и двухфакторная аутентификация'),
        'Фишинг': Video('6VZL0DJWr7g', 784, 'Первый отдел', 'Фишинг: как мошенники крадут деньги и данные'),
        'Обновления и минимальные права': Video('g8io45pkhXQ', 796, 'Обучение системных администраторов', 'Как устроена кибербезопасность: VPN, NAT, фаервол и принцип минимальных привилегий'),
        'Сети и TLS': Video('nsyLWDtWXk0', 1117, 'QA Studio | Тестирование', 'Как работает шифрование в HTTPS (SSL и TLS)'),
        'Шифрование и хеширование': Video('VbB99SOR8OE', 360, 'hasio', 'Пароли, шифрование, хеширование и СОЛЬ'),
        'Контроль доступа': Video('Jc1cqLk7NmQ', 277, 'MakeIT', 'Идентификация, аутентификация и авторизация простыми словами'),
        'Безопасный ввод': Video('pDvSNaQfuIc', 933, 'CyberYozh', 'SQL-инъекции для начинающих: от теории к практике'),
        'Резервные копии и инциденты': Video('GqCoVdm6odE', 839, 'Обучение системных администраторов', 'Как не потерять данные: резервное копирование и правило 3-2-1 простыми словами'),
        'Мини-аудит учебного приложения': Video('4Ufdf3t3o3Y', 440, 'Reconholic', 'Весь OWASP Top 10 простыми словами'),
    },
    'machine-learning-beginners': {
        'Задачи машинного обучения': Video('ku2oPMPht2I', 697, 'machine learrrning', 'ОБУЧЕНИЕ С УЧИТЕЛЕМ, ОБУЧЕНИЕ БЕЗ УЧИТЕЛЯ, ОБУЧЕНИЕ С ПОДКРЕПЛЕНИЕМ | ЗАДАЧИ МАШИННОГО ОБУЧЕНИЯ'),
        'Табличные данные': Video('wjDns1IYcPg', 216, 'egoroff_channel', 'Анализ данных с помощью Pandas. Вводное занятие'),
        'Разделение данных': Video('5UdOdUgDr-c', 686, 'Школа itProger / Программирование', 'Python Data Science / Урок #3 – Основы машинного обучения (Scikit-learn)'),
        'Подготовка признаков': Video('XsuCOfpf8Ic', 1297, 'machine learrrning', 'StandardScaler| MinMaxScaler | МАСШТАБИРОВАНИЕ ДАННЫХ | МАШИННОЕ ОБУЧЕНИЕ'),
        'Линейная регрессия': Video('rE43fnoQNPw', 461, 'Душкин объяснит', 'Что такое линейная регрессия? Душкин объяснит'),
        'Классификация': Video('9BoVCdedvW8', 1197, 'machine learrrning', 'Логистическая Регрессия | Logistic Regression | Линейная модель для классификации |МАШИННОЕ ОБУЧЕНИЕ'),
        'Метрики': Video('-jplpYLrcdM', 850, 'selfedu', '#23. Показатели precision и recall. F-мера | Машинное обучение'),
        'Переобучение': Video('m7P7bnLxIc4', 746, 'machine learrrning', 'ПЕРЕОБУЧЕНИЕ И НЕДООБУЧЕНИЕ В МАШИННОМ ОБУЧЕНИИ | overfitting, underfitting для регрессии'),
        'Кросс-валидация и baseline': Video('Sjof9d8R96E', 551, 'hyperlee', 'Machine Learning. Урок №2. Кросс - валидация/Сross-validation'),
        'Мини-проект и ограничения': Video('mqp7dWk40HI', 371, 'Школа itProger / Программирование', 'Python Data Science / Урок #1 – Полная обработка данных (Scikit-learn, TensorFlow, PyTorch, Plotly)'),
    },
    'chinese-beginners': {
        'Пиньинь и тоны': Video('9k46ogTPTwU', 719, 'ChineseZen', 'КИТАЙСКИЙ ЯЗЫК | Урок 1 | Тоны, произношение и пиньинь'),
        'Приветствие': Video('QEoeANKpuq4', 441, 'ChineseZen', 'КИТАЙСКИЙ ЯЗЫК |  Урок 3 | Приветствие, прощание, благодарность'),
        'Местоимения и 是': Video('0jegi8h6294', 599, 'SmarTest', 'Китайский язык для начинающих. Урок 1. Местоимения китайского языка, глагол связка 是 shi'),
        'Вопросительная частица 吗': Video('pGQNuL4zS0c', 247, 'panda chin', 'Урок 46. Вопросительная частица 吗 ma в китайском языке'),
        'Числа от нуля до ста': Video('_o0_3927Idw', 536, 'Loong Chinese', 'Числа от 1 до 100 на китайском. Chinese numbers 1-100. 数字一到一百'),
        'Семья и 的': Video('aXPT78-7bVM', 457, 'WAWA CHINESE 哇哇汉语', 'Разговор о семье и членах семьи | 你家有几口人？| Базовый китайский язык для начинающих c нуля | 基础汉语'),
        'Даты и время': Video('1bMnybW3vQE', 642, 'SmarTest', 'Китайский язык для начинающих. Урок 4. Часы, минуты, секунды. Время в китайском языке'),
        'Счётные слова': Video('-hV81AlPVBE', 752, 'Twins Chinese', 'Счетные слова в китайском.  Топ 15. Китайский урок  | Школа китайского  | Twins Chinese'),
        'Есть и находиться': Video('6G64sIoB_4I', 688, 'Александра Саранчина | Школа китайского языка', 'Местонахождение и глагол 在 (zài) - Изучаем грамматику китайского языка легко'),
        'Короткое представление': Video('lFil1r-hNyQ', 490, 'Nuli Chinese', 'Красивый и интересный РАССКАЗ О СЕБЕ НА КИТАЙСКОМ (план из 7 пунктов с примерами)'),
    },
    'databases': {
        'Сущности и атрибуты': Video('tNQlFW3BRUc', 556, 'Listen IT', 'Что такое ERD за 9 минут'),
        'Ключи': Video('cZTxadhqahQ', 606, 'Igor Vovchenko', 'Начальный курс SQL.Первичный ключ и внешний ключ  Типы связей между таблицами'),
        'SELECT и фильтрация': Video('0Jw3pnF0huk', 420, 'Andrey Sozykin', 'Оператор SELECT | Основы SQL'),
        'Создание и изменение строк': Video('eyWGkfBYmIY', 596, 'Andrey Sozykin', 'Вставка и изменение данных в SQL | Основы SQL'),
        'JOIN': Video('H3LYwkePWfM', 948, 'Vlad Mishustin', 'Все JOIN в SQL Для Начинающих За 15 Минут'),
        'Агрегации': Video('L53jIs9KVG4', 435, 'Andrey Sozykin', 'Группировка в SQL | Основы SQL'),
        'Нормализация': Video('0kq99Y8m0gw', 891, 'Диджитализируй!', 'Нормальные формы базы данных. Три нормальных формы, нормализация и денормализация БД'),
        'Транзакции': Video('vFmajCQ7Wuc', 586, 'Listen IT', 'Что такое ACID за 9 минут'),
        'Индексы и EXPLAIN': Video('LpEwssOYRKA', 640, 'Listen IT', 'Что такое SQL ИНДЕКСЫ за 10 минут: Объяснение с примерами'),
        'Миграции и резервирование': Video('SD6_EPg0Aqk', 898, 'Артём Шумейко', 'Alembic - Как делать Миграции Базы Данных на Python #13'),
    },
    'web-lab': {
        'Как работает веб': Video('93cov6yT4OY', 966, 'Droider', 'КАК РАБОТАЕТ HTTP? – АНАТОМИЯ ИНТЕРНЕТА'),
        'HTML: структура страницы': Video('MBe1h80ghKA', 453, 'Listen IT', 'Что такое HTML за 7 минут'),
        'Формы и доступность': Video('_in4LAdxAUA', 279, 'Александр Ламков — Friendly Frontend', '11. HTML формы. Теги form, fieldset, legend, label и поле ввода input'),
        'CSS и блочная модель': Video('oQDNPNZ72Ig', 556, 'Александр Ламков — Friendly Frontend', '3. Блочная модель в CSS — свойства display, width, height, padding, margin, border и box-sizing'),
        'Flexbox и Grid': Video('YG8Vhz1pAsU', 994, 'Александр Ламков — Friendly Frontend', '12. CSS Flexbox Layout. Флексы в CSS. Гайд по флексбокс'),
        'JavaScript и события': Video('H9XRtCjD3hA', 551, 'Василий Муравьев', 'Уроки Javascript #1. Обработчик событий - AddEventListener.'),
        'Асинхронные запросы': Video('SHiUyM_fFME', 852, 'Владилен Минин', 'Урок 8. JavaScript. Как работает Async, Await. Работа с сервером c fetch'),
        'React и компоненты': Video('GeulXZP_kZ8', 911, 'Frontend Fundamentals | Александр Караджиков', 'Все что нужно знать о REACT для НОВИЧКА за 15 минут | Изучаем Реакт'),
        'Маршруты и доступ': Video('0auS9DNTmzE', 485, 'Михаил Непомнящий', 'React Router 6 - базовый роутинг React-приложения'),
        'Мини-проект: каталог': Video('IW_7b0nJoSE', 322, 'Rutina dev', 'Поисковой фильтр в реакт проекте? 🔍 | Как сделать живой поиск на Javascript'),
    },
    'team-practice': {
        'Общая цель и результат': Video('ROKGXp3zCEo', 525, 'амоБлог ', 'Как ПРАВИЛЬНО ПОСТАВИТЬ ЦЕЛИ: простой гайд'),
        'Роли и ответственность': Video('bKZvl3VOQ2c', 872, 'Скрамбери', 'Как войти в IT? Роли в команде и что они делают'),
        'Декомпозиция': Video('Ag-o4g_6HIU', 504, 'Павел Александрович', 'ДЕКОМПОЗИЦИЯ. Как решать большие задачи эффективно.'),
        'Задачи и критерии приёмки': Video('ExA_CoxcoRo', 337, 'Y_LAB University', 'User Story: принципы, критерии приемки, декомпозиция'),
        'Git и ветки': Video('XuFaQSW79rM', 847, 'Vlad Mishustin', 'Лучший Гайд по Git Для Начинающих За 15 Минут'),
        'Обзор изменений': Video('7__ZzWA-71U', 536, 'Merion Academy', 'Что такое код-ревью?'),
        'Контракты API': Video('EaFr0wYaxxM', 430, 'Свят404', 'REST API простыми словами. Что такое REST API? | 2022'),
        'Ошибки и воспроизведение': Video('8UkU-T38Z6g', 908, 'Лёша Маршал', 'Составление баг репортов'),
        'Интеграция и демонстрация': Video('pFKwmEdwZZQ', 929, 'Артём Шумейко', 'CI/CD — Простым языком на понятном примере'),
        'Ретроспектива': Video('OYUw-jZAd2E', 588, 'Dmitry Blinov', 'Как провести ретроспективу – Инструкция за 10 минут (Agile Retrospective) DBlinov.com'),
    },
}


def apply(s) -> int:
    """Attach catalog videos to seeded lessons (Y10). Returns how many lessons got a video.

    Only lessons of catalog courses whose title matches and whose video_url is empty:
    a teacher's own video is never replaced, a rerun changes nothing, demo progress stays (D3).
    """
    from sqlalchemy import select
    from app.models import Course, Lesson, Module

    added = 0
    for slug, videos in VIDEOS.items():
        course = s.scalar(select(Course).where(Course.slug == slug))
        if not course:
            continue
        for lesson in s.scalars(select(Lesson).join(Module).where(Module.course_id == course.id)):
            video = videos.get(lesson.title)
            if video and not lesson.video_url:
                lesson.video_url, lesson.video_duration = watch_url(video.youtube_id), video.seconds
                added += 1
    s.flush()
    return added
