-- Staff-only answer-key report. Do not expose this query through a student API.
SELECT c.title AS course, l.title AS topic, q.prompt AS question,
       q.options, q.correct_index + 1 AS correct_option,
       q.options ->> q.correct_index AS correct_answer
FROM quiz_questions q
JOIN lessons l ON l.id = q.lesson_id
JOIN modules m ON m.id = l.module_id
JOIN courses c ON c.id = m.course_id
ORDER BY c.id, m.position, l.position;
