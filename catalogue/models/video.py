from typing import ClassVar  # Add typing imports

from django.db import models  # import the model class that all models are based on
from django.db.models import Count, Q
from django.urls import reverse  # generate urls by reversing url pattern

# from .series import Series
# from .speaker import Speaker
from .bible_book import Bible_Book  # Changed from BibleBook to Bible_Book

# from .ministry import Ministry
# from .demograpic import Demographic
from .label import Label

# Now import the models that we need to link to:
# from .channel import Channel

# Publication state. Legacy + Studio-published content is "published" (visible on
# the public site); Studio creates content as "draft" until a human publishes.
DRAFT = "draft"
PUBLISHED = "published"


def published_count(relation="video"):
    """A ``Count`` annotation over only *published* videos, reached via the given
    reverse relation name ("video" for most models, "videos" for the Series M2M).
    Use instead of ``Count(relation)`` on public category counts so draft-only
    categories don't show or inflate their tallies."""
    return Count(relation, filter=Q(**{f"{relation}__status": PUBLISHED}))


class VideoQuerySet(models.QuerySet):
    def published(self):
        """Public videos only. The canonical source for every public surface."""
        return self.filter(status=PUBLISHED)

    def alive(self):
        """Not soft-deleted."""
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        """Soft-deleted (trashed) only."""
        return self.exclude(deleted_at__isnull=True)


class AliveVideoManager(models.Manager.from_queryset(VideoQuerySet)):
    """Default manager — excludes soft-deleted rows everywhere (Laravel-style
    global scope): public surfaces, the Studio Library, reverse relations
    (``series.videos``, ``speaker.video_set`` …) and the search reconcile all
    skip trashed rows automatically. Reach trashed rows via ``Video.all_objects``
    (restore / admin). Keeps all the ``VideoQuerySet`` methods (``.published()``…)."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


# Now the actual class definition for the model (database table):
class Video(models.Model):
    """Model representing the database table for videos,
    where each table entry is an individual video"""

    id = models.CharField(
        max_length=10, unique=True, help_text="Another unique identifier used for database linking", primary_key=True
    )
    id_number = models.CharField(
        max_length=100,
        unique=True,
        help_text="A unique video identifier generated e.g.YT1234",
    )

    bible_book = models.ManyToManyField(Bible_Book, blank=True, help_text="The bible books covered in the video.")
    demographic = models.ManyToManyField("Demographic", blank=True, help_text="The video's demographic.")
    description = models.TextField(max_length=5000, help_text="Enter a brief description of the video <5000 chars.")
    url = models.URLField(unique=True, help_text="A link to where the video is hosted.")
    ministry = models.ManyToManyField("Ministry", blank=True, help_text="The ministries associated with the video.")
    number_in_series = models.IntegerField(
        help_text="If part of a series provide the number in the series.",
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=200, help_text="The title of the video."
    )  # check max title length on popular upload sites ->>> Youtube 100 characters, Vimeo 128.
    speaker = models.ManyToManyField("Speaker", blank=True, help_text="The speakers/artist in the video.")
    is_livestream = models.BooleanField(default=False, help_text="Whether the video was a live stream.")
    topic = models.ManyToManyField("Topic", help_text="Select topics for this video.")

    # Publication state. Defaults to "published" so the existing catalogue stays
    # live after the migration; Studio-created videos start as "draft".
    status = models.CharField(
        max_length=12,
        choices=[(DRAFT, "Draft"), (PUBLISHED, "Published")],
        default=PUBLISHED,
        db_index=True,
        help_text="Draft videos are hidden from the public site until published.",
    )

    # Soft delete (Laravel-style). A timestamp instead of a hard DELETE so the
    # Studio's Reject / delete is recoverable; the default manager hides these.
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When set, the video is soft-deleted: hidden everywhere but retained for restore.",
    )

    thumbnail = models.TextField(max_length=200, help_text="Thumbnail Location", null=True)

    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Runtime in whole seconds, harvested from the hosting platform (YouTube/Vimeo).",
    )

    alternate_urls = models.JSONField(
        default=list,
        blank=True,
        help_text="Other places this video is hosted: [{'url': ..., 'platform': 'youtube'|'vimeo'|'other'}]. "
        "The legacy catalogue holds both a Vimeo and a YouTube copy for most programmes; "
        "`url` is the primary, these are the rest.",
    )

    date_recorded = models.DateField(null=True, blank=True, help_text="The date the video was recorded.")
    date_created = models.DateField(help_text="The date a video is uploaded.")
    date_modified = models.DateField(null=True, blank=True, help_text=" The last time the video data was edited.")

    labels = models.ForeignKey(
        Label,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        help_text="Labels for internal admin use.",
    )
    channel = models.ForeignKey(
        "Channel",
        on_delete=models.RESTRICT,
        null=True,
        help_text="The channel for the video.",
    )
    series = models.ForeignKey(
        "Series",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        help_text="The series the video is part of.",
    )

    # Default manager hides soft-deleted rows; all_objects sees everything.
    objects = AliveVideoManager()
    all_objects = VideoQuerySet.as_manager()

    class Meta:
        ordering: ClassVar[list[str]] = ["date_created"]

    def __str__(self):
        """String for representing model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the video"""
        return reverse("video", args=[str(self.id)])

    def display_topic(self):
        """Create a string for the topics. This is required to display topics in Admin."""
        return ", ".join(topic.name for topic in self.topic.all()[:3])

    display_topic.short_description = "Topics"
