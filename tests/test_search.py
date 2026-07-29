import pytest

from tests.factories import SeriesFactory, SpeakerFactory, TopicFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_search_finds_videos_by_name_and_description(client):
    VideoFactory(name="The Grace of God")
    VideoFactory(name="Unrelated", description="A talk all about grace.")
    VideoFactory(name="Something else entirely")

    page = inertia_page(client.get("/search", {"search": "grace"}))

    assert page["component"] == "Search"
    names = [v["name"] for v in page["props"]["videos"]]
    assert names == ["The Grace of God", "Unrelated"]
    assert "Found 2 videos" in page["props"]["description"]


def test_search_first_page_includes_matching_categories(client):
    video = VideoFactory()
    video.topic.add(TopicFactory(name="Grace"))
    video.speaker.add(SpeakerFactory(name="Grace Jones"))
    SeriesFactory(name="Amazing Grace")

    page = inertia_page(client.get("/search", {"search": "grace"}))

    categories = {(c["category"], c["name"]) for c in page["props"]["categories"]}
    assert ("Topics", "Grace") in categories
    assert ("Speakers", "Grace Jones") in categories
    assert ("Series", "Amazing Grace") in categories


def test_search_without_a_term_renders_the_empty_page(client, django_assert_max_num_queries):
    # #329: a bookmark of /search (or a crawler) sends no ?search= at all.
    VideoFactory(name="The Grace of God")

    # No term means no search work — the only query left is the live-stream check
    # every page runs, so neither Typesense nor the ORM fallback was consulted.
    with django_assert_max_num_queries(1):
        response = client.get("/search")
    page = inertia_page(response)

    assert response.status_code == 200
    assert page["component"] == "Search"
    assert page["props"]["title"] == "Search"
    assert page["props"]["videos"] == []
    assert page["props"]["categories"] == []


def test_search_with_only_a_page_param_renders_the_empty_page(client):
    # #329: ?page=2 with no ?search= is the same missing-key crash.
    VideoFactory(name="The Grace of God")

    response = client.get("/search", {"page": 2})
    page = inertia_page(response)

    assert response.status_code == 200
    assert page["props"]["videos"] == []


@pytest.mark.parametrize("term", ["", "   "])
def test_search_with_a_blank_term_renders_the_empty_page(client, term):
    # A blank term must not list the whole catalogue via the ORM fallback.
    VideoFactory(name="The Grace of God")

    page = inertia_page(client.get("/search", {"search": term}))

    assert page["props"]["videos"] == []


def test_search_category_labels_are_cleaned(client):
    # Phase 6: depth-prefix mojibake leaked into search category chips.
    video = VideoFactory()
    video.topic.add(TopicFactory(name="â\x88\x92â\x88\x92â\x88\x92 Grace abounds"))

    page = inertia_page(client.get("/search", {"search": "grace"}))

    topic_names = [c["name"] for c in page["props"]["categories"] if c["category"] == "Topics"]
    assert "Grace abounds" in topic_names
