import pytest

from tests.factories import SeriesFactory, SpeakerFactory, TopicFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_watch_page_renders_video_with_metadata(client):
    series = SeriesFactory(name="John's Gospel")
    video = VideoFactory(name="The Word Became Flesh", series=series)
    video.topic.add(TopicFactory(name="Incarnation"))
    video.speaker.add(SpeakerFactory(name="Jane Doe"))

    response = client.get(f"/video/{video.id}")

    assert response.status_code == 200
    page = inertia_page(response)
    assert page["component"] == "WatchVideo"

    props = page["props"]
    assert props["video"]["name"] == "The Word Became Flesh"
    metadata = props["video_metadata"]
    assert metadata["series"]["name"] == "John's Gospel"
    assert [t["name"] for t in metadata["topic"]] == ["Incarnation"]
    assert [s["name"] for s in metadata["speaker"]] == ["Jane Doe"]


def test_video_get_absolute_url_resolves(client):
    """Video.get_absolute_url reversed a non-existent route name ('video-detail'
    vs the urlconf's 'video'), crashing anything that calls it — e.g. the Django
    admin's "View on site" button."""
    video = VideoFactory()

    url = video.get_absolute_url()

    assert url == f"/video/{video.id}"
    assert client.get(url).status_code == 200
