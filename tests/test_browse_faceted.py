"""Faceted browse at /browse — combinatorial discovery by speaker, Bible book,
audience, type (talk/service) and length, URL-driven and shareable. Honours the
M2M decoy trap (no Video.series facet) and stays query-bounded."""

import pytest

from tests.factories import (
    BibleBookFactory,
    DemographicFactory,
    SpeakerFactory,
    VideoFactory,
)
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def browse(client, **params):
    return inertia_page(client.get("/browse/", params))


def test_renders_the_faceted_component_with_facet_options(client):
    VideoFactory(is_livestream=False)
    page = browse(client)

    assert page["component"] == "BrowseFaceted"
    facets = page["props"]["facets"]
    assert {"type", "length", "audience", "book", "speaker"} <= set(facets)


def test_filters_by_speaker(client):
    speaker = SpeakerFactory(name="Dominic Steele")
    wanted = VideoFactory(name="By Dominic")
    wanted.speaker.add(speaker)
    VideoFactory(name="By someone else")

    names = [v["name"] for v in browse(client, speaker=speaker.id)["props"]["videos"]]

    assert names == ["By Dominic"]


def test_filters_by_book(client):
    romans = BibleBookFactory(name="ROM", order="52")
    wanted = VideoFactory(name="Romans talk")
    wanted.bible_book.add(romans)
    VideoFactory(name="Unrelated")

    names = [v["name"] for v in browse(client, book="ROM")["props"]["videos"]]

    assert names == ["Romans talk"]


def test_filters_by_audience(client):
    kids = DemographicFactory(name="Kids")
    wanted = VideoFactory(name="Kids talk")
    wanted.demographic.add(kids)
    VideoFactory(name="Adult talk")

    names = [v["name"] for v in browse(client, audience="Kids")["props"]["videos"]]

    assert names == ["Kids talk"]


def test_filters_by_type(client):
    VideoFactory(name="A sermon", is_livestream=False)
    VideoFactory(name="A service", is_livestream=True)

    talks = [v["name"] for v in browse(client, type="talk")["props"]["videos"]]
    streams = [v["name"] for v in browse(client, type="stream")["props"]["videos"]]

    assert talks == ["A sermon"]
    assert streams == ["A service"]


def test_filters_by_length_band(client):
    VideoFactory(name="Short one", duration_seconds=600)  # <15m
    VideoFactory(name="Medium one", duration_seconds=1800)  # 15-40m
    VideoFactory(name="Long one", duration_seconds=3600)  # >40m

    assert [v["name"] for v in browse(client, length="short")["props"]["videos"]] == ["Short one"]
    assert [v["name"] for v in browse(client, length="medium")["props"]["videos"]] == ["Medium one"]
    assert [v["name"] for v in browse(client, length="long")["props"]["videos"]] == ["Long one"]


def test_combines_facets_with_and(client):
    speaker = SpeakerFactory(name="Speaker A")
    kids = DemographicFactory(name="Kids")
    match = VideoFactory(name="Match", is_livestream=False)
    match.speaker.add(speaker)
    match.demographic.add(kids)
    partial = VideoFactory(name="Speaker only")
    partial.speaker.add(speaker)

    names = [v["name"] for v in browse(client, speaker=speaker.id, audience="Kids")["props"]["videos"]]

    assert names == ["Match"]


def test_no_duplicate_rows_when_matching_multiple_values_in_a_facet(client):
    a = SpeakerFactory(name="A")
    b = SpeakerFactory(name="B")
    video = VideoFactory(name="Two speakers")
    video.speaker.add(a, b)

    videos = browse(client, speaker=[a.id, b.id])["props"]["videos"]

    assert [v["name"] for v in videos] == ["Two speakers"]  # once, not twice


def test_active_filters_echoed_for_chips(client):
    speaker = SpeakerFactory(name="Speaker A")
    VideoFactory().speaker.add(speaker)

    active = browse(client, speaker=speaker.id, type="talk")["props"]["active"]

    assert str(speaker.id) in [str(s) for s in active["speaker"]]
    assert active["type"] == "talk"


def test_query_count_is_bounded(client, django_assert_max_num_queries):
    for n in range(30):
        v = VideoFactory(name=f"v{n}", duration_seconds=600)
        v.speaker.add(SpeakerFactory(name=f"sp{n}"))

    # page + count + facet aggregates (audience/book/speaker) + live flag
    with django_assert_max_num_queries(10):
        client.get("/browse/", {"type": "talk", "length": "short"})
