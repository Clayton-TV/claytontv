"""Dedicated audiences area (/audience), decoupled from Topics — the user
disliked reaching Kids/Youth/Adults via the Topics page."""

import pytest

from tests.factories import DemographicFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_audiences_index_lists_populated_demographics(client):
    kids = DemographicFactory(name="Kids", summary="Teaching for children")
    VideoFactory().demographic.add(kids)
    DemographicFactory(name="Empty")  # no videos → excluded

    page = inertia_page(client.get("/audience/"))

    assert page["component"] == "AudiencesIndex"
    tiles = {a["name"]: a for a in page["props"]["audiences"]}
    assert "Kids" in tiles
    assert "Empty" not in tiles
    assert tiles["Kids"]["videosCount"] == 1
    assert tiles["Kids"]["summary"] == "Teaching for children"
    assert tiles["Kids"]["url"] == "/audience/Kids"


def test_demographic_url_points_at_audience():
    assert DemographicFactory(name="Kids").get_absolute_url() == "/audience/Kids"


def test_audience_detail_shows_its_videos(client):
    kids = DemographicFactory(name="Kids")
    wanted = VideoFactory(name="Kids talk")
    wanted.demographic.add(kids)

    page = inertia_page(client.get("/audience/Kids"))

    assert "Kids talk" in [v["name"] for v in page["props"]["videos"]]


def test_topics_index_no_longer_lists_audiences(client):
    DemographicFactory(name="Kids")

    page = inertia_page(client.get("/topic/"))

    assert "audiences" not in page["props"]
