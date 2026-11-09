-- Read-only: course structure, author and publication status.
SELECT c.slug, c.title AS course, c.status, u.display_name AS teacher,
       m.position AS module_position, m.title AS module,
       l.position AS lesson_position, l.title AS lesson
FROM courses c
JOIN users u ON u.id = c.teacher_id
JOIN modules m ON m.course_id = c.id
JOIN lessons l ON l.module_id = m.id
ORDER BY c.slug, m.position, l.position;
