from django.contrib import admin

# Import all the models from the models package
from .models import (
    Bible_Book,
    Channel,
    Demographic,
    Label,
    Ministry,
    Series,
    Speaker,
    Topic,
    Video,
)


# Video Admin Configuration
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for Video model"""

    list_display = ("name", "id_number", "channel", "series", "date_created", "is_livestream", "display_topic")
    list_filter = ("is_livestream", "date_created", "channel", "series", "labels")
    search_fields = ("name", "id_number", "description")
    ordering = ("-date_created",)
    date_hierarchy = "date_created"

    # Many-to-many fields displayed with filter_horizontal for better UX
    filter_horizontal = ("bible_book", "demographic", "ministry", "speaker", "topic")

    # Read-only fields
    readonly_fields = ("date_modified",)

    # Custom fieldsets for better organization
    fieldsets = (
        ("Basic Information", {"fields": ("id_number", "name", "description", "url")}),
        ("Series Information", {"fields": ("channel", "series", "number_in_series"), "classes": ("collapse",)}),
        (
            "Content Classification",
            {"fields": ("bible_book", "topic", "demographic", "ministry", "speaker"), "classes": ("collapse",)},
        ),
        (
            "Dates & Status",
            {"fields": ("is_livestream", "date_recorded", "date_created", "date_modified"), "classes": ("collapse",)},
        ),
        ("Admin", {"fields": ("labels",), "classes": ("collapse",)}),
    )


# Series Admin Configuration
@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """Admin configuration for Series model"""

    list_display = ("name", "year_start", "year_end", "display_topics", "display_speakers")
    list_filter = ("year_start", "year_end")
    search_fields = ("name", "summary")
    ordering = ("-year_start",)

    filter_horizontal = ("topic", "speaker", "ministry", "videos", "bible_book")

    fieldsets = (
        ("Basic Information", {"fields": ("name", "summary", "year_start", "year_end")}),
        (
            "Related Content",
            {"fields": ("topic", "speaker", "ministry", "bible_book", "videos"), "classes": ("collapse",)},
        ),
    )

    def display_topics(self, obj):
        """Display first few topics"""
        return ", ".join([topic.name for topic in obj.topic.all()[:3]])

    display_topics.short_description = "Topics"

    def display_speakers(self, obj):
        """Display first few speakers"""
        return ", ".join([speaker.name for speaker in obj.speaker.all()[:3]])

    display_speakers.short_description = "Speakers"


# Channel Admin Configuration
@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin configuration for Channel model"""

    list_display = ("name", "type", "trusted", "channel_url")
    list_filter = ("type", "trusted")
    search_fields = ("name", "summary", "channel_url")
    ordering = ("name",)

    filter_horizontal = ("ministry",)

    fieldsets = (
        ("Basic Information", {"fields": ("name", "summary", "type", "channel_url", "trusted")}),
        ("Related Content", {"fields": ("ministry",), "classes": ("collapse",)}),
    )


# Speaker Admin Configuration
@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    """Admin configuration for Speaker model"""

    list_display = ("name", "thumbnail", "video_count", "series_count")
    search_fields = ("name", "bio")
    ordering = ("name",)

    filter_horizontal = ("videos", "series")

    fieldsets = (
        ("Basic Information", {"fields": ("name", "bio", "thumbnail")}),
        ("Related Content", {"fields": ("videos", "series"), "classes": ("collapse",)}),
    )

    def video_count(self, obj):
        """Count of related videos"""
        return obj.videos.count()

    video_count.short_description = "Videos"

    def series_count(self, obj):
        """Count of related series"""
        return obj.series.count()

    series_count.short_description = "Series"


# Topic Admin Configuration
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin configuration for Topic model"""

    list_display = ("name", "category", "video_count", "series_count")
    list_filter = ("category",)
    search_fields = ("name", "summary", "category")
    ordering = ("category", "name")

    filter_horizontal = ("videos", "series")

    fieldsets = (
        ("Basic Information", {"fields": ("name", "category", "summary")}),
        ("Related Content", {"fields": ("videos", "series"), "classes": ("collapse",)}),
    )

    def video_count(self, obj):
        """Count of related videos"""
        return obj.videos.count()

    video_count.short_description = "Videos"

    def series_count(self, obj):
        """Count of related series"""
        return obj.series.count()

    series_count.short_description = "Series"


# Ministry Admin Configuration
@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    """Admin configuration for Ministry model"""

    list_display = ("name", "thumbnail", "video_count", "series_count", "channel_count")
    search_fields = ("name", "summary")
    ordering = ("name",)

    filter_horizontal = ("videos", "series", "channel")

    fieldsets = (
        ("Basic Information", {"fields": ("name", "summary", "thumbnail")}),
        ("Related Content", {"fields": ("videos", "series", "channel"), "classes": ("collapse",)}),
    )

    def video_count(self, obj):
        """Count of related videos"""
        return obj.videos.count()

    video_count.short_description = "Videos"

    def series_count(self, obj):
        """Count of related series"""
        return obj.series.count()

    series_count.short_description = "Series"

    def channel_count(self, obj):
        """Count of related channels"""
        return obj.channel.count()

    channel_count.short_description = "Channels"


# Bible Book Admin Configuration
@admin.register(Bible_Book)
class BibleBookAdmin(admin.ModelAdmin):
    """Admin configuration for Bible_Book model"""

    list_display = ("name", "type", "order", "get_full_name")
    list_filter = ("type",)
    search_fields = ("name",)
    ordering = ("order",)

    fieldsets = (("Basic Information", {"fields": ("order", "name", "type", "summary")}),)

    def get_full_name(self, obj):
        """Get the full name of the Bible book"""
        return dict(obj._meta.get_field("name").choices).get(obj.name, obj.name)

    get_full_name.short_description = "Full Name"


# Demographic Admin Configuration
@admin.register(Demographic)
class DemographicAdmin(admin.ModelAdmin):
    """Admin configuration for Demographic model"""

    list_display = ("name", "thumbnail", "series_count", "topic_count", "video_count")
    search_fields = ("name", "summary")
    ordering = ("name",)

    filter_horizontal = ("series", "topics", "videos")

    fieldsets = (
        ("Basic Information", {"fields": ("name", "summary", "thumbnail")}),
        ("Related Content", {"fields": ("series", "topics", "videos"), "classes": ("collapse",)}),
    )

    def series_count(self, obj):
        """Count of related series"""
        return obj.series.count()

    series_count.short_description = "Series"

    def topic_count(self, obj):
        """Count of related topics"""
        return obj.topics.count()

    topic_count.short_description = "Topics"

    def video_count(self, obj):
        """Count of related videos"""
        return obj.videos.count()

    video_count.short_description = "Videos"


# Label Admin Configuration
@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    """Admin configuration for Label model"""

    list_display = ("label_series", "label_subseries", "label_episode")
    search_fields = ("label_series", "label_subseries", "label_episode")
    ordering = ("label_series",)

    fieldsets = (("Label Information", {"fields": ("label_series", "label_subseries", "label_episode")}),)
