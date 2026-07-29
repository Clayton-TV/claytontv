"""Runtime harvest from the hosting platforms — YouTube contentDetails
(batched) and Vimeo oEmbed (per video). Gentle on both, never touches the
legacy server; idempotent (only fills nulls unless --refresh)."""

import logging
from io import StringIO

import pytest
import requests
from django.core.management import call_command

from catalogue.durations import format_duration, harvest_durations, parse_iso8601_duration
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("iso", "seconds"),
    [
        ("PT7M2S", 422),
        ("PT28M50S", 1730),
        ("PT1H2M3S", 3723),
        ("PT45S", 45),
        ("PT2H", 7200),
        ("P0D", 0),  # zero-length / live placeholder
        ("", None),
        (None, None),
        ("garbage", None),
    ],
)
def test_parse_iso8601_duration(iso, seconds):
    assert parse_iso8601_duration(iso) == seconds


@pytest.mark.parametrize(
    ("seconds", "label"),
    [(422, "7:02"), (1730, "28:50"), (3723, "1:02:03"), (45, "0:45"), (None, "")],
)
def test_format_duration(seconds, label):
    assert format_duration(seconds) == label


class FakeHarvestSession:
    """Routes by host: YouTube videos.list vs Vimeo oEmbed."""

    def __init__(self, yt=None, vimeo=None, time_out=(), yt_status=200):
        self.yt = yt or {}  # video_id -> ISO duration
        self.vimeo = vimeo or {}  # url -> seconds
        self.time_out = set(time_out)  # YouTube ids / Vimeo urls the platform is too slow to answer
        self.yt_status = yt_status  # e.g. 403 when the quota is spent
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        params = params or {}
        if self.time_out & set(params.get("id", "").split(",")) or params.get("url") in self.time_out:
            raise requests.ReadTimeout("read timed out")

        class Response:
            def __init__(self, code, payload):
                self.status_code = code
                self._payload = payload

            def json(self):
                return self._payload

        if "youtube" in url:
            if self.yt_status != 200:
                return Response(self.yt_status, {"error": {"message": "quota exceeded"}})
            ids = params["id"].split(",")
            items = [{"id": i, "contentDetails": {"duration": self.yt[i]}} for i in ids if i in self.yt]
            return Response(200, {"items": items})
        # vimeo oembed
        target = params.get("url")
        if target in self.vimeo:
            return Response(200, {"duration": self.vimeo[target]})
        return Response(404, {})


def test_harvests_youtube_in_batches(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    a = VideoFactory(url="https://www.youtube.com/watch?v=aaa", duration_seconds=None)
    b = VideoFactory(url="https://youtu.be/bbb", duration_seconds=None)
    session = FakeHarvestSession(yt={"aaa": "PT7M2S", "bbb": "PT28M50S"})

    stats = harvest_durations(session=session)

    a.refresh_from_db()
    b.refresh_from_db()
    assert a.duration_seconds == 422
    assert b.duration_seconds == 1730
    assert stats["youtube"] == 2


def test_harvests_vimeo_via_oembed(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://vimeo.com/99643001/d440c6994e", duration_seconds=None)
    session = FakeHarvestSession(vimeo={"https://vimeo.com/99643001/d440c6994e": 3263})

    harvest_durations(session=session)

    v.refresh_from_db()
    assert v.duration_seconds == 3263


def test_unresolvable_vimeo_is_left_null_not_zero(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://vimeo.com/177746828", duration_seconds=None)  # no hash → 404
    session = FakeHarvestSession()

    stats = harvest_durations(session=session)

    v.refresh_from_db()
    assert v.duration_seconds is None
    assert stats["unresolved"] == 1


def test_is_idempotent_skips_already_harvested(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    VideoFactory(url="https://youtu.be/ccc", duration_seconds=600)
    session = FakeHarvestSession(yt={"ccc": "PT99M"})

    harvest_durations(session=session)

    assert session.calls == []  # nothing missing → no API call


def test_slow_vimeo_reply_is_skipped_not_fatal(monkeypatch, caplog):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    slow = VideoFactory(url="https://vimeo.com/111111/aaaaaaaaaa", duration_seconds=None)
    quick = VideoFactory(url="https://vimeo.com/222222/bbbbbbbbbb", duration_seconds=None)
    session = FakeHarvestSession(vimeo={quick.url: 3263}, time_out={slow.url})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session)

    slow.refresh_from_db()
    quick.refresh_from_db()
    assert slow.duration_seconds is None  # left for the next run to backfill
    assert quick.duration_seconds == 3263  # the rest of the queue still got harvested
    assert len(session.calls) == 2
    assert stats == {"youtube": 0, "vimeo": 1, "unresolved": 0, "failed": 1}
    assert slow.url in caplog.text


def test_failed_youtube_batch_is_skipped_not_fatal(monkeypatch, caplog):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    yt = VideoFactory(url="https://youtu.be/eee", duration_seconds=None)
    also_yt = VideoFactory(url="https://youtu.be/fff", duration_seconds=None)
    vimeo = VideoFactory(url="https://vimeo.com/333333/cccccccccc", duration_seconds=None)
    session = FakeHarvestSession(vimeo={vimeo.url: 1200}, time_out={"eee"})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session)

    yt.refresh_from_db()
    also_yt.refresh_from_db()
    vimeo.refresh_from_db()
    assert yt.duration_seconds is None
    assert also_yt.duration_seconds is None
    assert vimeo.duration_seconds == 1200  # Vimeo still ran after the YouTube batch failed
    assert stats == {"youtube": 0, "vimeo": 1, "unresolved": 0, "failed": 2}  # videos, not batches
    assert "eee" in caplog.text and "fff" in caplog.text


def test_youtube_error_response_is_counted_not_silently_ignored(monkeypatch, caplog):
    """A 403 (spent quota) is valid JSON with no items — it must not read as a clean run."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://youtu.be/ggg", duration_seconds=None)
    session = FakeHarvestSession(yt={"ggg": "PT7M2S"}, yt_status=403)

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session)

    v.refresh_from_db()
    assert v.duration_seconds is None
    assert stats["failed"] == 1
    assert "403" in caplog.text


def test_missing_youtube_key_skips_youtube_without_killing_the_run(monkeypatch, caplog):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    yt = VideoFactory(url="https://youtu.be/hhh", duration_seconds=None)
    vimeo = VideoFactory(url="https://vimeo.com/555555/eeeeeeeeee", duration_seconds=None)
    session = FakeHarvestSession(vimeo={vimeo.url: 900})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session)

    yt.refresh_from_db()
    vimeo.refresh_from_db()
    assert yt.duration_seconds is None
    assert vimeo.duration_seconds == 900  # Vimeo needs no key, so it still runs
    assert stats == {"youtube": 0, "vimeo": 1, "unresolved": 0, "failed": 1}
    assert "YOUTUBE_API_KEY" in caplog.text


def test_a_run_that_reaches_nothing_at_all_is_logged_as_an_error(monkeypatch, caplog):
    """One slow video is routine; a run that resolves nothing is worth an alert."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://vimeo.com/444444/dddddddddd", duration_seconds=None)
    session = FakeHarvestSession(time_out={v.url})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session)

    assert stats["failed"] == 1
    assert [r.levelname for r in caplog.records if r.levelname == "ERROR"]


def test_refresh_reharvests_everything(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://youtu.be/ddd", duration_seconds=600)
    session = FakeHarvestSession(yt={"ddd": "PT15M"})

    harvest_durations(session=session, refresh=True)

    v.refresh_from_db()
    assert v.duration_seconds == 900


def test_command_reports_every_stat(monkeypatch):
    """Nothing to harvest, so no API calls — this pins the summary line's keys."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    out = StringIO()

    call_command("harvest_durations", stdout=out, stderr=StringIO())

    assert "YouTube: 0" in out.getvalue()
    assert "failed" in out.getvalue()
