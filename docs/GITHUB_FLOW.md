# GitHub: инструкция для команды

## Один раз
```bash
git clone https://github.com/astr0kaiqqw/Mini-LMS.git
cd Mini-LMS
git fetch origin
git switch develop
```
Если develop ещё нет, координатор создаёт её из main и отправляет: `git switch -c develop main`, затем `git push -u origin develop`. Ветки на GitHub — не папки.

## Одна задача — одна ветка
```bash
git switch develop
git pull --ff-only origin develop
git switch -c feature/anuar-login
```
Для Руслана: `feature/db-course-schema`. Для остальных: `feature/yerassyl-quiz-api`, `feature/olzhas-quiz-requirements`. Имена — латиницей.

Измените файлы, проверьте результат, посмотрите diff:
```bash
git status
git diff
git add frontend/src/main.tsx
git diff --cached
git commit -m "feat(auth): add login form"
git push -u origin feature/anuar-login
```
Добавляйте конкретные файлы; перед коммитом проверяйте, что нет .env, дампов и чужих изменений. Для БД пример: `feat(db): add courses table`. Формат: type(scope): short English description. Типы: feat, fix, docs, test, chore, perf.

## Pull Request
В GitHub откройте Compare & pull request, base — develop, compare — своя ветка. Заполните шаблон: проблема, результат, проверки, ограничения, недельная задача. Добавьте reviewer. Для схемы автор — Руслан, reviewer — разработчик, который использует эти данные. Автор не утверждает собственный PR.

Исправления по review отправляйте обычным commit/push в ту же ветку. После проверок и одобрения используйте Squash and merge. Main обновляется из develop через отдельный release PR после недельной проверки. Защиту веток нужно включить в настройках GitHub: запрет прямых изменений main, обязательное review и проверки. Этот файл сам защиту не включает.

## Конфликты
Сначала сохранить свои изменения в коммит, затем fetch и merge origin/develop в свою ветку. Разобрать конфликтующие строки с их автором, повторить проверки и сделать commit. Не использовать force push и не удалять изменения вслепую.

## Личный отчёт
Ссылка на PR + что сделал лично + как проверил + что осталось. Сгенерированный помощником код сначала изучить, проверить и осмысленно доработать; не выдавать его автоматически за свою выполненную работу.
