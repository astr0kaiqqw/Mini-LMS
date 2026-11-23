"""Check that every catalog video still exists and may be embedded on other sites.

Uses YouTube oEmbed: 200 = public and embeddable, 401 = owner disabled embedding,
404 = deleted or private. No API key, no download. Run before every demo:

    python testing/check_lesson_videos.py            # report, exit 1 if any video is broken
    python testing/check_lesson_videos.py --markdown # table for testing/VIDEO_ACCEPTANCE.md
"""
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "database/seeds"))
from lesson_videos import VIDEOS, watch_url  # noqa: E402

REASONS = {401: "встраивание запрещено автором", 403: "доступ запрещён", 404: "удалено или скрыто"}


def check(item):
    slug, lesson, video = item
    url = "https://www.youtube.com/oembed?format=json&url=" + watch_url(video.youtube_id)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return slug, lesson, video, r.status, json.load(r).get("author_name")
        except urllib.error.HTTPError as e:
            if e.code < 500:
                return slug, lesson, video, e.code, None
        except OSError:
            pass
        time.sleep(2 * (attempt + 1))
    return slug, lesson, video, None, None


def main():
    items = [(slug, lesson, v) for slug, lessons in VIDEOS.items() for lesson, v in lessons.items()]
    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(check, items))
    broken = [r for r in results if r[3] != 200]
    if "--markdown" in sys.argv:
        print("| Курс | Урок | Видео | Ответ | Причина |\n|---|---|---|---|---|")
        for slug, lesson, v, code, _ in broken:
            print(f"| {slug} | {lesson} | [{v.youtube_id}]({watch_url(v.youtube_id)}) | {code} | {REASONS.get(code, 'нет ответа')} |")
    for slug, lesson, v, code, _ in broken:
        print(f"НЕДОСТУПНО {slug} / {lesson}: {watch_url(v.youtube_id)} -> {code} {REASONS.get(code, 'нет ответа')}")
    print(f"Проверено {len(results)}, доступно {len(results) - len(broken)}, недоступно {len(broken)}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
