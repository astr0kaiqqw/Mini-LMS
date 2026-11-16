-- Preview the deletion plan without running the deletion.
explain (costs on)
delete from login_sessions where expires_at <= now();

-- Remove only expired sessions.
delete from login_sessions where expires_at <= now();
