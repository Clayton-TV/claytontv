import pytest

from tests.factories import (
    BibleBookFactory,
    DemographicFactory,
    MinistryFactory,
    SeriesFactory,
    SpeakerFactory,
    TopicFactory,
    VideoFactory,
)
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


class TestSpeakersIndex:
    """Lookup-first pivot (docs/DESIGN_SPEC.md): featured tier + search,
    long tail scroll-deferred — never a 662-card dump."""

    def speakers_with_talks(self, spec):
        for name, talks in spec:
            speaker = SpeakerFactory(name=name)
            for _ in range(talks):
                video = VideoFactory()
                video.speaker.add(speaker)

    def test_featured_voices_are_the_deepest_catalogues(self, client):
        self.speakers_with_talks([("Minor, M", 1), ("Major, M", 3), ("Middle, M", 2)])
        SpeakerFactory(name="Silent, S")  # no videos → hidden everywhere

        page = inertia_page(client.get("/speaker/"))

        assert page["component"] == "SpeakersIndex"
        props = page["props"]
        assert [s["name"] for s in props["featured"]] == ["Major, M", "Middle, M", "Minor, M"]
        assert props["total"] == 3
        assert "all_speakers" not in props  # long tail loads on scroll

    def test_featured_includes_known_for_series(self, client):
        speaker = SpeakerFactory(name="Steele, Dominic")
        series = SeriesFactory(name="The Pastor's Heart")
        for _ in range(2):
            video = VideoFactory()
            video.speaker.add(speaker)
            series.videos.add(video)

        props = inertia_page(client.get("/speaker/"))["props"]

        assert props["featured"][0]["knownFor"] == "The Pastor's Heart"

    def test_all_speakers_load_on_scroll_grouped_a_to_z(self, client):
        import json

        self.speakers_with_talks([("Zebedee, Z", 1), ("Amos, A", 1), ("Abel, A", 1)])

        response = client.get(
            "/speaker/",
            HTTP_X_INERTIA="true",
            HTTP_X_INERTIA_PARTIAL_COMPONENT="SpeakersIndex",
            HTTP_X_INERTIA_PARTIAL_DATA="all_speakers",
        )

        groups = json.loads(response.content)["props"]["all_speakers"]
        assert [g["letter"] for g in groups] == ["A", "Z"]
        assert [s["name"] for s in groups[0]["speakers"]] == ["Abel, A", "Amos, A"]

    def test_lookup_returns_matches(self, client):
        self.speakers_with_talks([("Keller, Tim", 1), ("Piper, John", 1)])

        props = inertia_page(client.get("/speaker/", {"q": "piper"}))["props"]

        assert [s["name"] for s in props["results"]] == ["Piper, John"]
        assert props["query"] == "piper"


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


def test_demographic_landing_redirects_to_audiences(client):
    # Audiences now have their own /audience/ area (Phase 5), not folded into Topics.
    response = client.get("/demographic/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/audience/"


def test_topics_page_no_longer_folds_in_audiences(client):
    # Superseded by the dedicated /audience/ area — see tests/test_audiences.py.
    kids = DemographicFactory(name="Kids")
    VideoFactory().demographic.add(kids)

    props = inertia_page(client.get("/topic/"))["props"]

    assert "audiences" not in props


def test_catalogue_stub_is_gone(client):
    assert client.get("/catalogue/").status_code == 404


class TestTopicsIndexDataBlemishes:
    """Phase 6: the legacy taxonomy leaks case-typo category duplicates and
    depth-prefix mojibake into topic names — clean both at the view layer."""

    def test_case_typo_category_variants_merge_into_one_group(self, client):
        # Real blemish: 'Christian Life' (16 topics) vs the typo 'Christian LIfe' (1).
        TopicFactory(name="Prayer", category="Christian Life")
        TopicFactory(name="Suffering", category="Christian LIfe")

        props = inertia_page(client.get("/topic/"))["props"]
        groups = {g["category"]: g for g in props["topic_groups"]}

        assert "Christian LIfe" not in groups
        assert "Christian Life" in groups  # the majority spelling wins
        names = {t["name"] for t in groups["Christian Life"]["topics"]}
        assert names == {"Prayer", "Suffering"}

    def test_whitespace_category_variants_merge(self, client):
        TopicFactory(name="Grace", category="Doctrine")
        TopicFactory(name="Glory", category="Doctrine ")  # trailing space

        props = inertia_page(client.get("/topic/"))["props"]
        categories = [g["category"] for g in props["topic_groups"]]

        assert categories.count("Doctrine") == 1

    def test_depth_prefix_mojibake_stripped_from_topic_names(self, client):
        # MINUS SIGN (U+2212) double-encoded as bytes E2 88 92 → U+00E2 U+0088 U+0092.
        TopicFactory(name="â" * 3 + " The Grace of God", category="Doctrine")

        props = inertia_page(client.get("/topic/"))["props"]
        names = [t["name"] for g in props["topic_groups"] for t in g["topics"]]

        assert "The Grace of God" in names
