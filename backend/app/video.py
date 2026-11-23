"""Lesson video sources: direct HTML5 files and YouTube (docs/VIDEO_TECHNICAL_DESCRIPTION.md, Y1-Y5)."""
import re
from urllib.parse import parse_qs, urlsplit

YOUTUBE_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com",
    "youtu.be", "youtube-nocookie.com", "www.youtube-nocookie.com",
}
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}")
NOT_ONE_VIDEO = "Нужна ссылка на одно видео YouTube"


def youtube_id(url: str) -> str | None:
    """ID of a YouTube video link, None for other hosts, ValueError for YouTube links without one video."""
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    if host not in YOUTUBE_HOSTS:
        return None
    path = parts.path.rstrip("/")
    if host == "youtu.be":
        candidate = path.removeprefix("/")
    elif path == "/watch":
        candidate = (parse_qs(parts.query).get("v") or [""])[0]
    elif path.startswith("/embed/"):
        candidate = path.removeprefix("/embed/")
    else:  # playlists, channels, Shorts
        candidate = ""
    if not VIDEO_ID.fullmatch(candidate):
        raise ValueError(NOT_ONE_VIDEO)
    return candidate


def watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def normalize(url: str) -> str:
    """YouTube links become https://www.youtube.com/watch?v=ID; other links stay as typed."""
    vid = youtube_id(url)
    return watch_url(vid) if vid else url


def describe(url: str | None) -> tuple[str | None, str | None]:
    """(video_provider, youtube_id) for an already stored link."""
    if not url:
        return None, None
    try:
        vid = youtube_id(url)
    except ValueError:  # legacy row saved before validation
        return "youtube", None
    return ("youtube", vid) if vid else ("html5", None)
