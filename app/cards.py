"""Card-sized video serialization, shared by page views and the latest feed."""

VIDEO_CARD_FIELDS = (
    "id",
    "name",
    "url",
    "thumbnail",
    "date_recorded",
    "date_created",
    "is_livestream",
    "duration_seconds",
)


def video_card_props(videos):
    """Serialize videos to the fields the card components render.

    Passing full Video objects to Inertia serializes every M2M relation,
    costing ~5 extra queries per video.
    """
    if hasattr(videos, "values"):
        return list(videos.values(*VIDEO_CARD_FIELDS))
    return [{field: getattr(video, field) for field in VIDEO_CARD_FIELDS} for video in videos]
