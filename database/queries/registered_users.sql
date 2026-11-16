-- Registered accounts with their assigned role, newest first.
select u.id, u.email, u.display_name, r.name as role, u.created_at
from users u
join roles r on r.id = u.role_id
join credentials c on c.user_id = u.id
order by u.created_at desc, u.id desc;
