"""The live-admin adapter, tested against synthetic HTML replicating the
observed form structure (input/textarea/select names verified in the
authenticated recon of 2026-06-12; see data/legacy_rescue/lookups/README.md)."""

import logging

import pytest
import requests
from django.test import override_settings

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
    # The shipped policy: a short pause, then a longer one. Pinned exactly —
    # "escalating" alone would let a nonsense (600, 1200) through.
    assert instant_sleeps == [2, 5]


def test_fetch_gives_up_when_the_old_site_is_genuinely_down(instant_sleeps):
    """Retries are bounded — a site that never answers still raises, so a real
    outage surfaces instead of being swallowed."""
    from catalogue.ingest import live_admin

    session = FlakySession([list_html("12404")], failures=99, on="mediaProgramme.asp")

    with pytest.raises(requests.exceptions.ReadTimeout):
        live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert session.attempts == live_admin.max_attempts() == 3


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


class Resp:
    """A response fake that answers like requests' does — including raising
    from raise_for_status(), which the older fakes stub out."""

    def __init__(self, text="", url="", status_code=200):
        self.text = text
        self.url = url
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"{self.status_code} for {self.url}", response=self)


class StatusSession:
    """Answers each GET with the next scripted status code (200 once the script
    runs out), so the retry boundary can be pinned status by status."""

    def __init__(self, statuses, body=None):
        self.statuses = list(statuses)
        self.body = list_html("12404") if body is None else body
        self.requests_made = 0

    def get(self, url, **kwargs):
        scripted = self.requests_made < len(self.statuses)
        status = self.statuses[self.requests_made] if scripted else 200
        self.requests_made += 1
        return Resp(self.body, url, status)


@pytest.mark.parametrize("status", [500, 502, 503, 504, 429])
def test_an_overloaded_or_rate_limited_answer_is_retried(status, instant_sleeps):
    """#366's acceptance line is "only give up if the site is genuinely
    unreachable rather than just slow" — a classic-ASP box answering 503, or a
    proxy answering 429, IS just slow. Previously these did 1 GET and died."""
    from catalogue.ingest import live_admin

    session = StatusSession([status, status])

    html = live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert "ID=12404" in html
    assert session.requests_made == 3
    assert instant_sleeps == [2, 5]


@pytest.mark.parametrize("status", [400, 404, 410, 418])
def test_a_broken_request_still_fails_fast(status, instant_sleeps):
    """The other side of the boundary: a 404 (or any non-429 4xx) is a real
    answer that a retry cannot improve. One request, no sleeps."""
    from catalogue.ingest import live_admin

    session = StatusSession([status])

    with pytest.raises(requests.exceptions.HTTPError):
        live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert session.requests_made == 1
    assert instant_sleeps == []


def test_a_server_that_only_ever_503s_still_gives_up(instant_sleeps):
    """Retrying 5xx must not become an infinite hammer on a downed server."""
    from catalogue.ingest import live_admin

    session = StatusSession([503] * 99)

    with pytest.raises(requests.exceptions.HTTPError):
        live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert session.requests_made == live_admin.max_attempts() == 3
    assert instant_sleeps == [2, 5]


def test_the_shipped_retry_policy_is_three_attempts_two_then_five_seconds():
    from django.conf import settings

    from catalogue.ingest import live_admin

    assert tuple(settings.LEGACY_ADMIN_RETRY_WAITS_SECONDS) == (2, 5)
    assert live_admin.retry_waits() == (2, 5)
    assert live_admin.max_attempts() == 3


@override_settings(LEGACY_ADMIN_RETRY_WAITS_SECONDS=(0.5, 1, 2, 3))
def test_retry_patience_is_configurable_for_the_long_catch_up_run(instant_sleeps):
    """#287's catch-up run wants more patience than the hourly cron — the knob
    is a setting (env LEGACY_ADMIN_RETRY_WAITS), not a code edit."""
    from catalogue.ingest import live_admin

    session = FlakySession([list_html("12404")], failures=4, on="mediaProgramme.asp")

    html = live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert "ID=12404" in html
    assert session.attempts == live_admin.max_attempts() == 5
    assert instant_sleeps == [0.5, 1, 2, 3]


@override_settings(LEGACY_ADMIN_RETRY_WAITS_SECONDS=(1000, 1000, 1000))
def test_an_over_generous_setting_cannot_park_the_hourly_run(instant_sleeps):
    """The cron holds a flock; a typo'd wait must not sit on it for hours, so
    the waits are trimmed to a total budget per request."""
    from catalogue.ingest import live_admin

    session = FlakySession([list_html("12404")], failures=99, on="mediaProgramme.asp")

    with pytest.raises(requests.exceptions.ReadTimeout):
        live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert sum(instant_sleeps) <= live_admin.RETRY_BUDGET_SECONDS


@override_settings(LEGACY_ADMIN_RETRY_WAITS_SECONDS=())
def test_retries_can_be_turned_off_entirely(instant_sleeps):
    from catalogue.ingest import live_admin

    session = FlakySession([list_html("12404")], failures=99, on="mediaProgramme.asp")

    with pytest.raises(requests.exceptions.ReadTimeout):
        live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert session.attempts == 1
    assert instant_sleeps == []


class LapsedSession:
    """A session whose cookie has expired mid-run: content GETs land on
    /accessdenied.html until a login POST mints a working one."""

    LOGIN_BODY = '<form action="https://clayton.tv/adminsection/login.asp?at=1"></form>'

    def __init__(self, login_works=True, wobbles=0):
        self.headers = {}
        self.login_works = login_works
        self.wobbles = wobbles
        self.gets = 0
        self.posts = 0
        self.logged_in = False

    def _wobble(self):
        if self.wobbles:
            self.wobbles -= 1
            raise requests.exceptions.ConnectionError("Remote end closed connection")

    def get(self, url, **kwargs):
        self.gets += 1
        self._wobble()
        if url.endswith("/adminsection/"):  # the login form itself
            return Resp(self.LOGIN_BODY, url)
        if not self.logged_in:
            return Resp("denied", "https://clayton.tv/adminsection/accessdenied.html")
        return Resp(list_html("12404"), url)

    def post(self, url, data=None, **kwargs):
        self.posts += 1
        self._wobble()
        self.logged_in = self.login_works
        return Resp("<html>Channel Manager</html>", url)


@pytest.fixture
def credentials(monkeypatch):
    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "ettie")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "secret")
    monkeypatch.delenv("LEGACY_ADMIN_COOKIE", raising=False)


def test_a_session_that_lapses_mid_run_is_re_minted_and_the_page_refetched(instant_sleeps, credentials):
    from catalogue.ingest import live_admin

    session = LapsedSession()

    html = live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert "ID=12404" in html
    # denied page + login form + the retried page; exactly one credential POST
    assert (session.gets, session.posts) == (3, 1)


def test_a_lapse_plus_wobbles_still_lands_but_only_logs_in_once(instant_sleeps, credentials):
    """Retry-plus-re-login is the amplification case: wobbles inside a re-login
    must not multiply into repeated credential submissions."""
    from catalogue.ingest import live_admin

    session = LapsedSession(wobbles=2)

    html = live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert "ID=12404" in html
    # 2 dropped GETs, the denied page, the login form, the retried page
    assert (session.gets, session.posts) == (5, 1)


def test_only_one_re_login_is_attempted_per_fetch(instant_sleeps, credentials):
    """If the fresh session is refused too, give up loudly — a legacy admin
    locks accounts out, so a login storm is worse than a failed hour."""
    from catalogue.ingest import live_admin

    session = LapsedSession(login_works=False)

    with pytest.raises(live_admin.AdminAuthError):
        live_admin.fetch(session, "mediaProgramme.asp?offset=0")

    assert session.posts == 1


def test_a_retried_login_refetches_the_form_instead_of_replaying_the_token(instant_sleeps, credentials):
    """The login action carries an `at=` token. If it is single-use, replaying
    the same POST bounces back to the form and raises a misleading "check your
    credentials" for what was only a network blip — so re-fetch the form."""
    from catalogue.ingest import live_admin

    posted_to = []

    class TokenSession:
        def __init__(self):
            self.headers = {}
            self.forms_served = 0

        def get(self, url, **kwargs):
            self.forms_served += 1
            action = f"https://clayton.tv/adminsection/login.asp?at=token{self.forms_served}"
            return Resp(f'<form action="{action}"></form>', action)

        def post(self, url, data=None, **kwargs):
            posted_to.append(url)
            if len(posted_to) == 1:
                raise requests.exceptions.ReadTimeout("read timed out")
            return Resp("<html>Channel Manager</html>", url)

    assert live_admin.login(TokenSession()) is True
    assert [url.rsplit("=", 1)[-1] for url in posted_to] == ["token1", "token2"]


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
    # Each attempt re-fetches the form before posting, so the dropped POST
    # costs one extra GET rather than replaying a spent login URL.
    assert (session.gets, session.posts) == (3, 2)


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
