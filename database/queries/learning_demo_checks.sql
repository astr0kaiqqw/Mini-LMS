-- Each target course must have 10 lessons and 3 distinct demo students.
SELECT c.slug, count(DISTINCT l.id) AS lessons,
       count(DISTINCT e.user_id) FILTER (WHERE u.email LIKE '%.student%@demo.example.test') AS demo_students
FROM courses c
LEFT JOIN modules m ON m.course_id=c.id
LEFT JOIN lessons l ON l.module_id=m.id
LEFT JOIN enrollments e ON e.course_id=c.id
LEFT JOIN users u ON u.id=e.user_id
WHERE c.slug IN ('calculus-1','linear-algebra','english','python-beginners','cpp-beginners',
'philosophy','cybersecurity','machine-learning-beginners','chinese-beginners','databases','web-lab','team-practice')
GROUP BY c.id ORDER BY c.slug;
