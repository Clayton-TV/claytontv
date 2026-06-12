"""Model factories for the test suite.

Schema gotchas worth knowing when writing tests:

- Topic and Series each declare their own ``videos`` M2M with
  ``related_name="+"`` — a SEPARATE join table from the reverse of
  ``Video.topic`` / ``Video.series`` that the app's views actually query.
  Link videos through the Video side (``video.topic.add(...)``,
  ``VideoFactory(series=...)``) or the views won't see them.
- ``Video.id``, ``Topic.id`` and ``Speaker.id`` are CharField primary keys
  holding stringified legacy integers.
"""

import datetime

import factory
from factory.django import DjangoModelFactory

from catalogue.models import (
    Bible_Book,
    Channel,
    Demographic,
    Ministry,
    Series,
    Speaker,
    Topic,
    Video,
)


class ChannelFactory(DjangoModelFactory):
    class Meta:
        model = Channel

    name = factory.Sequence(lambda n: f"Channel {n}")
    type = "You"
    channel_url = factory.Sequence(lambda n: f"https://www.youtube.com/@channel{n}")
    trusted = True


class SpeakerFactory(DjangoModelFactory):
    class Meta:
        model = Speaker

    id = factory.Sequence(lambda n: str(n + 1))
    name = factory.Sequence(lambda n: f"Speaker {n}")
    bio = "A test speaker."
    thumbnail = "speakers/test.jpg"


class MinistryFactory(DjangoModelFactory):
    class Meta:
        model = Ministry

    name = factory.Sequence(lambda n: f"Ministry {n}")
    thumbnail = "ministries/test.jpg"


class DemographicFactory(DjangoModelFactory):
    class Meta:
        model = Demographic

    name = factory.Sequence(lambda n: f"Demographic {n}")
    summary = "A test demographic."
    thumbnail = "demographics/test.jpg"


class BibleBookFactory(DjangoModelFactory):
    class Meta:
        model = Bible_Book
        django_get_or_create = ("name",)

    order = "1"
    name = "GEN"
    type = "LAW"
    summary = "Genesis"


class TopicFactory(DjangoModelFactory):
    class Meta:
        model = Topic

    id = factory.Sequence(lambda n: str(n + 1))
    name = factory.Sequence(lambda n: f"Topic {n}")
    category = "Teaching"


class SeriesFactory(DjangoModelFactory):
    class Meta:
        model = Series

    name = factory.Sequence(lambda n: f"Series {n}")
    id_number = factory.Sequence(lambda n: f"S{n:05d}")
    year_start = "2024"
    year_end = "2025"


class VideoFactory(DjangoModelFactory):
    class Meta:
        model = Video

    id = factory.Sequence(lambda n: str(n + 1))
    id_number = factory.Sequence(lambda n: f"YT{n:06d}")
    name = factory.Sequence(lambda n: f"Video {n}")
    description = "A test video."
    url = factory.Sequence(lambda n: f"https://www.youtube.com/watch?v=test{n:06d}")
    is_livestream = False
    thumbnail = "https://example.com/thumb.jpg"
    date_recorded = datetime.date(2026, 1, 1)
    date_created = datetime.date(2026, 1, 2)
