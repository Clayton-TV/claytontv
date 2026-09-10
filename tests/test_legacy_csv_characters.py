import csv

import pytest

from catalogue.legacy_csv import resolve_topic_names
from catalogue.management.commands.import_topics import Command as ImportTopicsCommand
from catalogue.management.commands.import_videos import Command as ImportVideosCommand
from catalogue.management.commands.link_demographics import Command as LinkDemographicsCommand
from catalogue.management.commands.link_series import Command as LinkSeriesCommand
from catalogue.management.commands.link_videos import Command as LinkVideosCommand
from catalogue.models import Topic, Video
from tests.factories import DemographicFactory, SeriesFactory, SpeakerFactory, TopicFactory, VideoFactory

pytestmark = pytest.mark.django_db


def write_csv(tmp_path, filename, fields, row):
    path = tmp_path / filename
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)
    return path


@pytest.fixture
def comma_topics():
    return [
        TopicFactory(id="101", name="Heaven, Hell, and the Spiritual Realm"),
        TopicFactory(id="102", name="Discipleship"),
    ]


def test_video_topic_linker_keeps_comma_bearing_topic_name(comma_topics, tmp_path):
    video = VideoFactory(id="100")
    path = write_csv(
        tmp_path,
        "Videos.csv",
        ["ID", "Name", "Topic", "Speaker/Artist", "Bible Book"],
        {
            "ID": video.id,
            "Name": video.name,
            "Topic": "Heaven, Hell, and the Spiritual Realm;Discipleship",
            "Speaker/Artist": "",
            "Bible Book": "",
        },
    )

    LinkVideosCommand().link_videos(path, debug=False)

    assert list(video.topic.values_list("name", flat=True)) == [
        "Discipleship",
        "Heaven, Hell, and the Spiritual Realm",
    ]


def test_series_topic_linker_keeps_comma_bearing_topic_name(comma_topics, tmp_path):
    series = SeriesFactory(id_number="SERIES-100")
    path = write_csv(
        tmp_path,
        "Series.csv",
        ["ID", "topic_name", "speaker_id", "video_id", "bbook_names"],
        {
            "ID": series.id_number,
            "topic_name": "Heaven, Hell, and the Spiritual Realm",
            "speaker_id": "",
            "video_id": "",
            "bbook_names": "",
        },
    )

    LinkSeriesCommand().link_series(path, debug=False)

    assert list(series.topic.values_list("name", flat=True)) == ["Heaven, Hell, and the Spiritual Realm"]


def test_demographic_topic_linker_keeps_comma_bearing_topic_name(comma_topics, tmp_path):
    demographic = DemographicFactory(name="Adults")
    path = write_csv(
        tmp_path,
        "Demographics.csv",
        ["Name", "Topics", "Series", "Videos"],
        {"Name": demographic.name, "Topics": "Heaven, Hell, and the Spiritual Realm", "Series": "", "Videos": ""},
    )

    LinkDemographicsCommand().link_demographics(path, debug=False)

    assert list(demographic.topics.values_list("name", flat=True)) == ["Heaven, Hell, and the Spiritual Realm"]


def test_ambiguous_topic_value_does_not_clear_existing_links(tmp_path):
    existing = TopicFactory(id="201", name="Existing")
    TopicFactory(id="202", name="A")
    TopicFactory(id="203", name="B")
    TopicFactory(id="204", name="A, B")
    speaker = SpeakerFactory(name="Jane Doe")
    video = VideoFactory(id="200")
    video.topic.add(existing)
    path = write_csv(
        tmp_path,
        "Videos.csv",
        ["ID", "Name", "Topic", "Speaker/Artist", "Bible Book"],
        {
            "ID": video.id,
            "Name": video.name,
            "Topic": "A, B",
            "Speaker/Artist": "Jane Doe",
            "Bible Book": "",
        },
    )

    LinkVideosCommand().link_videos(path, debug=False)

    assert list(video.topic.values_list("name", flat=True)) == ["Existing"]
    assert list(video.speaker.values_list("id", flat=True)) == [speaker.id]


def test_topic_resolver_accepts_a_known_name_containing_a_semicolon():
    assert resolve_topic_names("Theory; Practice", {"Theory; Practice"}) == ["Theory; Practice"]


def test_legacy_csv_imports_utf8_bom_and_special_characters(tmp_path):
    topic_path = write_csv(
        tmp_path,
        "Topics.csv",
        ["id", "name", "category", "summary"],
        {
            "id": "301",
            "name": "L'Église, São Paulo",
            "category": "Culture",
            "summary": 'Quoted "summary", with a newline\nand apostrophe\'s.',
        },
    )
    video_path = write_csv(
        tmp_path,
        "Videos.csv",
        ["ID", "ID Number", "Name", "Description", "URL", "Thumbnail", "DateRecorded", "DateCreated", "IsLivestream"],
        {
            "ID": "302",
            "ID Number": "YT302",
            "Name": "L'Église, São Paulo",
            "Description": 'Quoted "description", with a newline\nand apostrophe\'s.',
            "URL": "https://example.com/302",
            "Thumbnail": "https://example.com/302.jpg",
            "DateRecorded": "2026-01-02",
            "DateCreated": "2026-01-02",
            "IsLivestream": "0",
        },
    )

    ImportTopicsCommand().imp_topics(topic_path, debug=False)
    ImportVideosCommand().imp_videos(video_path, debug=False)

    assert Topic.objects.get(id="301").name == "L'Église, São Paulo"
    assert Topic.objects.get(id="301").summary == 'Quoted "summary", with a newline\nand apostrophe\'s.'
    assert Video.objects.get(id="302").name == "L'Église, São Paulo"
    assert Video.objects.get(id="302").description == 'Quoted "description", with a newline\nand apostrophe\'s.'
