import pytest

from catalogue.models import RelatedResource
from tests.factories import BibleBookFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_passage_badge_links_to_the_chapter(client):
    luke = BibleBookFactory(name="LUK", order="42", type="GOS")
    video = VideoFactory(name="Luke 15:11-24 - The Prodigal Son - JPC Sermon")
    video.bible_book.add(luke)

    props = inertia_page(client.get(f"/video/{video.id}"))["props"]

    assert props["passage"]["label"] == "Luke 15:11-24"
    assert props["passage"]["url"] == "/book/LUK?chapter=15"


def test_no_passage_badge_for_topical_titles(client):
    luke = BibleBookFactory(name="LUK", order="42", type="GOS")
    video = VideoFactory(name="Word Alive - A topical talk")
    video.bible_book.add(luke)

    props = inertia_page(client.get(f"/video/{video.id}"))["props"]

    assert props["passage"] is None


def test_related_resources_are_surfaced(client):
    video = VideoFactory()
    RelatedResource.objects.create(video=video, kind="transcript", url="https://printandaudio.org.uk/x")
    RelatedResource.objects.create(video=video, kind="audio", url="https://printandaudio.org.uk/y")

    props = inertia_page(client.get(f"/video/{video.id}"))["props"]

    kinds = {r["kind"] for r in props["resources"]}
    assert kinds == {"transcript", "audio"}


def test_no_resources_when_none_exist(client):
    video = VideoFactory()

    props = inertia_page(client.get(f"/video/{video.id}"))["props"]

    assert props["resources"] == []
