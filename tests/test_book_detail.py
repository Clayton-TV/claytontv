import pytest

from tests.factories import BibleBookFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def luke_with_videos(titles):
    book = BibleBookFactory(name="LUK", order="42", type="GOS")
    for title in titles:
        video = VideoFactory(name=title)
        video.bible_book.add(book)
    return book


def test_book_detail_builds_a_chapter_strip_and_references(client):
    luke_with_videos(
        [
            "Luke 20:9-19 - If I Were God - JPC Service",
            "Luke 5: 1-11 - A Life-Changing Encounter - JPC Sermon",
            "Word Alive '10 - A topical talk",  # no chapter
        ]
    )

    page = inertia_page(client.get("/book/LUK"))

    assert page["component"] == "BookDetail"
    props = page["props"]
    assert props["book"]["name"] == "Luke"
    assert props["book"]["section"] == "Gospel"
    assert props["chapters"] == [5, 20]  # only chapters that have teaching, sorted
    # Chapter-bearing teaching leads, ordered by chapter; topical talk trails
    refs = [v.get("reference") for v in props["videos"]]
    assert refs == ["5:1-11", "20:9-19", None]


def test_chapter_filter_narrows_to_one_chapter(client):
    luke_with_videos(["Luke 20:9-19 - A", "Luke 5: 1-11 - B"])

    props = inertia_page(client.get("/book/LUK", {"chapter": 20}))["props"]

    assert props["selected_chapter"] == 20
    assert [v["reference"] for v in props["videos"]] == ["20:9-19"]


def test_unknown_book_is_handled(client):
    assert inertia_page(client.get("/book/ZZZ"))["props"]["title"].startswith("Bible book not found")
