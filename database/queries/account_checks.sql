-- Выполнять только в локальной или тестовой БД. Только чтение.
SELECT r.name, count(u.id) AS user_count
FROM roles r LEFT JOIN users u ON u.role_id = r.id
GROUP BY r.name ORDER BY r.name;

-- Существующий UNIQUE(email) уже создаёт индекс; дублирующий индекс не нужен.
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, display_name, role_id FROM users WHERE email = 'student@example.test';
-- TODO(W11, Руслан): DB-01 — записать исходный план и результаты проверок в docs/DB_TEST_REPORT.md.
