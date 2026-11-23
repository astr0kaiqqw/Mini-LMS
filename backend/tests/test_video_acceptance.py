"""Acceptance scenarios for YouTube lesson videos (testing/VIDEO_ACCEPTANCE.md).

VD-01..03 check the analyst's catalog and need no database.
VD-10.. run against PostgreSQL like the other acceptance files.
xfail(strict=True) marks an agreed requirement that is not implemented yet: the test
starts failing with XPASS once the task is done, and its owner removes the marker.
"""
import math
import os
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from test_learning import env, course  # noqa: F401  (fixture)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "database/seeds"))
from curriculum import COURSES, lessons_for  # noqa: E402
from lesson_videos import VIDEOS, watch_url  # noqa: E402

needs_db = pytest.mark.skipif(os.getenv("RUN_DB_TESTS") != "1", reason="Requires isolated PostgreSQL")

TEACHER = "instructor@demo.example.test"
STUDENT = "calculus-1.student1@demo.example.test"
YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
CANONICAL = re.compile(r"^https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$")
ALL = [(slug, title, v) for slug, lessons in VIDEOS.items() for title, v in lessons.items()]


# ---------- Catalog (database/seeds/lesson_videos.py)

def test_vd01_every_seed_lesson_has_exactly_one_video():
    assert list(VIDEOS) == list(COURSES)
    for slug in COURSES:
        assert list(VIDEOS[slug]) == [l["title"] for l in lessons_for(slug)], slug


def test_vd02_video_records_are_complete_and_unique():
    ids = [v.youtube_id for _, _, v in ALL]
    assert len(ids) == len(set(ids)) == 120
    for slug, title, v in ALL:
        assert YOUTUBE_ID.match(v.youtube_id), (slug, title)
        assert 180 <= v.seconds <= 1500, (slug, title, v.seconds)  # K4: 3-25 minutes
        assert v.channel.strip() and v.title.strip(), (slug, title)
        assert CANONICAL.match(watch_url(v.youtube_id))


def test_vd03_video_load_per_course_stays_under_150_minutes():
    for slug, lessons in VIDEOS.items():
        assert sum(v.seconds for v in lessons.values()) <= 150 * 60, slug  # K5


# ---------- Works today: the watch rule does not depend on the video source

def lesson_of(s, slug="calculus-1", position=1):
    from app.models import Lesson, Module
    return s.scalar(
        select(Lesson).join(Module)
        .where(Module.course_id == course(s, slug).id)
        .order_by(Module.position, Lesson.position)
        .offset(position - 1)
    )


def lesson_body(l, **changes):
    body = dict(title=l.title, position=l.position, summary=l.summary, content=l.content,
                practice=l.practice, duration_minutes=l.duration_minutes,
                video_url=l.video_url, video_duration=l.video_duration)
    return {**body, **changes}


@needs_db
def test_vd10_youtube_lesson_completes_by_the_same_90_percent_rule(env):
    s, login = env
    student = login(STUDENT)
    l = lesson_of(s)
    v = VIDEOS["calculus-1"][l.title]
    l.video_url, l.video_duration = watch_url(v.youtube_id), v.seconds
    s.flush()
    assert student.post(f"/api/lessons/{l.id}/complete").status_code == 422
    watched = math.ceil(v.seconds * 0.9)
    for start in range(0, watched, 10):
        r = student.post(f"/api/lessons/{l.id}/watch", json={"start": start, "end": min(start + 10, watched)})
        assert r.status_code == 200, r.text
    assert r.json()["completed"] is True
    seek = student.post(f"/api/lessons/{l.id}/watch", json={"start": 0, "end": v.seconds})
    assert seek.status_code == 422  # a jump over the whole video is not a watched span


# ---------- Confirmed gaps (VIDEO_TECHNICAL_DESCRIPTION, section 9)

@needs_db
@pytest.mark.xfail(strict=True, reason="VID-GAP-3: YouTube links are stored as typed, API has no video source")
def test_vd20_youtube_link_is_normalized_and_typed(env):
    s, login = env
    teacher, student = login(TEACHER), login(STUDENT)
    l = lesson_of(s)
    vid = VIDEOS["calculus-1"][l.title]
    r = teacher.put(f"/api/staff/lessons/{l.id}", json=lesson_body(
        l, video_url=f"https://youtu.be/{vid.youtube_id}?t=30&si=share", video_duration=vid.seconds))
    assert r.status_code == 200, r.text
    got = student.get(f"/api/lessons/{l.id}").json()
    assert got["video_url"] == watch_url(vid.youtube_id)
    assert (got["video_provider"], got["youtube_id"]) == ("youtube", vid.youtube_id)
    text = student.get(f"/api/lessons/{lesson_of(s, position=2).id}").json()
    assert (text["video_provider"], text["youtube_id"]) == (None, None)
