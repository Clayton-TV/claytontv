"""The command palette endpoint: fast, name-only, grouped, capped — it feeds
keystroke-by-keystroke search in the ⌘K palette, so it must stay cheap."""

import pytest

from tests.factories import SeriesFactory, SpeakerFactory, TopicFactory, VideoFactory

pytestmark = pytest.mark.django_db


def get(client, q):
    return client.get("/api/palette", {"q": q})


def test_returns_matching_videos_with_watch_urls(client):
    video = VideoFactory(name="Romans 8 and the Spirit")
    VideoFactory(name="Unrelated")

    data = get(client, "romans").json()

    names = [v["name"] for v in data["videos"]]
    assert names == ["Romans 8 and the Spirit"]
    assert data["videos"][0]["url"] == f"/video/{video.id}"


def test_groups_categories_with_counts(client):
    series = SeriesFactory(name="Romans for Everyone")
    series.videos.add(VideoFactory(), VideoFactory())
    speaker = SpeakerFactory(name="Roman Speakerman")
    speaker.video_set.add(VideoFactory())
    TopicFactory(name="Romance")  # no videos: still listed, count 0

    data = get(client, "roman").json()

    by_kind = {(c["kind"], c["name"]): c for c in data["categories"]}
    assert by_kind[("Series", "Romans for Everyone")]["count"] == 2
    assert by_kind[("Speaker", "Roman Speakerman")]["count"] == 1
    assert ("Topic", "Romance") in by_kind
    assert all(c["url"] for c in data["categories"])


def test_results_are_capped(client):
    for n in range(10):
        VideoFactory(name=f"Capped video {n}")

    data = get(client, "capped").json()

    assert len(data["videos"]) == 6


def test_blank_query_returns_empty_groups(client):
    VideoFactory(name="Anything")

    data = get(client, "").json()

    assert data == {"videos": [], "categories": []}


def test_query_count_is_bounded(client, django_assert_max_num_queries):
    for n in range(30):
        series = SeriesFactory(name=f"Grace series {n}")
        series.videos.add(VideoFactory(name=f"Grace video {n}"))

    with django_assert_max_num_queries(8):
        get(client, "grace")
