"""Store YouTube lesson links in one canonical form (VIDEO_TECHNICAL_DESCRIPTION, Y4)."""

import re
from urllib.parse import parse_qs, urlsplit

from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

CHECK = (
    "video_url IS NULL OR video_url NOT LIKE '%youtu%' "
    "OR video_url ~ '^https://www[.]youtube[.]com/watch[?]v=[A-Za-z0-9_-]{11}$'"
)
HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "youtube-nocookie.com", "www.youtube-nocookie.com"}


def canonical(url):
    """Frozen copy of app.video.normalize: migrations must not import app code."""
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    if host not in HOSTS:
        return url
    path = parts.path.rstrip("/")
    if host == "youtu.be":
        vid = path.removeprefix("/")
    elif path == "/watch":
        vid = (parse_qs(parts.query).get("v") or [""])[0]
    elif path.startswith("/embed/"):
        vid = path.removeprefix("/embed/")
    else:
        vid = ""
    return f"https://www.youtube.com/watch?v={vid}" if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid) else None


def upgrade():
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, video_url FROM lessons WHERE video_url LIKE '%youtu%'")).all()
    for lesson_id, url in rows:
        fixed = canonical(url)
        if fixed is None:  # not one video: turn the lesson back into a text lesson, progress goes with it
            conn.execute(sa.text("DELETE FROM lesson_progress WHERE lesson_id = :id"), {"id": lesson_id})
            conn.execute(sa.text("UPDATE lessons SET video_url = NULL, video_duration = NULL WHERE id = :id"), {"id": lesson_id})
        elif fixed != url:
            conn.execute(sa.text("UPDATE lessons SET video_url = :u WHERE id = :id"), {"u": fixed, "id": lesson_id})
    op.execute(f"ALTER TABLE lessons ADD CONSTRAINT ck_lessons_youtube_url CHECK ({CHECK}) NOT VALID")
    op.execute("ALTER TABLE lessons VALIDATE CONSTRAINT ck_lessons_youtube_url")


def downgrade():
    op.drop_constraint("ck_lessons_youtube_url", "lessons")
