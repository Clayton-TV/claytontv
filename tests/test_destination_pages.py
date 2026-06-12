import json

import pytest

from tests.factories import SeriesFactory, SpeakerFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def below_fold(client, url, props):
    response = client.get(
        url,
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_PARTIAL_COMPONENT="SpeakerDetail",
        HTTP_X_INERTIA_PARTIAL_DATA=props,
    )
    return json.loads(response.content)["props"]


class TestSpeakerDetail:
    def test_renders_name_talk_count_and_talks(self, client):
        speaker = SpeakerFactory(name="Dominic Steele")
        talk = VideoFactory(name="Romans 1")
        talk.speaker.add(speaker)

        page = inertia_page(client.get("/speaker/Dominic%20Steele"))

        assert page["component"] == "SpeakerDetail"
        assert page["props"]["speaker"]["name"] == "Dominic Steele"
        assert page["props"]["speaker"]["talksCount"] == 1
        assert [v["name"] for v in page["props"]["videos"]] == ["Romans 1"]

    def test_series_are_deferred_and_list_what_the_speaker_features_in(self, client):
        speaker = SpeakerFactory(name="Vaughan Roberts")
        series = SeriesFactory(name="John's Gospel")
        talk = VideoFactory()
        talk.speaker.add(speaker)
        series.videos.add(talk)
        other = SeriesFactory(name="Unrelated")
        other.videos.add(VideoFactory())

        first = inertia_page(client.get("/speaker/Vaughan%20Roberts"))
        assert "series" not in first["props"]  # deferred — absent on first load
        # defer() registers it for the <Deferred> component's auto-load
        assert "series" in first.get("deferredProps", {}).get("default", [])

        props = below_fold(client, "/speaker/Vaughan%20Roberts", "series")
        assert [s["name"] for s in props["series"]] == ["John's Gospel"]

    def test_unknown_speaker_is_handled(self, client):
        assert inertia_page(client.get("/speaker/Nobody"))["props"]["title"].startswith("Speaker not found")


class TestSeriesDetailEpisodes:
    def test_episodes_are_numbered_and_ordered_for_a_course(self, client):
        series = SeriesFactory(name="Acts")
        e1 = VideoFactory(name="Acts 1", number_in_series=1)
        e2 = VideoFactory(name="Acts 2", number_in_series=2)
        e3 = VideoFactory(name="Acts 3", number_in_series=3)
        # add out of order; the page must present them in episode order
        for v in (e3, e1, e2):
            series.videos.add(v)

        page = inertia_page(client.get("/series/" + series.id_number))

        assert page["component"] == "SeriesDetail"
        episodes = page["props"]["episodes"]
        assert [(e["number"], e["name"]) for e in episodes] == [(1, "Acts 1"), (2, "Acts 2"), (3, "Acts 3")]
        assert page["props"]["start_url"] == f"/video/{e1.id}"

    def test_episode_global_numbering_survives_pagination(self, client):
        series = SeriesFactory(name="Big series")
        for n in range(55):
            v = VideoFactory(number_in_series=n + 1)
            series.videos.add(v)

        props = inertia_page(client.get(f"/series/{series.id_number}", {"page": 2}))["props"]

        assert props["page_start"] == 50  # row index offset for "episode N" labels
        assert len(props["episodes"]) == 5
        assert props["has_prev_page"] is True
