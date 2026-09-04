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
    """Routes by host: YouTube videos.list vs Vimeo oEmbed.

    `vimeo` maps url -> seconds; a value of None models the documented
    hashless case, which really answers 200 with `"duration": null` (probed
    against vimeo.com/177746828). An url the fake doesn't know 404s, which is
    what Vimeo returns for a deleted or mistyped id.
    """

    def __init__(
        self,
        yt=None,
        vimeo=None,
        time_out=(),
        yt_status=200,
        yt_items=None,
        yt_fail_calls=(),
        vimeo_status=None,
    ):
        self.yt = yt or {}  # video_id -> ISO duration
        self.vimeo = vimeo or {}  # url -> seconds (None = answered, no duration)
        self.time_out = set(time_out)  # YouTube ids / Vimeo urls the platform is too slow to answer
        self.yt_status = yt_status  # e.g. 403 when the quota is spent
        self.yt_items = yt_items  # raw items list, for malformed-payload cases
        self.yt_fail_calls = set(yt_fail_calls)  # 0-based YouTube call indices that time out
        self.vimeo_status = vimeo_status or {}  # url -> status code, for 429/5xx
        self.calls = []
        self.yt_calls = 0

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
            call_index = self.yt_calls
            self.yt_calls += 1
            if call_index in self.yt_fail_calls:
                raise requests.ReadTimeout("read timed out")
            if self.yt_status != 200:
                return Response(self.yt_status, {"error": {"message": "quota exceeded"}})
            ids = params["id"].split(",")
            if self.yt_items is not None:
                return Response(200, {"items": self.yt_items})
            items = [{"id": i, "contentDetails": {"duration": self.yt[i]}} for i in ids if i in self.yt]
            return Response(200, {"items": items})
        # vimeo oembed
        target = params.get("url")
        if target in self.vimeo_status:
            return Response(self.vimeo_status[target], {"error": "unavailable"})
        if target in self.vimeo:
            return Response(200, {"duration": self.vimeo[target]})
        return Response(404, {})


def test_harvests_youtube_in_batches(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    a = VideoFactory(url="https://www.youtube.com/watch?v=aaa", duration_seconds=None)
    b = VideoFactory(url="https://youtu.be/bbb", duration_seconds=None)
    session = FakeHarvestSession(yt={"aaa": "PT7M2S", "bbb": "PT28M50S"})

    stats = harvest_durations(session=session, vimeo_delay=0)

    a.refresh_from_db()
    b.refresh_from_db()
    assert a.duration_seconds == 422
    assert b.duration_seconds == 1730
    assert stats["youtube"] == 2


def test_harvests_vimeo_via_oembed(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://vimeo.com/99643001/d440c6994e", duration_seconds=None)
    session = FakeHarvestSession(vimeo={"https://vimeo.com/99643001/d440c6994e": 3263})

    harvest_durations(session=session, vimeo_delay=0)

    v.refresh_from_db()
    assert v.duration_seconds == 3263


def test_unresolvable_vimeo_is_left_null_not_zero(monkeypatch):
    """Hashless older videos answer 200 with a null duration (probed live) —
    the platform was reachable, so this is `unresolved`, never `failed`."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://vimeo.com/177746828", duration_seconds=None)  # no hash → 200, duration null
    session = FakeHarvestSession(vimeo={"https://vimeo.com/177746828": None})

    stats = harvest_durations(session=session, vimeo_delay=0)

    v.refresh_from_db()
    assert v.duration_seconds is None
    assert stats == {"youtube": 0, "vimeo": 0, "unresolved": 1, "failed": 0}


def test_is_idempotent_skips_already_harvested(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    VideoFactory(url="https://youtu.be/ccc", duration_seconds=600)
    session = FakeHarvestSession(yt={"ccc": "PT99M"})

    harvest_durations(session=session, vimeo_delay=0)

    assert session.calls == []  # nothing missing → no API call


def test_slow_vimeo_reply_is_skipped_not_fatal(monkeypatch, caplog):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    slow = VideoFactory(url="https://vimeo.com/111111/aaaaaaaaaa", duration_seconds=None)
    quick = VideoFactory(url="https://vimeo.com/222222/bbbbbbbbbb", duration_seconds=None)
    session = FakeHarvestSession(vimeo={quick.url: 3263}, time_out={slow.url})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    slow.refresh_from_db()
    quick.refresh_from_db()
    assert slow.duration_seconds is None  # left for the next run to backfill
    assert quick.duration_seconds == 3263  # the rest of the queue still got harvested
    assert len(session.calls) == 2
    assert stats == {"youtube": 0, "vimeo": 1, "unresolved": 0, "failed": 1}
    assert f"video {slow.id}" in caplog.text
    assert slow.url not in caplog.text


def test_failed_youtube_batch_is_skipped_not_fatal(monkeypatch, caplog):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    yt = VideoFactory(url="https://youtu.be/eee", duration_seconds=None)
    also_yt = VideoFactory(url="https://youtu.be/fff", duration_seconds=None)
    vimeo = VideoFactory(url="https://vimeo.com/333333/cccccccccc", duration_seconds=None)
    session = FakeHarvestSession(vimeo={vimeo.url: 1200}, time_out={"eee"})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

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
        stats = harvest_durations(session=session, vimeo_delay=0)

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
        stats = harvest_durations(session=session, vimeo_delay=0)

    yt.refresh_from_db()
    vimeo.refresh_from_db()
    assert yt.duration_seconds is None
    assert vimeo.duration_seconds == 900  # Vimeo needs no key, so it still runs
    assert stats == {"youtube": 0, "vimeo": 1, "unresolved": 0, "failed": 1}
    assert "YOUTUBE_API_KEY" in caplog.text


def test_a_run_that_reaches_nothing_at_all_is_logged_as_an_error(monkeypatch, caplog):
    """A whole platform unreachable is worth an alert. (A single slow video is
    not — see test_a_quiet_night_with_a_single_blip_stays_a_warning.)"""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    dead = [VideoFactory(url=f"https://vimeo.com/44{n:04d}/dead{n}", duration_seconds=None) for n in range(20)]
    session = FakeHarvestSession(time_out={v.url for v in dead})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    assert stats["failed"] == 20
    assert [r.levelname for r in caplog.records if r.levelname == "ERROR"]


def test_total_outage_alerts_even_though_vimeo_leaves_something_unresolved(monkeypatch, caplog):
    """The hashless Vimeo back-catalogue lands in `unresolved` on every run, so
    an alert that waits for `unresolved == 0` can never fire in production."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    for n in range(60):
        VideoFactory(url=f"https://youtu.be/out{n}", duration_seconds=None)
    hashless = VideoFactory(url="https://vimeo.com/177746828", duration_seconds=None)
    session = FakeHarvestSession(vimeo={hashless.url: None}, yt_fail_calls={0, 1})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    assert stats == {"youtube": 0, "vimeo": 0, "unresolved": 1, "failed": 60}
    assert [r for r in caplog.records if r.levelname == "ERROR"]


def test_a_quota_that_dies_partway_through_alerts(monkeypatch, caplog):
    """Quota exhaustion is partial by nature and runs in this direction: the
    batches before the quota ran out succeed, everything after it fails. An
    alert that waits for a *majority* of failures would sleep through it."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    for n in range(100):
        VideoFactory(url=f"https://youtu.be/half{n}", duration_seconds=None)
    session = FakeHarvestSession(yt={f"half{n}": "PT5M" for n in range(100)}, yt_fail_calls={1})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    assert stats["youtube"] == 50  # the batch before the quota died
    assert stats["failed"] == 50  # the batch after it
    assert [r for r in caplog.records if r.levelname == "ERROR"]


def test_a_dead_platform_alerts_even_when_the_other_is_healthy(monkeypatch, caplog):
    """Vimeo flat on its back while the much larger YouTube half sails through.
    Pooling both platforms into one ratio let the healthy majority mask it."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    for n in range(60):
        VideoFactory(url=f"https://youtu.be/fine{n}", duration_seconds=None)
    down = [VideoFactory(url=f"https://vimeo.com/9{n:05d}/hash{n}", duration_seconds=None) for n in range(40)]
    session = FakeHarvestSession(
        yt={f"fine{n}": "PT5M" for n in range(60)},
        vimeo_status={v.url: 503 for v in down},
    )

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    assert stats == {"youtube": 60, "vimeo": 0, "unresolved": 0, "failed": 40}
    assert [r for r in caplog.records if r.levelname == "ERROR"]


def test_a_catalogue_of_gone_vimeo_videos_never_alerts(monkeypatch, caplog):
    """~20% of the hashless back-catalogue is deleted and 404s permanently
    (probed: 8 of 40 sampled). Counting those as `failed` would fire this
    ERROR every single night, on every healthy run, until someone muted it."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    for n in range(40):
        VideoFactory(url=f"https://vimeo.com/12{n:05d}", duration_seconds=None)
    session = FakeHarvestSession()  # every url unknown to the fake → 404, as Vimeo really does

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    assert stats == {"youtube": 0, "vimeo": 0, "unresolved": 40, "failed": 0}
    assert not [r for r in caplog.records if r.levelname == "ERROR"]


def test_a_quiet_night_with_a_single_blip_stays_a_warning(monkeypatch, caplog):
    """The steady state months from now: the queue is only the permanently
    unresolvable videos, so `resolved` is legitimately 0. One transient
    timeout must not page anyone, or the alert gets muted and we're blind."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    for n in range(30):
        VideoFactory(url=f"https://vimeo.com/13{n:05d}", duration_seconds=None)
    blip = VideoFactory(url="https://vimeo.com/1400000/blip", duration_seconds=None)
    session = FakeHarvestSession(time_out={blip.url})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    assert stats["failed"] == 1
    assert stats["unresolved"] == 30
    assert not [r for r in caplog.records if r.levelname == "ERROR"]


def test_a_routine_single_failure_stays_a_warning(monkeypatch, caplog):
    """The other edge of the threshold: one slow video among successes must not
    page anyone, or the ERROR becomes noise and gets ignored."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    slow = VideoFactory(url="https://vimeo.com/111111/aaaaaaaaaa", duration_seconds=None)
    for n in range(5):
        VideoFactory(url=f"https://youtu.be/ok{n}", duration_seconds=None)
    session = FakeHarvestSession(yt={f"ok{n}": "PT5M" for n in range(5)}, time_out={slow.url})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    assert stats["failed"] == 1
    assert stats["youtube"] == 5
    assert not [r for r in caplog.records if r.levelname == "ERROR"]


def test_a_gone_vimeo_video_is_unresolved_not_a_platform_failure(monkeypatch):
    """404 means the video is deleted or private — permanent, and nothing to
    do with Vimeo's health. Only a transient status counts as `failed`."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://vimeo.com/121650999", duration_seconds=None)
    session = FakeHarvestSession(vimeo_status={v.url: 404})

    stats = harvest_durations(session=session, vimeo_delay=0)

    v.refresh_from_db()
    assert v.duration_seconds is None
    assert stats == {"youtube": 0, "vimeo": 0, "unresolved": 1, "failed": 0}


def test_a_boolean_vimeo_duration_is_rejected_not_stored_as_one_second(monkeypatch):
    """int(True) is 1 — that would quietly write a 1-second runtime and render
    it on the site as '0:01'."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://vimeo.com/151515/iiiiiiiiii", duration_seconds=None)
    session = FakeHarvestSession(vimeo={v.url: True})

    stats = harvest_durations(session=session, vimeo_delay=0)

    v.refresh_from_db()
    assert v.duration_seconds is None
    assert stats["failed"] == 1


@pytest.mark.parametrize("bad", [-5, 3599999999996400])
def test_an_out_of_range_vimeo_duration_does_not_kill_the_run(monkeypatch, bad):
    """duration_seconds is a PositiveIntegerField: a negative trips its CHECK
    constraint and an absurd one overflows Postgres' integer, both of which
    aborted the run mid-queue (SQLite hides the overflow locally)."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    rotten = VideoFactory(url="https://vimeo.com/161616/jjjjjjjjjj", duration_seconds=None)
    good = VideoFactory(url="https://vimeo.com/171717/kkkkkkkkkk", duration_seconds=None)
    session = FakeHarvestSession(vimeo={rotten.url: bad, good.url: 1200})

    stats = harvest_durations(session=session, vimeo_delay=0)

    rotten.refresh_from_db()
    good.refresh_from_db()
    assert rotten.duration_seconds is None
    assert good.duration_seconds == 1200  # the queue carried on
    assert stats == {"youtube": 0, "vimeo": 1, "unresolved": 0, "failed": 1}


def test_an_absurd_youtube_duration_is_not_stored(monkeypatch):
    """Same overflow, reached through the ISO-8601 parser instead."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://youtu.be/huge", duration_seconds=None)
    session = FakeHarvestSession(yt={"huge": "PT999999999999H"})

    stats = harvest_durations(session=session, vimeo_delay=0)

    v.refresh_from_db()
    assert v.duration_seconds is None
    assert stats["unresolved"] == 1


def test_vimeo_server_error_is_counted_failed_not_unresolved(monkeypatch, caplog):
    """A 429/503 means we couldn't reach Vimeo — recording it as `unresolved`
    made it indistinguishable from a video that genuinely has no duration."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://vimeo.com/666666/ffffffffff", duration_seconds=None)
    session = FakeHarvestSession(vimeo_status={v.url: 503})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    v.refresh_from_db()
    assert v.duration_seconds is None
    assert stats == {"youtube": 0, "vimeo": 0, "unresolved": 0, "failed": 1}
    assert "503" in caplog.text


def test_non_numeric_vimeo_duration_does_not_kill_the_run(monkeypatch, caplog):
    """int('about an hour') would abort the whole harvest mid-queue."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    bad = VideoFactory(url="https://vimeo.com/777777/gggggggggg", duration_seconds=None)
    good = VideoFactory(url="https://vimeo.com/888888/hhhhhhhhhh", duration_seconds=None)
    session = FakeHarvestSession(vimeo={bad.url: "about an hour", good.url: 1200})

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    bad.refresh_from_db()
    good.refresh_from_db()
    assert bad.duration_seconds is None
    assert good.duration_seconds == 1200  # the queue carried on past the bad payload
    assert stats == {"youtube": 0, "vimeo": 1, "unresolved": 0, "failed": 1}


def test_youtube_item_without_an_id_does_not_kill_the_run(monkeypatch, caplog):
    """item['id'] on a malformed 200 body would abort the whole harvest."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://youtu.be/jjj", duration_seconds=None)
    session = FakeHarvestSession(yt_items=[{"contentDetails": {"duration": "PT7M2S"}}])

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    v.refresh_from_db()
    assert v.duration_seconds is None
    # Counted once, not once as `failed` and again in the missing-id sweep.
    assert sum(stats.values()) == 1


def test_youtube_ids_absent_from_the_reply_are_counted_unresolved(monkeypatch, caplog):
    """videos.list silently drops deleted/private/region-blocked ids from a 200.
    Those must land in a bucket, or the stats quietly stop summing."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    kept = VideoFactory(url="https://youtu.be/kept", duration_seconds=None)
    dropped = VideoFactory(url="https://youtu.be/gone", duration_seconds=None)
    session = FakeHarvestSession(yt={"kept": "PT7M2S"})  # 'gone' is simply not returned

    with caplog.at_level(logging.WARNING):
        stats = harvest_durations(session=session, vimeo_delay=0)

    kept.refresh_from_db()
    dropped.refresh_from_db()
    assert kept.duration_seconds == 422
    assert dropped.duration_seconds is None
    assert stats == {"youtube": 1, "vimeo": 0, "unresolved": 1, "failed": 0}
    assert sum(stats.values()) == 2  # every target accounted for
    assert "gone" in caplog.text


def test_youtube_item_with_an_unparseable_duration_is_counted_unresolved(monkeypatch):
    """Returned but undurationed still has to land in a bucket."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    VideoFactory(url="https://youtu.be/odd", duration_seconds=None)
    session = FakeHarvestSession(yt={"odd": "not-an-iso-duration"})

    stats = harvest_durations(session=session, vimeo_delay=0)

    assert stats == {"youtube": 0, "vimeo": 0, "unresolved": 1, "failed": 0}


def test_refresh_reharvests_everything(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    v = VideoFactory(url="https://youtu.be/ddd", duration_seconds=600)
    session = FakeHarvestSession(yt={"ddd": "PT15M"})

    harvest_durations(session=session, refresh=True, vimeo_delay=0)

    v.refresh_from_db()
    assert v.duration_seconds == 900


def test_command_reports_every_stat(monkeypatch):
    """Pins the summary line's keys. The session is mocked, so this can never
    reach the real APIs however much the test DB happens to hold."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    VideoFactory(url="https://youtu.be/iii", duration_seconds=None)
    session = FakeHarvestSession(yt={"iii": "PT10M"})
    monkeypatch.setattr("catalogue.durations.requests.Session", lambda: session)
    out = StringIO()

    call_command("harvest_durations", stdout=out, stderr=StringIO())

    assert "YouTube: 1" in out.getvalue()
    assert "unresolved: 0" in out.getvalue()
    assert "failed" in out.getvalue()


def test_transport_failures_do_not_log_api_keys_or_private_video_urls(monkeypatch, caplog):
    api_key = "test-api-key-do-not-log"
    private_hash = "test-private-hash-do-not-log"
    monkeypatch.setenv("YOUTUBE_API_KEY", api_key)
    VideoFactory(url="https://youtu.be/aaa", duration_seconds=None)
    VideoFactory(url=f"https://vimeo.com/123/{private_hash}", duration_seconds=None)

    class FailedSession:
        def get(self, url, params=None, timeout=None):
            request = requests.Request("GET", url, params=params).prepare()
            raise requests.ConnectionError(f"Request failed: {request.url}")

    with caplog.at_level(logging.WARNING, logger="catalogue.durations"):
        stats = harvest_durations(session=FailedSession(), vimeo_delay=0)

    assert stats["failed"] == 2
    assert api_key not in caplog.text
    assert private_hash not in caplog.text


def test_nonfinite_vimeo_duration_does_not_abort_remaining_videos():
    bad = VideoFactory(url="https://vimeo.com/123", duration_seconds=None)
    good = VideoFactory(url="https://vimeo.com/456", duration_seconds=None)
    session = FakeHarvestSession(vimeo={bad.url: float("inf"), good.url: 90})

    stats = harvest_durations(session=session, vimeo_delay=0)

    bad.refresh_from_db()
    good.refresh_from_db()
    assert bad.duration_seconds is None
    assert good.duration_seconds == 90
    assert stats["failed"] == 1
    assert stats["vimeo"] == 1
