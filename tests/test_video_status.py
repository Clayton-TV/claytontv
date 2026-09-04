"""Video.status: a draft must be invisible on every public surface, while a
published video shows normally. This is the load-bearing guarantee for the
Studio (drafts staged before they go live)."""

import pytest
from django.contrib.auth import get_user_model

from catalogue.models.video import DRAFT, Video
from tests.factories import (
    BibleBookFactory,
    ChannelFactory,
    DemographicFactory,
    MinistryFactory,
    SeriesFactory,
    SpeakerFactory,
    TopicFactory,
    VideoFactory,
)
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db

PUB = "Published Romans talk"
DRF = "Draft Romans talk"


def _names(items, key="name"):
    return {i[key] for i in items}


def test_published_manager_excludes_drafts():
    VideoFactory(name=PUB)
    VideoFactory(name=DRF, status=DRAFT)
    names = set(Video.objects.published().values_list("name", flat=True))
    assert PUB in names
    assert DRF not in names


def test_homepage_and_latest_hide_drafts(client):
    VideoFactory(name=PUB)
    VideoFactory(name=DRF, status=DRAFT)

    home = inertia_page(client.get("/"))["props"]
    assert PUB in _names(home["latest_videos"])
    assert DRF not in _names(home["latest_videos"])

    feed = inertia_page(client.get("/latest/"))["props"]
    feed_names = {item.get("name") for group in feed["groups"] for item in group["items"]}
    assert PUB in feed_names
    assert DRF not in feed_names


def test_palette_and_search_hide_drafts(client):
    # No Typesense in tests → both go through the ORM fallback path.
    VideoFactory(name=PUB)
    VideoFactory(name=DRF, status=DRAFT)

    palette = client.get("/api/palette", {"q": "romans"}).json()
    assert PUB in _names(palette["videos"])
    assert DRF not in _names(palette["videos"])

    results = inertia_page(client.get("/search", {"search": "romans"}))["props"]
    assert PUB in _names(results["videos"])
    assert DRF not in _names(results["videos"])


def test_browse_hides_drafts(client):
    VideoFactory(name=PUB)
    VideoFactory(name=DRF, status=DRAFT)

    page = inertia_page(client.get("/browse/"))["props"]
    assert PUB in _names(page["videos"])
    assert DRF not in _names(page["videos"])


def test_relation_pages_hide_drafts(client):
    speaker = SpeakerFactory(name="Paula Preacher")
    series = SeriesFactory(name="Romans Course")
    topic = TopicFactory(name="Grace")
    book = BibleBookFactory()
    channel = ChannelFactory(name="Trinity Church")
    ministry = MinistryFactory(name="City Mission")
    audience = DemographicFactory(name="Adults")

    pub = VideoFactory(name=PUB, channel=channel)
    drf = VideoFactory(name=DRF, status=DRAFT, channel=channel)
    for v in (pub, drf):
        v.speaker.add(speaker)
        v.topic.add(topic)
        v.bible_book.add(book)
        v.ministry.add(ministry)
        v.demographic.add(audience)
        series.videos.add(v)

    # Hit each detail page by its canonical URL and assert draft is absent.
    for url in (
        speaker.get_absolute_url(),
        topic.get_absolute_url(),
        book.get_absolute_url(),
        channel.get_absolute_url(),
        ministry.get_absolute_url(),
        audience.get_absolute_url(),
        series.get_absolute_url(),
    ):
        props = inertia_page(client.get(url))["props"]
        videos = props.get("videos") or props.get("episodes") or []
        names = _names(videos)
        assert PUB in names, f"published video missing from {url}"
        assert DRF not in names, f"draft leaked on {url}"


def test_watch_page_draft_is_404_for_anon_but_visible_to_staff(client):
    draft = VideoFactory(name=DRF, status=DRAFT)

    assert client.get(f"/video/{draft.id}").status_code == 404

    staff = get_user_model().objects.create_user("ed", password="x", is_staff=True)
    client.force_login(staff)
    assert client.get(f"/video/{draft.id}").status_code == 200


def test_published_watch_page_still_200(client):
    pub = VideoFactory(name=PUB)
    assert client.get(f"/video/{pub.id}").status_code == 200
