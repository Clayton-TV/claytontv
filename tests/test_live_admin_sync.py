"""The live-admin adapter, tested against synthetic HTML replicating the
observed form structure (input/textarea/select names verified in the
authenticated recon of 2026-06-12; see data/legacy_rescue/lookups/README.md)."""

import logging

import pytest
import requests

from catalogue.ingest.legacy import ingest_programmes
from catalogue.ingest.live_admin import list_programme_ids, parse_meta_page, to_dump_record
from catalogue.models import Video

pytestmark = pytest.mark.django_db

LIST_HTML = """
<table>
<tr><td><a href="mediaProgrammeMeta.asp?ID=12404">Luke 14 - Excuses</a></td></tr>
<tr><td><a href="mediaProgrammeTimeline.asp?ID=12404">timeline</a></td></tr>
<tr><td><a href="mediaProgrammeMeta.asp?ID=12403">Kids Talk</a></td></tr>
</table>
"""

META_HTML = """
<form action="mediaProgrammeMeta.asp?ID=12404">
<input name="programmeRef" value="YT6325KidsTalkAM17.05.26">
<input name="URL" value="Luke 14:1,15-24 - Excuses - Jesmond Parish - Sermon">
<input name="programmeName" value="Luke 14:1,15-24  - Excuses - Jesmond Parish - Sermon">
<input name="programmeDate" value="17/05/2026">
<textarea name="programmeDescription">&lt;p&gt;Dan McBride preaches.&lt;/p&gt;</textarea>
<input name="vimeoLink" value="https://www.youtube.com/watch?v=oCivERk8ZWQ">
<input name="ThumbnailURL" value="https://i.ytimg.com/vi/oCivERk8ZWQ/mqdefault.jpg">
<input name="ProgrammeTranscript" value="">
<input name="ProgrammeAudio" value="">
<select name="ProgrammeRelatedSpeakers" multiple>
  <option value="360|0" selected>McBride, Dan </option>
  <option value="11|0">Redfearn, Jonathan</option>
</select>
<select name="ProgrammeRelatedTopics" multiple>
  <option value="146|0" selected>&#8722;&#8722;&#8722; Preaching &amp; Teaching</option>
</select>
<select name="ProgrammeRelatedBooks" multiple>
  <option value="42|0" selected>Luke</option>
</select>
</form>
"""


class FakeSession:
    def __init__(self, pages):
        self.pages = pages

    def get(self, url, **kwargs):
        class R:
            status_code = 200
            url_ = None

            def __init__(self, text, url):
                self.text = text
                self.url = url

            def raise_for_status(self):
                pass

        for fragment, body in self.pages.items():
            if fragment in url:
                return R(body, url)
        return R("", url)


def test_list_page_yields_unique_ids_in_order():
    session = FakeSession({"mediaProgramme.asp": LIST_HTML})
    assert list_programme_ids(session, pages=1) == ["12404", "12403"]


def list_html(*ids):
    rows = "".join(f'<tr><td><a href="mediaProgrammeMeta.asp?ID={i}">x</a></td></tr>' for i in ids)
    return f"<table>{rows}</table>"


class PagedSession(FakeSession):
    """Serves a different list page per offset, so depth behaviour is testable."""

    def __init__(self, list_pages, metas=None):
        super().__init__(metas or {})
        self.list_pages = list_pages
        self.offsets_requested = []

    def get(self, url, **kwargs):
        if "mediaProgramme.asp" in url:
            import re

            offset = int(re.search(r"offset=(\d+)", url).group(1))
            self.offsets_requested.append(offset)
            page = offset // 50
            body = self.list_pages[page] if page < len(self.list_pages) else ""

            class R:
                status_code = 200

                def __init__(self):
                    self.text = body
                    self.url = url

                def raise_for_status(self):
                    pass

            return R()
        return super().get(url, **kwargs)


def test_auto_depth_crawls_until_a_page_holds_no_new_programmes():
    """pages=None: keep paging the newest-modified list until a whole page is
    already-known ids — the catch-up backfill sizes itself, no --pages guess."""
    from tests.factories import VideoFactory

    for known in ("100", "101"):
        VideoFactory(id=known)
    session = PagedSession(
        [list_html("300", "301"), list_html("302", "100"), list_html("100", "101"), list_html("999")]
    )

    ids = list_programme_ids(session, pages=None)

    assert ids == ["300", "301", "302", "100", "101"]
    # Stopped after the all-known page; never fetched page 3
    assert session.offsets_requested == [0, 50, 100]


def test_auto_depth_is_capped():
    from catalogue.ingest import live_admin

    endless = PagedSession([list_html(str(1000 + n)) for n in range(500)])

    list_programme_ids(endless, pages=None)

    assert len(endless.offsets_requested) == live_admin.MAX_AUTO_PAGES


def test_an_empty_first_page_fails_loudly():
    """Zero programme links on page 0 means the admin's HTML changed or an
    ASP error page came back — a silent 0-synced success would hide it."""
    session = PagedSession([""])

    with pytest.raises(RuntimeError, match="no programme links"):
        list_programme_ids(session, pages=1)


def test_sync_ingests_page_by_page_so_a_crash_loses_nothing():
    """A mid-backfill crash (network, session lapse) must keep everything
    already fetched — ingest happens per page, not once at the end."""
    from catalogue.ingest import live_admin

    class CrashySession(PagedSession):
        def get(self, url, **kwargs):
            if "mediaProgrammeMeta.asp" in url and "ID=12403" in url:
                raise OSError("network died")
            return super().get(url, **kwargs)

    session = CrashySession(
        [list_html("12404"), list_html("12403"), list_html("12404")],
        metas={"mediaProgrammeMeta.asp": META_HTML},
    )

    with pytest.raises(OSError):
        live_admin.sync(pages=None, delay_seconds=0, session=session)

    # Page 0's programme was ingested before page 1 crashed
    assert Video.objects.filter(id="12404").exists()


# Current admin layout: the meta form has NO vimeoLink — the video URL lives
# on the media item editor, reached via the programme's image-picker options
# (value = "<thumbnail>|<media id>"). Observed live 2026-06-12 on ID 12408.
_LINK_INPUT = '<input name="vimeoLink" value="https://www.youtube.com/watch?v=oCivERk8ZWQ">'
_THUMB_INPUT = '<input name="ThumbnailURL" value="https://i.ytimg.com/vi/oCivERk8ZWQ/mqdefault.jpg">'
META_HTML_NO_MEDIA = META_HTML.replace(_LINK_INPUT, "").replace(_THUMB_INPUT, "")

IMAGE_HTML = """
<select name="ddlThumbnail">
  <option value="https://img.youtube.com/vi/EJ2WLlPuBQ8/mqdefault.jpg|13838" selected>thumb</option>
</select>
"""

MEDIA_UPDATE_HTML = """
<form><input name="MediaName" value="YT6336SermonPM31.05.26">
<input name="vimeoLink" value="https://youtu.be/EJ2WLlPuBQ8">
<input name="MediaDuration" value="1730000"></form>
"""


def test_media_url_is_resolved_via_the_media_item_editor():
    """Meta form without vimeoLink → follow image-picker media id to
    mediaUpdate.asp and take the link from there."""
    from catalogue.ingest import live_admin

    session = PagedSession(
        [list_html("12408")],
        metas={
            "mediaProgrammeMeta.asp": META_HTML_NO_MEDIA,
            "mediaProgrammeImage.asp": IMAGE_HTML,
            "mediaUpdate.asp": MEDIA_UPDATE_HTML,
        },
    )

    stats, _records = live_admin.sync(pages=1, delay_seconds=0, session=session)

    assert stats["created"] == 1
    video = Video.objects.get(id="12408")
    assert video.url == "https://youtu.be/EJ2WLlPuBQ8"
    assert video.thumbnail == "https://img.youtube.com/vi/EJ2WLlPuBQ8/mqdefault.jpg"


def test_programmes_with_no_media_anywhere_stay_skipped():
    from catalogue.ingest import live_admin

    session = PagedSession(
        [list_html("12409")],
        metas={
            "mediaProgrammeMeta.asp": META_HTML_NO_MEDIA,
            "mediaProgrammeImage.asp": "<select name='ddlThumbnail'></select>",
        },
    )

    stats, _ = live_admin.sync(pages=1, delay_seconds=0, session=session)

    assert stats["skipped_no_media"] == 1
    assert not Video.objects.filter(id="12409").exists()


def test_meta_page_parses_to_a_dump_shaped_record():
    record = to_dump_record("12404", parse_meta_page(META_HTML))

    assert record["id"] == 12404
    assert record["ref"] == "YT6325KidsTalkAM17.05.26"
    assert record["date_added"] == "2026-05-17"  # DD/MM/YYYY parsed
    assert record["media"][0]["url"] == "https://www.youtube.com/watch?v=oCivERk8ZWQ"
    assert record["label_a"] == [{"id": 360, "name": "McBride, Dan"}]
    assert record["label_b"][0]["id"] == 146
    assert record["label_c"] == [{"id": 42, "name": "Luke"}]
    # Only SELECTED options count — Redfearn is in the dropdown but not assigned
    assert all(label["id"] != 11 for label in record["label_a"])


def test_adapted_records_flow_through_the_standard_ingest():
    record = to_dump_record("12404", parse_meta_page(META_HTML))

    stats = ingest_programmes([record])

    assert stats["created"] == 1
    video = Video.objects.get(id="12404")
    assert video.name.startswith("Luke 14:1,15-24 - Excuses")  # double space normalized
    assert [s.name for s in video.speaker.all()] == ["McBride, Dan"]
    assert "Preaching & Teaching" in [t.name for t in video.topic.all()]

    # And the cornerstone: re-sync is a no-op
    again = ingest_programmes([to_dump_record("12404", parse_meta_page(META_HTML))])
    assert again["created"] == 0 and again["updated"] == 1


@pytest.fixture
def instant_sleeps(monkeypatch):
    """Record every `time.sleep` (retry backoff and sync's own pacing between
    programmes) without actually serving it, so the tests stay instant."""
    waits = []
    monkeypatch.setattr("time.sleep", waits.append)
    return waits


class FlakySession(PagedSession):
    """Raises a transient network error on the first `failures` requests for
    any URL containing `on`, then behaves normally."""

    def __init__(self, *args, failures, on="", error=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.failures = failures
        self.on = on
        self.error = error or requests.exceptions.ReadTimeout("Read timed out.")
        self.attempts = 0

    def get(self, url, **kwargs):
        if self.on in url:
            self.attempts += 1
            if self.attempts <= self.failures:
                raise self.error
        return super().get(url, **kwargs)


def test_fetch_retries_a_wobbly_request_and_carries_on(instant_sleeps, caplog):
    """Two dropped replies from the dying old site must not end the run: the
    third attempt's response is returned, with a warning logged per retry."""
    from catalogue.ingest import live_admin

    session = FlakySession([list_html("12404")], failures=2, on="mediaProgramme.asp")

    with caplog.at_level(logging.WARNING):
        html = live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert "ID=12404" in html
    assert session.attempts == 3
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 2
    # Backoff escalates rather than hammering the server
    assert instant_sleeps == sorted(instant_sleeps) and len(instant_sleeps) == 2
    assert instant_sleeps[0] < instant_sleeps[-1]


def test_fetch_gives_up_when_the_old_site_is_genuinely_down(instant_sleeps):
    """Retries are bounded — a site that never answers still raises, so a real
    outage surfaces instead of being swallowed."""
    from catalogue.ingest import live_admin

    session = FlakySession([list_html("12404")], failures=99, on="mediaProgramme.asp")

    with pytest.raises(requests.exceptions.ReadTimeout):
        live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert session.attempts == live_admin.MAX_ATTEMPTS


def test_failures_that_are_not_wobbles_are_not_retried(instant_sleeps):
    """Retries are for a flaky connection, not for a broken request — anything
    a retry can't fix must fail on the first attempt, as it always did."""
    from catalogue.ingest import live_admin

    session = FlakySession(
        [list_html("12404")],
        failures=99,
        on="mediaProgramme.asp",
        error=requests.exceptions.TooManyRedirects("redirect loop"),
    )

    with pytest.raises(requests.exceptions.TooManyRedirects):
        live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert session.attempts == 1
    assert instant_sleeps == []


def test_a_single_blip_mid_sync_does_not_abort_the_run(instant_sleeps):
    """The whole point of #366: one wobble on a programme page costs a pause,
    not the hour's import."""
    from catalogue.ingest import live_admin

    session = FlakySession(
        [list_html("12404")],
        metas={"mediaProgrammeMeta.asp": META_HTML},
        failures=1,
        on="mediaProgrammeMeta.asp",
        error=requests.exceptions.ConnectionError("Remote end closed connection"),
    )

    stats, _records = live_admin.sync(pages=1, delay_seconds=0, session=session)

    assert stats["created"] == 1
    assert Video.objects.filter(id="12404").exists()


def test_login_retries_transient_failures_too(instant_sleeps, monkeypatch):
    from catalogue.ingest import live_admin

    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "ettie")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "secret")

    class S:
        def __init__(self):
            self.headers = {}
            self.gets = 0
            self.posts = 0

        def get(self, url, **kw):
            self.gets += 1
            if self.gets == 1:
                raise requests.exceptions.ConnectTimeout("connect timed out")

            class R:
                url = "https://clayton.tv/adminsection/login.asp"
                text = '<form action="https://clayton.tv/adminsection/login.asp"></form>'

            return R()

        def post(self, url, data=None, **kw):
            self.posts += 1
            if self.posts == 1:
                raise requests.exceptions.ReadTimeout("read timed out")

            class R:
                text = "<html>Channel Manager</html>"

            return R()

    session = S()

    assert live_admin.login(session) is True
    assert (session.gets, session.posts) == (2, 2)


def test_login_submits_the_observed_form_fields(monkeypatch):
    from catalogue.ingest import live_admin

    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "ettie")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "secret")
    posts = []

    class S:
        def __init__(self):
            self.headers = {}

        def get(self, url, **kw):
            class R:
                url = "https://clayton.tv/adminsection/login.asp?at=17:39"
                text = (
                    '<form action="https://clayton.tv/adminsection/login.asp?at=17:39" method="post">'
                    '<input name="kt_login_user"><input type="password" name="kt_login_password"></form>'
                )

            return R()

        def post(self, url, data=None, **kw):
            posts.append((url, data))

            class R:
                text = "<html>Channel Manager</html>"

            return R()

    assert live_admin.login(S()) is True
    url, data = posts[0]
    assert "login.asp" in url
    assert data["kt_login_user"] == "ettie"
    assert data["kt_login_password"] == "secret"


def test_login_failure_is_loud(monkeypatch):
    from catalogue.ingest import live_admin

    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "ettie")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "wrong")

    class S:
        def __init__(self):
            self.headers = {}

        def get(self, url, **kw):
            class R:
                url = "x"
                text = '<form action="a"></form>'

            return R()

        def post(self, url, **kw):
            class R:
                text = '<input name="kt_login_password">'  # bounced back to the form

            return R()

    with pytest.raises(live_admin.AdminAuthError):
        live_admin.login(S())
