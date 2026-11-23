# Видео YouTube к урокам: каталог

Автор: Олжас, системный аналитик. Подбор и проверка: 23 ноября 2026.
Данные для кода: [`database/seeds/lesson_videos.py`](../database/seeds/lesson_videos.py). Требования к плееру и учёту просмотра: [техническое описание](VIDEO_TECHNICAL_DESCRIPTION.md).

## Итог

| Показатель | Значение |
|---|---|
| Уроков с видео | **120 из 120** (12 курсов × 10) |
| Общая длительность | 21 ч 53 мин, в среднем 10,9 мин на урок |
| Самое короткое / длинное | 3:36 (ML, «Табличные данные») / 21:37 (ML, «Подготовка признаков») |
| На курс | от 83 мин (English) до 139 мин (Python) |
| Разных авторов | 79, ни у одного больше 6 видео |
| Речь | русская во всех 120 |
| Русские субтитры | есть у 115 |
| Доступность (oEmbed) | 120 / 120 — публичные, встраивание разрешено |

## Критерии отбора

| ID | Критерий | Как проверено |
|---|---|---|
| K1 | Тема видео совпадает с темой и примером урока из `curriculum.py` | Вручную по названию и описанию, 120 решений |
| K2 | Речь на русском; для English и Chinese — объяснение на русском | Язык из метаданных; 6 видео без метки — по описанию и тегам |
| K3 | Публичное, встраивание на сайт разрешено, без возрастного ограничения, не трансляция | `yt-dlp` (`playable_in_embed`, `age_limit`, `live_status`) и oEmbed = 200 |
| K4 | Длительность 3–25 минут | Точные секунды из метаданных; тест `test_vd02` |
| K5 | Не больше 150 минут видео на курс | Тест `test_vd03` |
| K6 | Учебный канал или преподаватель, без мата и рекламы в названии | Вручную |
| K7 | Одно видео на урок, без повторов | Тест `test_vd02` |

## Как шла работа

1. По каждому уроку составил поисковый запрос из названия и содержания, взял 10 первых результатов (1200 кандидатов).
2. Отбросил кандидатов короче 2,5 и длиннее 40 минут и трансляции, остальное просмотрел по названию, автору и числу просмотров.
3. Для 17 уроков первый поиск дал англоязычные или не по теме ролики, и я искал заново другими словами.
4. Проверил полные метаданные всех 120 выбранных видео. Три видео заменил:
   - «Даты и время» (Chinese): **автор запретил встраивание** (oEmbed 401), на нашем сайте оно не проиграется;
   - «Контроль доступа» (Cybersecurity) и «Обзор изменений» (Работа в команде): речь на английском.
5. Повторно прогнал проверку доступности: 120 из 120.

Во время проверки YouTube временно заблокировал автоматические запросы с нашего IP («подтвердите, что вы не робот»). Поэтому повторная проверка ([`testing/check_lesson_videos.py`](../testing/check_lesson_videos.py)) использует oEmbed: он не требует ключа и не блокируется, а запрет встраивания и удаление различает по коду ответа (401 и 404).

## Как заменить видео

1. Найти видео по критериям K1–K7.
2. Взять точную длительность в секундах. От неё зависит правило 90%, округлять нельзя.
3. Поменять запись в `lesson_videos.py`, прогнать `test_video_acceptance.py` и `check_lesson_videos.py`.
4. В уже заполненной БД заменить ссылку через форму урока. Прогресс этого урока сбросится у всех (правило V6).

## Каталог

### Calculus 1 (`calculus-1`), 104 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Функции и область определения | [9 класс, 15 урок, Определение числовой функции. Область определения…](https://www.youtube.com/watch?v=FENzriAjRP4) | Видеокурсы DA VINCI | 6:03 |
| 2 | Графики и преобразования | [ГРАФИК ФУНКЦИЙ — Сдвиги Графика Функции, Как строить Графики Функци…](https://www.youtube.com/watch?v=XbstdyaZop0) | INTENSIVKURS - Учебный Центр для Школьников | 8:39 |
| 3 | Предел последовательности | [Как понять предел последовательности за 10 минут?](https://www.youtube.com/watch?v=q8XtKMiBISc) | Riemann | 11:17 |
| 4 | Предел функции | [Предел функции в точке. 10 класс.](https://www.youtube.com/watch?v=5QCVBpIntcs) | MEKTEП OnLine MATEMATИKA | 8:48 |
| 5 | Непрерывность | [✓ Непрерывность функции в точке. Непрерывность многочленов · матан…](https://www.youtube.com/watch?v=nXUEw07DWkw) | Борис Трушин | 15:44 |
| 6 | Производная как скорость | [АЛГЕБРА С НУЛЯ — Что такое Производная?](https://www.youtube.com/watch?v=qrVpZGVXRuo) | INTENSIVKURS - Учебный Центр для Школьников | 11:30 |
| 7 | Правила дифференцирования | [ПРОИЗВОДНАЯ СТЕПЕННОЙ ФУНКЦИИ решение производных функций](https://www.youtube.com/watch?v=6N6c-sKRLEw) | физика ОГЭ математика ЕГЭ - Романов Владимир | 7:45 |
| 8 | Цепное правило | [Производная сложной функции. 10 класс.](https://www.youtube.com/watch?v=QLffopgx7uc) | MEKTEП OnLine MATEMATИKA | 12:21 |
| 9 | Экстремумы | [АЛГЕБРА С НУЛЯ — Точки Экстремума Функции](https://www.youtube.com/watch?v=j5r6AVv9h2Q) | INTENSIVKURS - Учебный Центр для Школьников | 12:55 |
| 10 | Определённый интеграл | [Определенный интеграл. 11 класс.](https://www.youtube.com/watch?v=5xFJBunQYSI) | MEKTEП OnLine MATEMATИKA | 8:58 |

### Linear Algebra (`linear-algebra`), 120 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Векторы | [Координаты вектора. 9 класс.](https://www.youtube.com/watch?v=LaR0W-uLi5k) | МЕКТЕП OnLine ГЕОМЕТРИЯ | 10:35 |
| 2 | Операции с векторами | [Сложение, вычитание, умножение на число векторов через координату.…](https://www.youtube.com/watch?v=6dhIlY1DH_M) | МЕКТЕП OnLine ГЕОМЕТРИЯ | 7:48 |
| 3 | Скалярное произведение | [Скалярное произведение векторов. 9 класс.](https://www.youtube.com/watch?v=KC3wfa8p_8U) | МЕКТЕП OnLine ГЕОМЕТРИЯ | 8:43 |
| 4 | Матрицы | [Линейная алгебра, 1 урок, Матрицы](https://www.youtube.com/watch?v=vAxpptpYAJo) | Видеокурсы DA VINCI | 9:16 |
| 5 | Умножение матриц | [МАТРИЦЫ математика УМНОЖЕНИЕ МАТРИЦ и простейшие операции с матрицами](https://www.youtube.com/watch?v=Ye4lx98j71w) | физика ОГЭ математика ЕГЭ - Романов Владимир | 8:31 |
| 6 | Системы линейных уравнений | [Матричный метод решения систем уравнений](https://www.youtube.com/watch?v=AWrczMDGTac) | Valery Volkov | 18:45 |
| 7 | Метод Гаусса | [Решение системы уравнений методом Гаусса](https://www.youtube.com/watch?v=hZcxW4sgW64) | Кафедра математики. On-line | 10:00 |
| 8 | Определитель и обратимость | [ОПРЕДЕЛИТЕЛЬ МАТРИЦЫ 2х2 3х3 4x4 свойства определителя](https://www.youtube.com/watch?v=UikJ3Gma6H0) | физика ОГЭ математика ЕГЭ - Романов Владимир | 13:34 |
| 9 | Линейная независимость | [Линейная зависимость и  линейная независимость  векторов.](https://www.youtube.com/watch?v=LaXL4QgQBig) | Виктор Глазнев | 16:15 |
| 10 | Собственные векторы | [Суть линейной алгебры: #14. Собственные векторы и собственные значе…](https://www.youtube.com/watch?v=khMBBxLJLcw) | Vert Dider | 17:14 |

### English (`english`), 83 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Приветствия и представление | [Английский для начинающих. Приветствие](https://www.youtube.com/watch?v=zFzek_xKaLA) | ED | 8:07 |
| 2 | Личные местоимения и be | [Урок 1. Глагол To Be в настоящем времени. A1 Elementary. #НЗА](https://www.youtube.com/watch?v=gZE0DdpwRew) | Инглиш Шоу: грамматика | 4:28 |
| 3 | Артикли и множественное число | [Артикли в английском · Грамматика английского · Онлайн-школа «Инглекс»](https://www.youtube.com/watch?v=eJnejBp9edA) | Инглекс | 7:26 |
| 4 | Present Simple | [Present Simple. ВСЕ ПРОЩЕ, чем вы думаете!](https://www.youtube.com/watch?v=6Qd1xAikoQc) | Инглиш Шоу | 5:22 |
| 5 | Вопросы и отрицания | [Вспомогательные глаголы DO или DOES - Present Simple](https://www.youtube.com/watch?v=GOqIL8gYEf0) | Английский с Еленой Дубровченко | 7:45 |
| 6 | Предлоги места и времени | [5 минут, чтобы разобраться в предлогах на английском: метод треугол…](https://www.youtube.com/watch?v=cgYMtuFa8Iw) | Skyeng – онлайн-школа иностранных языков | 8:04 |
| 7 | Present Continuous | [Present Continuous · Простое объяснение для начинающих](https://www.youtube.com/watch?v=wB9Wwizcgvc) | Английский с Ириной Кузьминой | 7:40 |
| 8 | Past Simple | [Past Simple — просто, понятно, быстро · Грамматика английского язык…](https://www.youtube.com/watch?v=H_q9D6NHEuI) | ED | 13:40 |
| 9 | Планы на будущее | [Will vs be going to · Грамматика английского · Онлайн-школа «Инглекс»](https://www.youtube.com/watch?v=MrbUPmpESVY) | Инглекс | 13:44 |
| 10 | Короткое связное письмо | [ЕГЭ Английский - Раздел 4 - личное письмо другу - универсальный шаблон](https://www.youtube.com/watch?v=xqBPNN8S2dQ) | Pro English | 6:55 |

### Python for Beginners (`python-beginners`), 139 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Первый запуск и print | [Урок 1. Функция print() - Изучение Python с нуля для начинающих](https://www.youtube.com/watch?v=ki6mKMyiCWY) | /coderoffka - Изучение Python c нуля | 12:20 |
| 2 | Переменные и типы | [Начало покорения Python / № 2 - Переменные и типы данных. Функция t…](https://www.youtube.com/watch?v=Wnm8Bk4_lBY) | Информатика без воды | 16:39 |
| 3 | Ввод и преобразование | [#6. Функции print() и input(). Преобразование строк в числа int() и…](https://www.youtube.com/watch?v=8hzpSR_Qaj8) | selfedu | 17:49 |
| 4 | Условия | [Уроки Python / Конструкция if elif else - если то иначе - Условная…](https://www.youtube.com/watch?v=bmS1QmE6wYM) | Изучаем мир ИТ / Олег Шпагин / Программирование | 8:54 |
| 5 | Циклы | [Python с нуля. Урок 4 · Циклы (for, while)](https://www.youtube.com/watch?v=sZ0EIwgLblY) | Иван Викторович | 10:31 |
| 6 | Списки и срезы | [#14. Срезы списков и сравнение списков · Python для начинающих](https://www.youtube.com/watch?v=Vx3s01Yb1P8) | selfedu | 13:37 |
| 7 | Словари и множества | [Уроки Python с нуля / #10 – Словари (dict) и работа с ними](https://www.youtube.com/watch?v=W2oO1Y-QDzo) | Школа itProger / Программирование | 16:09 |
| 8 | Функции | [35 Функции (def) в Python. Определение и вызов функции](https://www.youtube.com/watch?v=DJAlfolEv9A) | egoroff_channel | 11:31 |
| 9 | Файлы и исключения | [Python с нуля. Урок 9 · Файлы и исключения](https://www.youtube.com/watch?v=zlp6gD7UdOA) | Иван Викторович | 15:05 |
| 10 | Мини-проект: журнал оценок | [Работаем с JSON в Python. Парсинг JSON, сохраняем JSON в файл](https://www.youtube.com/watch?v=rIhygmw9HZM) | egoroff_channel | 16:27 |

### C++ for Beginners (`cpp-beginners`), 130 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Компиляция и первая программа | [#1. Первая программа на С++ · Язык С++ для начинающих](https://www.youtube.com/watch?v=c7Nb0lJHVtU) | selfedu | 9:30 |
| 2 | Типы и переменные | [Типы данных в C++. C++ для начинающих. Урок #4.](https://www.youtube.com/watch?v=pwUNLjgw7lY) | #SimpleCode | 6:44 |
| 3 | Ввод и операторы | [#2. Ввод-вывод с помощью объектов cin и cout · Язык С++ для начинающих](https://www.youtube.com/watch?v=mi1YqRF03IQ) | selfedu | 11:06 |
| 4 | Условия | [If else. Конструкция логического выбора if.  Лесенка if - else if.…](https://www.youtube.com/watch?v=k_YFH3PezqA) | #SimpleCode | 19:25 |
| 5 | Циклы | [Уроки C++ с нуля / Урок #6 - Циклы For, While, Do while](https://www.youtube.com/watch?v=Fh3huPx-kPI) | Гоша Дударь | 10:16 |
| 6 | Функции | [Функции c++ примеры. Синтаксис. Объявление, реализация функции. Пар…](https://www.youtube.com/watch?v=HFH65-sNQmI) | #SimpleCode | 19:25 |
| 7 | Строки и vector | [C++ · std::vector - векторы, как создать, вывести на печать, добавл…](https://www.youtube.com/watch?v=KPV89oSv18E) | Кирилл «Polchasa» Сапожников | 7:47 |
| 8 | Ссылки и const | [c++ ссылки что это. c++ ссылки и указатели разница. Указатель на сс…](https://www.youtube.com/watch?v=hZOX-LlUETE) | #SimpleCode | 19:52 |
| 9 | Структуры | [Структуры в C++ · struct C++. Разница между структурой и классом. И…](https://www.youtube.com/watch?v=EWJqZN7ifI0) | #SimpleCode | 10:23 |
| 10 | Файлы и мини-проект | [Чтение и запись в файл с++ используя класс fstream c++. Изучение С+…](https://www.youtube.com/watch?v=bTysglLJ8No) | #SimpleCode | 16:21 |

### Philosophy (`philosophy`), 101 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Философский вопрос | [Что такое философия](https://www.youtube.com/watch?v=KshafAmECAo) | SciOne | 12:28 |
| 2 | Аргумент и вывод | [Что такое аргумент? Логика (1)](https://www.youtube.com/watch?v=wsLZDC5WmwU) | Скептический философ | 8:21 |
| 3 | Логические ошибки | [Все логические ошибки за 9 минут](https://www.youtube.com/watch?v=craWARgRa0g) | Лобстер Sapiens | 9:00 |
| 4 | Знание и убеждение | [Проблема Гетье](https://www.youtube.com/watch?v=09gdiwUV7sU) | ПоТОК сознания | 4:56 |
| 5 | Скептицизм и сомнение | [Философия Декарт](https://www.youtube.com/watch?v=HeTn8E6G73o) | Гуманитарщина | 10:36 |
| 6 | Личность и идентичность | [Тебя уже давно НЕТ · Тождество личности](https://www.youtube.com/watch?v=aLOnKTTRrs4) | Капитан Дрейк | 13:54 |
| 7 | Свобода и ответственность | [Свобода воли и детерминизм. Просто и доступно. Лекции по философии…](https://www.youtube.com/watch?v=KZqwxtSq124) | Скептический философ | 14:10 |
| 8 | Этические подходы | [Этические теории – «этика добродетели», утилитаризм и деонтология](https://www.youtube.com/watch?v=XfQYJOuGgpo) | Иван Куницын · Про нейросети и не только | 14:10 |
| 9 | Справедливость и общество | [Джон Ролз - теория справедливости (За 10 минут)](https://www.youtube.com/watch?v=ug1PZi42MgQ) | Философия за 10 минут | 9:04 |
| 10 | Философское эссе | [Как правильно писать эссе · Полезные советы · Пример эссе · Эссе он…](https://www.youtube.com/watch?v=wA5K2_8IZfA) | Адукар | 4:45 |

### Cybersecurity (`cybersecurity`), 100 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Активы и модель угроз | [МОДЕЛЬ УГРОЗ · Простым языком на примере](https://www.youtube.com/watch?v=gsUOxAHoxbY) | Цифровая Благодетель | 4:10 |
| 2 | Пароли и MFA | [Знай! / Менеджер паролей и двухфакторная аутентификация](https://www.youtube.com/watch?v=4yCVx8aQ3nM) | РосКомСвобода | 3:46 |
| 3 | Фишинг | [Фишинг: как мошенники крадут деньги и данные](https://www.youtube.com/watch?v=6VZL0DJWr7g) | Первый отдел | 13:04 |
| 4 | Обновления и минимальные права | [Как устроена кибербезопасность: VPN, NAT, фаервол и принцип минимал…](https://www.youtube.com/watch?v=g8io45pkhXQ) | Обучение системных администраторов | 13:16 |
| 5 | Сети и TLS | [Как работает шифрование в HTTPS (SSL и TLS)](https://www.youtube.com/watch?v=nsyLWDtWXk0) | QA Studio · Тестирование | 18:37 |
| 6 | Шифрование и хеширование | [Пароли, шифрование, хеширование и СОЛЬ](https://www.youtube.com/watch?v=VbB99SOR8OE) | hasio | 6:00 |
| 7 | Контроль доступа | [Идентификация, аутентификация и авторизация простыми словами](https://www.youtube.com/watch?v=Jc1cqLk7NmQ) | MakeIT | 4:37 |
| 8 | Безопасный ввод | [SQL-инъекции для начинающих: от теории к практике](https://www.youtube.com/watch?v=pDvSNaQfuIc) | CyberYozh | 15:33 |
| 9 | Резервные копии и инциденты | [Как не потерять данные: резервное копирование и правило 3-2-1 прост…](https://www.youtube.com/watch?v=GqCoVdm6odE) | Обучение системных администраторов | 13:59 |
| 10 | Мини-аудит учебного приложения | [Весь OWASP Top 10 простыми словами](https://www.youtube.com/watch?v=4Ufdf3t3o3Y) | Reconholic | 7:20 |

### Machine Learning for Beginners (`machine-learning-beginners`), 117 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Задачи машинного обучения | [ОБУЧЕНИЕ С УЧИТЕЛЕМ, ОБУЧЕНИЕ БЕЗ УЧИТЕЛЯ, ОБУЧЕНИЕ С ПОДКРЕПЛЕНИЕМ…](https://www.youtube.com/watch?v=ku2oPMPht2I) | machine learrrning | 11:37 |
| 2 | Табличные данные | [Анализ данных с помощью Pandas. Вводное занятие](https://www.youtube.com/watch?v=wjDns1IYcPg) | egoroff_channel | 3:36 |
| 3 | Разделение данных | [Python Data Science / Урок #3 – Основы машинного обучения (Scikit-l…](https://www.youtube.com/watch?v=5UdOdUgDr-c) | Школа itProger / Программирование | 11:26 |
| 4 | Подготовка признаков | [StandardScaler· MinMaxScaler · МАСШТАБИРОВАНИЕ ДАННЫХ · МАШИННОЕ ОБ…](https://www.youtube.com/watch?v=XsuCOfpf8Ic) | machine learrrning | 21:37 |
| 5 | Линейная регрессия | [Что такое линейная регрессия? Душкин объяснит](https://www.youtube.com/watch?v=rE43fnoQNPw) | Душкин объяснит | 7:41 |
| 6 | Классификация | [Логистическая Регрессия · Logistic Regression · Линейная модель для…](https://www.youtube.com/watch?v=9BoVCdedvW8) | machine learrrning | 19:57 |
| 7 | Метрики | [#23. Показатели precision и recall. F-мера · Машинное обучение](https://www.youtube.com/watch?v=-jplpYLrcdM) | selfedu | 14:10 |
| 8 | Переобучение | [ПЕРЕОБУЧЕНИЕ И НЕДООБУЧЕНИЕ В МАШИННОМ ОБУЧЕНИИ · overfitting, unde…](https://www.youtube.com/watch?v=m7P7bnLxIc4) | machine learrrning | 12:26 |
| 9 | Кросс-валидация и baseline | [Machine Learning. Урок №2. Кросс - валидация/Сross-validation](https://www.youtube.com/watch?v=Sjof9d8R96E) | hyperlee | 9:11 |
| 10 | Мини-проект и ограничения | [Python Data Science / Урок #1 – Полная обработка данных (Scikit-lea…](https://www.youtube.com/watch?v=mqp7dWk40HI) | Школа itProger / Программирование | 6:11 |

### Chinese for Beginners (`chinese-beginners`), 92 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Пиньинь и тоны | [КИТАЙСКИЙ ЯЗЫК · Урок 1 · Тоны, произношение и пиньинь](https://www.youtube.com/watch?v=9k46ogTPTwU) | ChineseZen | 11:59 |
| 2 | Приветствие | [КИТАЙСКИЙ ЯЗЫК ·  Урок 3 · Приветствие, прощание, благодарность](https://www.youtube.com/watch?v=QEoeANKpuq4) | ChineseZen | 7:21 |
| 3 | Местоимения и 是 | [Китайский язык для начинающих. Урок 1. Местоимения китайского языка…](https://www.youtube.com/watch?v=0jegi8h6294) | SmarTest | 9:59 |
| 4 | Вопросительная частица 吗 | [Урок 46. Вопросительная частица 吗 ma в китайском языке](https://www.youtube.com/watch?v=pGQNuL4zS0c) | panda chin | 4:07 |
| 5 | Числа от нуля до ста | [Числа от 1 до 100 на китайском. Chinese numbers 1-100. 数字一到一百](https://www.youtube.com/watch?v=_o0_3927Idw) | Loong Chinese | 8:56 |
| 6 | Семья и 的 | [Разговор о семье и членах семьи · 你家有几口人？· Базовый китайский язык д…](https://www.youtube.com/watch?v=aXPT78-7bVM) | WAWA CHINESE 哇哇汉语 | 7:37 |
| 7 | Даты и время | [Китайский язык для начинающих. Урок 4. Часы, минуты, секунды. Время…](https://www.youtube.com/watch?v=1bMnybW3vQE) | SmarTest | 10:42 |
| 8 | Счётные слова | [Счетные слова в китайском.  Топ 15. Китайский урок  · Школа китайск…](https://www.youtube.com/watch?v=-hV81AlPVBE) | Twins Chinese | 12:32 |
| 9 | Есть и находиться | [Местонахождение и глагол 在 (zài) - Изучаем грамматику китайского яз…](https://www.youtube.com/watch?v=6G64sIoB_4I) | Александра Саранчина · Школа китайского языка | 11:28 |
| 10 | Короткое представление | [Красивый и интересный РАССКАЗ О СЕБЕ НА КИТАЙСКОМ (план из 7 пункто…](https://www.youtube.com/watch?v=lFil1r-hNyQ) | Nuli Chinese | 8:10 |

### Databases (`databases`), 109 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Сущности и атрибуты | [Что такое ERD за 9 минут](https://www.youtube.com/watch?v=tNQlFW3BRUc) | Listen IT | 9:16 |
| 2 | Ключи | [Начальный курс SQL.Первичный ключ и внешний ключ  Типы связей между…](https://www.youtube.com/watch?v=cZTxadhqahQ) | Igor Vovchenko | 10:06 |
| 3 | SELECT и фильтрация | [Оператор SELECT · Основы SQL](https://www.youtube.com/watch?v=0Jw3pnF0huk) | Andrey Sozykin | 7:00 |
| 4 | Создание и изменение строк | [Вставка и изменение данных в SQL · Основы SQL](https://www.youtube.com/watch?v=eyWGkfBYmIY) | Andrey Sozykin | 9:56 |
| 5 | JOIN | [Все JOIN в SQL Для Начинающих За 15 Минут](https://www.youtube.com/watch?v=H3LYwkePWfM) | Vlad Mishustin | 15:48 |
| 6 | Агрегации | [Группировка в SQL · Основы SQL](https://www.youtube.com/watch?v=L53jIs9KVG4) | Andrey Sozykin | 7:15 |
| 7 | Нормализация | [Нормальные формы базы данных. Три нормальных формы, нормализация и…](https://www.youtube.com/watch?v=0kq99Y8m0gw) | Диджитализируй! | 14:51 |
| 8 | Транзакции | [Что такое ACID за 9 минут](https://www.youtube.com/watch?v=vFmajCQ7Wuc) | Listen IT | 9:46 |
| 9 | Индексы и EXPLAIN | [Что такое SQL ИНДЕКСЫ за 10 минут: Объяснение с примерами](https://www.youtube.com/watch?v=LpEwssOYRKA) | Listen IT | 10:40 |
| 10 | Миграции и резервирование | [Alembic - Как делать Миграции Базы Данных на Python #13](https://www.youtube.com/watch?v=SD6_EPg0Aqk) | Артём Шумейко | 14:58 |

### Мастерская веба (`web-lab`), 106 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Как работает веб | [КАК РАБОТАЕТ HTTP? – АНАТОМИЯ ИНТЕРНЕТА](https://www.youtube.com/watch?v=93cov6yT4OY) | Droider | 16:06 |
| 2 | HTML: структура страницы | [Что такое HTML за 7 минут](https://www.youtube.com/watch?v=MBe1h80ghKA) | Listen IT | 7:33 |
| 3 | Формы и доступность | [11. HTML формы. Теги form, fieldset, legend, label и поле ввода input](https://www.youtube.com/watch?v=_in4LAdxAUA) | Александр Ламков — Friendly Frontend | 4:39 |
| 4 | CSS и блочная модель | [3. Блочная модель в CSS — свойства display, width, height, padding,…](https://www.youtube.com/watch?v=oQDNPNZ72Ig) | Александр Ламков — Friendly Frontend | 9:16 |
| 5 | Flexbox и Grid | [12. CSS Flexbox Layout. Флексы в CSS. Гайд по флексбокс](https://www.youtube.com/watch?v=YG8Vhz1pAsU) | Александр Ламков — Friendly Frontend | 16:34 |
| 6 | JavaScript и события | [Уроки Javascript #1. Обработчик событий - AddEventListener.](https://www.youtube.com/watch?v=H9XRtCjD3hA) | Василий Муравьев | 9:11 |
| 7 | Асинхронные запросы | [Урок 8. JavaScript. Как работает Async, Await. Работа с сервером c…](https://www.youtube.com/watch?v=SHiUyM_fFME) | Владилен Минин | 14:12 |
| 8 | React и компоненты | [Все что нужно знать о REACT для НОВИЧКА за 15 минут · Изучаем Реакт](https://www.youtube.com/watch?v=GeulXZP_kZ8) | Frontend Fundamentals · Александр Караджиков | 15:11 |
| 9 | Маршруты и доступ | [React Router 6 - базовый роутинг React-приложения](https://www.youtube.com/watch?v=0auS9DNTmzE) | Михаил Непомнящий | 8:05 |
| 10 | Мини-проект: каталог | [Поисковой фильтр в реакт проекте? 🔍 · Как сделать живой поиск на Ja…](https://www.youtube.com/watch?v=IW_7b0nJoSE) | Rutina dev | 5:22 |

### Работа в команде (`team-practice`), 107 мин

| № | Урок | Видео | Автор | Длит. |
|---|---|---|---|---|
| 1 | Общая цель и результат | [Как ПРАВИЛЬНО ПОСТАВИТЬ ЦЕЛИ: простой гайд](https://www.youtube.com/watch?v=ROKGXp3zCEo) | амоБлог  | 8:45 |
| 2 | Роли и ответственность | [Как войти в IT? Роли в команде и что они делают](https://www.youtube.com/watch?v=bKZvl3VOQ2c) | Скрамбери | 14:32 |
| 3 | Декомпозиция | [ДЕКОМПОЗИЦИЯ. Как решать большие задачи эффективно.](https://www.youtube.com/watch?v=Ag-o4g_6HIU) | Павел Александрович | 8:24 |
| 4 | Задачи и критерии приёмки | [User Story: принципы, критерии приемки, декомпозиция](https://www.youtube.com/watch?v=ExA_CoxcoRo) | Y_LAB University | 5:37 |
| 5 | Git и ветки | [Лучший Гайд по Git Для Начинающих За 15 Минут](https://www.youtube.com/watch?v=XuFaQSW79rM) | Vlad Mishustin | 14:07 |
| 6 | Обзор изменений | [Что такое код-ревью?](https://www.youtube.com/watch?v=7__ZzWA-71U) | Merion Academy | 8:56 |
| 7 | Контракты API | [REST API простыми словами. Что такое REST API? · 2022](https://www.youtube.com/watch?v=EaFr0wYaxxM) | Свят404 | 7:10 |
| 8 | Ошибки и воспроизведение | [Составление баг репортов](https://www.youtube.com/watch?v=8UkU-T38Z6g) | Лёша Маршал | 15:08 |
| 9 | Интеграция и демонстрация | [CI/CD — Простым языком на понятном примере](https://www.youtube.com/watch?v=pFKwmEdwZZQ) | Артём Шумейко | 15:29 |
| 10 | Ретроспектива | [Как провести ретроспективу – Инструкция за 10 минут (Agile Retrospe…](https://www.youtube.com/watch?v=OYUw-jZAd2E) | Dmitry Blinov | 9:48 |
