import pytest

from tests.factories import BibleBookFactory, DemographicFactory, MinistryFactory, SpeakerFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


class TestSpeakersIndex:
    def test_lists_speakers_with_counts_alphabetically(self, client):
        zeb = SpeakerFactory(name="Zebedee, Z")
        amy = SpeakerFactory(name="Amos, A")
        SpeakerFactory(name="Silent, S")  # no videos → hidden
        for speaker in (zeb, amy):
            video = VideoFactory()
            video.speaker.add(speaker)

        page = inertia_page(client.get("/speaker/"))

        assert page["component"] == "SpeakersIndex"
        assert [s["name"] for s in page["props"]["speakers"]] == ["Amos, A", "Zebedee, Z"]
        assert page["props"]["total"] == 2

    def test_filters_by_query(self, client):
        for name in ("Keller, Tim", "Piper, John"):
            speaker = SpeakerFactory(name=name)
            video = VideoFactory()
            video.speaker.add(speaker)

        props = inertia_page(client.get("/speaker/", {"q": "piper"}))["props"]

        assert [s["name"] for s in props["speakers"]] == ["Piper, John"]


class TestBooksIndex:
    def test_groups_books_by_section_in_canonical_order(self, client):
        genesis = BibleBookFactory(name="GEN", order="1", type="LAW")
        matthew = BibleBookFactory(name="MAT", order="40", type="GOS")
        video = VideoFactory()
        video.bible_book.add(genesis, matthew)

        page = inertia_page(client.get("/book/"))

        assert page["component"] == "BooksIndex"
        groups = page["props"]["book_groups"]
        assert [g["section"] for g in groups] == ["Law", "Gospel"]
        assert groups[0]["books"][0]["name"] == "Genesis"
        assert groups[0]["books"][0]["videosCount"] == 1


class TestMinistriesIndex:
    def test_lists_ministries_with_content(self, client):
        active = MinistryFactory(name="Jesmond Parish Church")
        MinistryFactory(name="Dormant Org")  # no videos → hidden
        video = VideoFactory()
        video.ministry.add(active)

        page = inertia_page(client.get("/ministry/"))

        assert page["component"] == "MinistriesIndex"
        assert [m["name"] for m in page["props"]["ministries"]] == ["Jesmond Parish Church"]


def test_demographic_landing_redirects_to_topics(client):
    response = client.get("/demographic/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/topic/"


def test_topics_page_includes_audiences(client):
    kids = DemographicFactory(name="Kids")
    video = VideoFactory()
    video.demographic.add(kids)

    props = inertia_page(client.get("/topic/"))["props"]

    (audience,) = props["audiences"]
    assert audience["name"] == "Kids"
    assert audience["videosCount"] == 1


def test_catalogue_stub_is_gone(client):
    assert client.get("/catalogue/").status_code == 404
