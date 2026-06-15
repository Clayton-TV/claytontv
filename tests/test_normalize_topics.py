"""normalize_topics command (#288): clean topic names + deterministic merge."""

import pytest
from django.core.management import call_command

from catalogue.models.topic import Topic
from tests.factories import TopicFactory, VideoFactory

pytestmark = pytest.mark.django_db

# Real legacy prefix: U+2212 MINUS (UTF-8 E2 88 92) misdecoded as Latin-1
# -> U+00E2 U+0088 U+0092, three deep.
MOJIBAKE = "\u00e2\u0088\u0092" * 3 + " The Grace of God"


def test_merges_mojibake_duplicate_into_clean_topic():
    clean = TopicFactory(name="The Grace of God")
    dirty = TopicFactory(name=MOJIBAKE)
    v1 = VideoFactory()
    v2 = VideoFactory()
    v1.topic.add(clean)
    v2.topic.add(dirty)

    call_command("normalize_topics")

    remaining = Topic.objects.filter(name="The Grace of God")
    assert remaining.count() == 1
    assert not Topic.objects.filter(name=MOJIBAKE).exists()
    # the duplicate's video was re-pointed to the surviving topic
    assert set(remaining.first().video_set.values_list("id", flat=True)) == {v1.id, v2.id}


def test_renames_a_lone_dirty_topic_without_merging():
    TopicFactory(name=MOJIBAKE)
    call_command("normalize_topics")
    assert Topic.objects.filter(name="The Grace of God").exists()
    assert not Topic.objects.filter(name=MOJIBAKE).exists()


def test_keeps_canonical_with_more_videos():
    big = TopicFactory(name="The Grace of God")
    small = TopicFactory(name=MOJIBAKE)
    for _ in range(3):
        VideoFactory().topic.add(big)
    VideoFactory().topic.add(small)

    call_command("normalize_topics")
    survivor = Topic.objects.get(name="The Grace of God")
    assert survivor.id == big.id  # kept the higher-video-count row
    assert survivor.video_set.count() == 4


def test_dry_run_changes_nothing():
    TopicFactory(name=MOJIBAKE)
    call_command("normalize_topics", "--dry-run")
    assert Topic.objects.filter(name=MOJIBAKE).exists()


def test_idempotent():
    TopicFactory(name="The Grace of God")
    TopicFactory(name=MOJIBAKE)
    call_command("normalize_topics")
    call_command("normalize_topics")  # second run is a no-op, must not error
    assert Topic.objects.filter(name="The Grace of God").count() == 1


def test_case_only_duplicates_are_left_alone():
    # Differs by case, not whitespace/prefix → human judgment (Slice 6), not us.
    TopicFactory(name="Christian Life")
    TopicFactory(name="Christian LIfe")
    call_command("normalize_topics")
    assert Topic.objects.filter(name="Christian Life").exists()
    assert Topic.objects.filter(name="Christian LIfe").exists()
