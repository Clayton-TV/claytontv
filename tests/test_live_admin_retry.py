import pytest
import requests

from catalogue.ingest import live_admin


class Response:
    def __init__(self, text="ok", url="https://clayton.tv/adminsection/page.asp", status_code=200, headers=None):
        self.text = text
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(response=self)


class Session:
    def __init__(self, gets, post=None):
        self.gets = list(gets)
        self.post_response = post or Response()
        self.get_urls = []
        self.posts = []
        self.headers = {}

    def get(self, url, **kwargs):
        self.get_urls.append((url, kwargs))
        item = self.gets.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def post(self, url, **kwargs):
        self.posts.append((url, kwargs))
        if isinstance(self.post_response, Exception):
            raise self.post_response
        return self.post_response


def test_fetch_retries_timeouts_and_overload(monkeypatch):
    sleeps = []
    monkeypatch.setattr(live_admin.time, "sleep", sleeps.append)
    session = Session(
        [
            requests.exceptions.ReadTimeout(),
            Response(status_code=503),
            Response("recovered"),
        ]
    )

    assert live_admin.fetch(session, "mediaProgramme.asp") == "recovered"
    assert len(session.get_urls) == 3
    assert sleeps == [2, 5]


def test_fetch_does_not_retry_a_client_error():
    session = Session([Response(status_code=404)])

    with pytest.raises(requests.exceptions.HTTPError):
        live_admin.fetch(session, "missing.asp")

    assert len(session.get_urls) == 1


def test_fetch_stops_after_three_attempts(monkeypatch):
    monkeypatch.setattr(live_admin.time, "sleep", lambda _wait: None)
    session = Session([requests.exceptions.ReadTimeout()] * 3)

    with pytest.raises(requests.exceptions.ReadTimeout):
        live_admin.fetch(session, "mediaProgramme.asp")

    assert len(session.get_urls) == 3


def test_fetch_reauthenticates_after_retried_overload_ends_in_a_401(monkeypatch):
    monkeypatch.setattr(live_admin.time, "sleep", lambda _wait: None)
    logins = []
    monkeypatch.setattr(live_admin, "login", lambda _session: logins.append(True) or True)
    session = Session(
        [
            Response(status_code=503),
            Response(status_code=503),
            Response(url="https://clayton.tv/adminsection/accessdenied.html", status_code=401),
            Response("recovered"),
        ]
    )

    assert live_admin.fetch(session, "mediaProgramme.asp") == "recovered"
    assert logins == [True]
    assert len(session.get_urls) == 4


def test_login_retries_the_form_get_but_not_the_credential_post(monkeypatch):
    sleeps = []
    monkeypatch.setattr(live_admin.time, "sleep", sleeps.append)
    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "user")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "password")
    session = Session(
        [
            requests.exceptions.ConnectTimeout(),
            Response('<form action="https://clayton.tv/adminsection/login.asp?at=secret-token"></form>'),
        ]
    )

    assert live_admin.login(session) is True
    assert len(session.get_urls) == 2
    assert len(session.posts) == 1
    assert sleeps == [2]


def test_login_does_not_replay_credentials_after_a_transport_failure(monkeypatch):
    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "user")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "password")
    session = Session(
        [Response('<form action="https://clayton.tv/adminsection/login.asp?at=secret-token"></form>')],
        post=requests.exceptions.ReadTimeout(),
    )

    with pytest.raises(live_admin.AdminAuthError, match="not retried"):
        live_admin.login(session)

    assert len(session.posts) == 1


def test_login_allows_same_origin_301_as_a_safe_get(monkeypatch):
    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "user")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "password")
    session = Session(
        [
            Response('<form action="https://clayton.tv/adminsection/login.asp"></form>'),
            Response("dashboard", "https://clayton.tv/adminsection/dashboard.asp"),
        ],
        post=Response(
            status_code=301,
            headers={"Location": "/adminsection/dashboard.asp"},
            url="https://clayton.tv/adminsection/login.asp",
        ),
    )

    assert live_admin.login(session) is True
    assert [url for url, _ in session.get_urls] == [
        "https://clayton.tv/adminsection/",
        "https://clayton.tv/adminsection/dashboard.asp",
    ]


def test_login_refuses_a_cross_origin_307_without_following_it(monkeypatch):
    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "user")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "password")
    session = Session(
        [Response('<form action="https://clayton.tv/adminsection/login.asp"></form>')],
        post=Response(
            status_code=307,
            headers={"Location": "https://evil.example/collect"},
            url="https://clayton.tv/adminsection/login.asp",
        ),
    )

    with pytest.raises(live_admin.AdminAuthError, match="redirect"):
        live_admin.login(session)

    assert len(session.posts) == 1
    assert len(session.get_urls) == 1


def test_login_rejects_an_offsite_form_without_echoing_its_token(monkeypatch):
    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "user")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "password")
    session = Session([Response('<form action="https://evil.example/collect?at=secret-token"></form>')])

    with pytest.raises(live_admin.AdminAuthError) as error:
        live_admin.login(session)

    assert "secret-token" not in str(error.value)
    assert not session.posts


def test_lapsed_session_reauthenticates_once(monkeypatch):
    monkeypatch.setenv("LEGACY_ADMIN_USERNAME", "user")
    monkeypatch.setenv("LEGACY_ADMIN_PASSWORD", "password")
    session = Session(
        [
            Response(url="https://clayton.tv/adminsection/accessdenied.html"),
            Response('<form action="https://clayton.tv/adminsection/login.asp"></form>'),
            Response("recovered"),
        ]
    )

    assert live_admin.fetch(session, "mediaProgramme.asp") == "recovered"
    assert len(session.posts) == 1
