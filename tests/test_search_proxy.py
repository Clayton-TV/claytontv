"""The search proxy: palette + search served by Typesense with an ORM fallback.

The Typesense path is exercised by monkeypatching the ``catalogue.search`` query
helpers (no live server needed); the fallback path is exercised by making those
helpers raise. A guarded live section hits the real endpoints over HTTP to prove
typo/synonym tolerance end-to-end (skips without a container).
"""

import pytest

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
