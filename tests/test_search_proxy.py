"""The search proxy: palette + search served by Typesense with an ORM fallback.

The Typesense path is exercised by monkeypatching the ``catalogue.search`` query
helpers (no live server needed); the fallback path is exercised by making those
helpers raise. A guarded live section hits the real endpoints over HTTP to prove
typo/synonym tolerance end-to-end (skips without a container).
"""

import pytest

from app.views import MAX_SEARCH_PAGE
from catalogue import search
from catalogue.search import Hit, SearchUnavailableError
from tests.factories import VideoFactory
from tests.utils import inertia_page, typesense_env_config

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# Palette
# --------------------------------------------------------------------------- #


def test_palette_uses_typesense_when_available(client, monkeypatch):
    video = Hit(kind="video", pk="7", name="Romans 8", url="/video/7", videos_count=0, date_display="2026-01-01")
    monkeypatch.setattr(search, "search_videos", lambda q, **kw: ([video], 1))
    monkeypatch.setattr(
        search,
        "search_categories",
        lambda q, **kw: [
            Hit(kind="series", pk="9", name="Romans", url="/series/9", videos_count=3),
            Hit(kind="book", pk="45", name="Romans", url="/book/ROM", videos_count=120),
        ],
    )

    data = client.get("/api/palette", {"q": "romans"}).json()

    # The date round-trips from the index doc to the payload (cross-path parity).
    assert data["videos"] == [{"id": "7", "name": "Romans 8", "url": "/video/7", "date": "2026-01-01"}]
    by_kind = {(c["kind"], c["name"]): c for c in data["categories"]}
    assert by_kind[("Series", "Romans")]["count"] == 3
    assert by_kind[("Book", "Romans")]["count"] == 120


def test_palette_falls_back_to_orm_when_typesense_unavailable(client, monkeypatch):
    def boom(*a, **k):
        raise SearchUnavailableError("down")

    monkeypatch.setattr(search, "search_videos", boom)
    VideoFactory(name="Grace Abounding")

    data = client.get("/api/palette", {"q": "grace"}).json()

    assert [v["name"] for v in data["videos"]] == ["Grace Abounding"]


def test_palette_reports_unexpected_errors_to_sentry(client, monkeypatch):
    captured = []

    def boom(*a, **k):
        raise ValueError("bug in proxy")

    monkeypatch.setattr(search, "search_videos", boom)
    monkeypatch.setattr("app.views.sentry_sdk.capture_exception", lambda *a, **k: captured.append(True))
    VideoFactory(name="Grace Abounding")

    data = client.get("/api/palette", {"q": "grace"}).json()

    assert captured == [True]  # unexpected error reported
    assert [v["name"] for v in data["videos"]] == ["Grace Abounding"]  # still served


# --------------------------------------------------------------------------- #
# Search page
# --------------------------------------------------------------------------- #


def test_search_uses_typesense_and_hydrates_in_relevance_order(client, monkeypatch):
    v1 = VideoFactory(name="First")
    v2 = VideoFactory(name="Second")
    v3 = VideoFactory(name="Third")
    ranked = [v3, v1, v2]  # Typesense relevance order, not DB order
    hits = [Hit(kind="video", pk=str(v.id), name=v.name, url=f"/video/{v.id}", videos_count=0) for v in ranked]

    monkeypatch.setattr(search, "search_videos", lambda q, **kw: (hits, 50))
    monkeypatch.setattr(
        search,
        "search_categories",
        lambda q, **kw: [Hit(kind="series", pk="9", name="A Series", url="/series/9", videos_count=4)],
    )

    props = inertia_page(client.get("/search", {"search": "x"}))["props"]

    assert [v["id"] for v in props["videos"]] == [str(v3.id), str(v1.id), str(v2.id)]
    assert props["description"] == "Found 50 videos (page 1 of 3)"
    assert props["has_prev_page"] is False
    assert props["has_next_page"] is True  # 24 < 50
    assert props["categories"][0] == {"category": "Series", "name": "A Series", "videosCount": 4, "url": "/series/9"}


def test_search_page_two_has_no_categories(client, monkeypatch):
    monkeypatch.setattr(search, "search_videos", lambda q, **kw: ([], 50))
    monkeypatch.setattr(search, "search_categories", lambda q, **kw: [])

    props = inertia_page(client.get("/search", {"search": "x", "page": "2"}))["props"]

    assert "categories" not in props
    assert props["has_prev_page"] is True


def test_search_clamps_pages_past_the_end_to_the_last_page(client, monkeypatch):
    # Typesense errors past its 10k result window, which used to mean a crawler
    # asking for page 999 tripped the "unexpected error" path into Sentry.
    video = VideoFactory(name="Romans 8")
    hit = Hit(kind="video", pk=str(video.id), name=video.name, url=f"/video/{video.id}", videos_count=0)
    requested_pages = []

    def fake_search(query, *, page=1, **kw):
        requested_pages.append(page)
        return ([hit], 30) if page == 2 else ([], 30)  # 30 results = 2 pages of 24

    monkeypatch.setattr(search, "search_videos", fake_search)

    props = inertia_page(client.get("/search", {"search": "romans", "page": "999"}))["props"]

    # Capped into Typesense's window first, then clamped to the last real page.
    assert requested_pages == [MAX_SEARCH_PAGE, 2]
    assert [v["name"] for v in props["videos"]] == ["Romans 8"]
    assert props["description"] == "Found 30 videos (page 2 of 2)"
    assert props["has_next_page"] is False


def test_search_never_advertises_pages_past_typesenses_window(client, monkeypatch):
    # More results than Typesense will page through: the last page it can serve
    # is the last page we may offer, or we invent an endless run of URLs.
    monkeypatch.setattr(search, "search_videos", lambda q, **kw: ([], 20_000))

    props = inertia_page(client.get("/search", {"search": "god", "page": "999"}))["props"]

    assert props["description"] == f"Found 20000 videos (page {MAX_SEARCH_PAGE} of {MAX_SEARCH_PAGE})"
    assert props["has_next_page"] is False


def test_search_clamped_to_page_one_still_fetches_categories(client, monkeypatch):
    requested_pages = []

    def fake_search(query, *, page=1, **kw):
        requested_pages.append(page)
        return ([], 5)  # one page of results

    monkeypatch.setattr(search, "search_videos", fake_search)
    monkeypatch.setattr(
        search,
        "search_categories",
        lambda q, **kw: [Hit(kind="series", pk="9", name="A Series", url="/series/9", videos_count=4)],
    )

    props = inertia_page(client.get("/search", {"search": "x", "page": "999"}))["props"]

    assert requested_pages == [MAX_SEARCH_PAGE, 1]
    assert props["categories"][0]["name"] == "A Series"


def test_search_does_not_re_ask_typesense_when_there_are_no_results(client, monkeypatch):
    requested_pages = []

    def fake_search(query, *, page=1, **kw):
        requested_pages.append(page)
        return ([], 0)

    monkeypatch.setattr(search, "search_videos", fake_search)
    monkeypatch.setattr(search, "search_categories", lambda q, **kw: [])

    props = inertia_page(client.get("/search", {"search": "asdfgh", "page": "5"}))["props"]

    assert requested_pages == [5]  # nothing to clamp to; page 5 was empty already
    assert props["videos"] == []
    assert props["description"] == "Found 0 videos (page 1 of 1)"


@pytest.mark.parametrize("page", ["0", "-3", "not-a-page"])
def test_search_never_asks_typesense_for_an_impossible_page(client, monkeypatch, page):
    requested_pages = []

    def fake_search(query, *, page=1, **kw):
        requested_pages.append(page)
        return ([], 30)

    monkeypatch.setattr(search, "search_videos", fake_search)
    monkeypatch.setattr(search, "search_categories", lambda q, **kw: [])

    props = inertia_page(client.get("/search", {"search": "romans", "page": page}))["props"]

    assert requested_pages == [1]
    assert props["has_prev_page"] is False


def test_search_falls_back_to_orm_when_typesense_unavailable(client, monkeypatch):
    def boom(*a, **k):
        raise SearchUnavailableError("down")

    monkeypatch.setattr(search, "search_videos", boom)
    VideoFactory(name="Unique Sermon Title")

    props = inertia_page(client.get("/search", {"search": "Unique Sermon"}))["props"]

    assert [v["name"] for v in props["videos"]] == ["Unique Sermon Title"]


# --------------------------------------------------------------------------- #
# Guarded live round-trip over HTTP — skipped without a reachable Typesense.
# --------------------------------------------------------------------------- #


@pytest.fixture
def live_index(settings):
    # test_settings disables Typesense; opt back in from the environment so the
    # view itself routes through Typesense for this test only.
    config = typesense_env_config()
    if config is None:
        pytest.skip("Typesense not configured (set TYPESENSE_API_KEY)")
    settings.TYPESENSE = config
    client_ = search.get_client()
    try:
        client_.collections.retrieve()
    except Exception:
        pytest.skip("Typesense not reachable")
    return client_


def test_palette_typo_tolerance_over_http(client, live_index):
    VideoFactory(name="The Sermon on the Mount")
    search.reindex()

    data = client.get("/api/palette", {"q": "sermom"}).json()  # typo

    assert any("Sermon on the Mount" in v["name"] for v in data["videos"])
