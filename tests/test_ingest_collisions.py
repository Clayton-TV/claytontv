"""Duplicate-URL programmes exist in the real dump (37 duplicate refs found
in recon); the importer must keep the first, report the rest, and stay
idempotent — the legacy chain crashed or silently skipped."""

import pytest

from catalogue.ingest.legacy import ingest_programmes
from catalogue.models import Video

pytestmark = pytest.mark.django_db


def programme(pid, url, name="A talk"):
    return {
        "id": pid,
        "ref": f"REF{pid}",
        "name": name,
        "date_added": "2020-01-01",
        "media": [{"id": pid * 10, "type": "Video", "url": url}],
    }


def test_duplicate_urls_keep_first_and_report_rest():
    stats = ingest_programmes(
        [
            programme(1, "https://vimeo.com/111"),
            programme(2, "https://vimeo.com/111", name="Duplicate listing"),
            programme(3, "https://vimeo.com/333"),
        ]
    )

    assert stats["created"] == 2
    assert stats["skipped_url_collision"] == 1
    assert stats["url_collisions"] == [{"programme_id": 2, "kept_video_id": "1"}]
    assert not Video.objects.filter(id="2").exists()


def test_collision_handling_is_idempotent():
    records = [programme(1, "https://vimeo.com/111"), programme(2, "https://vimeo.com/111")]
    ingest_programmes(records)

    stats = ingest_programmes(records)

    assert stats["created"] == 0
    assert stats["updated"] == 1
    assert stats["skipped_url_collision"] == 1
    assert Video.objects.count() == 1
