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


@pytest.mark.parametrize("page", ["999", "0", "-3", "not-a-page"])
def test_search_clamps_impossible_pages(client, page):
    # Crawlers walk made-up page numbers; the ORM fallback used to 500 on them.
    VideoFactory(name="The Grace of God")

    response = client.get("/search", {"search": "grace", "page": page})
    props = inertia_page(response)["props"]

    assert response.status_code == 200
    assert [v["name"] for v in props["videos"]] == ["The Grace of God"]
    assert "page 1 of 1" in props["description"]
    assert props["has_prev_page"] is False
    assert props["has_next_page"] is False


def test_search_clamped_last_page_still_shows_categories(client):
    # Clamping to page 1 means page 1's props, categories included.
    video = VideoFactory(name="Grace")
    video.topic.add(TopicFactory(name="Grace"))

    props = inertia_page(client.get("/search", {"search": "grace", "page": 999}))["props"]

    assert ("Topics", "Grace") in {(c["category"], c["name"]) for c in props["categories"]}


def test_search_category_labels_are_cleaned(client):
    # Phase 6: depth-prefix mojibake leaked into search category chips.
    video = VideoFactory()
    video.topic.add(TopicFactory(name="â\x88\x92â\x88\x92â\x88\x92 Grace abounds"))

    page = inertia_page(client.get("/search", {"search": "grace"}))

    topic_names = [c["name"] for c in page["props"]["categories"] if c["category"] == "Topics"]
    assert "Grace abounds" in topic_names


def test_search_sends_the_props_the_pagination_nav_needs(client):
    # #329: the nav needs num_pages to draw page numbers at all, and the
    # effective page so Prev/Next agree with the results actually shown.
    for n in range(30):
        VideoFactory(name=f"Grace {n}")

    props = inertia_page(client.get("/search", {"search": "grace", "page": 2}))["props"]

    assert props["num_pages"] == 2
    assert props["page"] == 2


def test_search_without_a_term_still_sends_the_pagination_props(client):
    props = inertia_page(client.get("/search"))["props"]

    assert props["num_pages"] == 1
    assert props["page"] == 1


@pytest.mark.parametrize("requested", ["999", "0", "-3", "not-a-page"])
def test_search_reports_the_effective_page_after_clamping(client, requested):
    # Prev used to render enabled on a clamped page because the nav read the
    # requested page out of the URL: clicking it re-clamped to the same page.
    VideoFactory(name="The Grace of God")

    props = inertia_page(client.get("/search", {"search": "grace", "page": requested}))["props"]

    assert props["page"] == 1
    assert props["num_pages"] == 1
