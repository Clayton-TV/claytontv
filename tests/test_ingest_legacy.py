"""Feature tests for the idempotent dump importer, run against REAL records
sampled from the legacy dump (tests/fixtures/legacy_programmes_sample.json)
— per the project rule: never assume the data, verify it."""

import json
from pathlib import Path

import pytest

from catalogue.ingest.legacy import ingest_programmes
from catalogue.models import Bible_Book, RelatedResource, Video

pytestmark = pytest.mark.django_db

FIXTURE = Path(__file__).parent / "fixtures" / "legacy_programmes_sample.json"


@pytest.fixture
def programmes():
    return json.loads(FIXTURE.read_text())


def test_ingests_real_records_without_dropping_data(programmes):
    stats = ingest_programmes(programmes)

    assert stats["created"] >= 3
    video = Video.objects.get(id="693")
    # Primary URL is the first Video media; the advert is excluded entirely
    assert video.url == "https://vimeo.com/97323692"
    assert all("CTVAd" not in alt["url"] for alt in video.alternate_urls)
    # Trailing-space speaker name normalized, linked by legacy ID
    assert [s.name for s in video.speaker.all()] == ["Redfearn, Jonathan"]
    assert video.speaker.first().id == "11"
    # Topic depth prefix stripped
    assert "The Sovereignty of God" in [t.name for t in video.topic.all()]
    # label_c id == canonical book order
    book = Bible_Book.objects.filter(order="9").first()
    if book:
        assert book in video.bible_book.all()
    # Transcript/audio links preserved as resources (the old chain dropped them)
    kinds = set(video.related_resources.values_list("kind", flat=True))
    assert kinds == {"transcript", "audio"}


def test_multiple_video_media_are_kept_as_alternates(programmes):
    multi = next(p for p in programmes if len([m for m in p.get("media", []) if m.get("type") == "Video"]) > 1)
    ingest_programmes(programmes)

    video = Video.objects.get(id=str(multi["id"]))
    assert len(video.alternate_urls) >= 1
    assert all({"url", "platform"} <= set(alt) for alt in video.alternate_urls)


def test_programmes_without_playable_media_are_skipped(programmes):
    stats = ingest_programmes(programmes)
    empty = [p for p in programmes if not [m for m in p.get("media", []) if m.get("type") == "Video"]]

    assert stats["skipped_no_media"] == len(empty)
    for p in empty:
        assert not Video.objects.filter(id=str(p["id"])).exists()


def test_running_twice_changes_nothing(programmes):
    """The core Epic 2 guarantee: re-ingestion is a no-op, never a wipe."""
    first = ingest_programmes(programmes)
    snapshot = list(Video.objects.order_by("id").values("id", "name", "url", "alternate_urls", "is_livestream"))
    resource_count = RelatedResource.objects.count()

    second = ingest_programmes(programmes)

    assert second["created"] == 0
    assert second["updated"] == first["created"]
    assert list(Video.objects.order_by("id").values("id", "name", "url", "alternate_urls", "is_livestream")) == snapshot
    assert RelatedResource.objects.count() == resource_count


def test_upsert_corrects_changed_fields_without_duplicating(programmes):
    ingest_programmes(programmes)
    Video.objects.filter(id="693").update(name="Vandalized title")

    ingest_programmes(programmes)

    assert Video.objects.filter(id="693").count() == 1
    assert Video.objects.get(id="693").name == "1 Samuel 12 - Here I Stand - JPC Sermon"
