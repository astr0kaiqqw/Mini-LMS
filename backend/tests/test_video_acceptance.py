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
