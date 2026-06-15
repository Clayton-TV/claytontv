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


# Scalar fields the Studio editor edits directly on the Video row.
VIDEO_EDIT_FIELDS = (
    "id",
    "name",
    "description",
    "url",
    "thumbnail",
    "duration_seconds",
    "is_livestream",
    "number_in_series",
    "status",
)


def video_edit_props(video):
    """Full editable view of one Video, as a plain dict for the Studio editor.

    Includes the scalar fields plus every relation the editor manages: the five
    M2M id-lists, the current series (via the ``Series.videos`` M2M — NOT the
    decoy ``Video.series`` FK), the ``alternate_urls`` JSON, and the
    ``related_resources`` rows. The caller should ``prefetch_related`` the M2Ms
    and ``related_resources`` to keep this off the N+1 path.
    """
    from catalogue.models.series import Series

    series_id = Series.objects.filter(videos=video).values_list("pk", flat=True).first()
    return {
        **{field: getattr(video, field) for field in VIDEO_EDIT_FIELDS},
        "date_recorded": video.date_recorded.isoformat() if video.date_recorded else None,
        "alternate_urls": video.alternate_urls or [],
        "speaker_ids": [str(s.pk) for s in video.speaker.all()],
        "topic_ids": [str(t.pk) for t in video.topic.all()],
        "bible_book_ids": [str(b.pk) for b in video.bible_book.all()],
        "demographic_ids": [str(d.pk) for d in video.demographic.all()],
        "ministry_ids": [str(m.pk) for m in video.ministry.all()],
        "series_id": str(series_id) if series_id is not None else None,
        "related_resources": [{"kind": r.kind, "url": r.url} for r in video.related_resources.order_by("kind")],
        "enrichment": enrichment_props(video),
    }


def enrichment_props(video):
    """The stored AI suggestions for a video as a plain dict, or ``None`` when
    there's no enrichment. Drives the editor's Suggestions panel (Epic #201, E3)
    — display + per-field apply; never auto-applied to human fields."""
    enrichment = getattr(video, "enrichment", None)
    if enrichment is None:
        return None
    return {
        "summary": enrichment.summary or "",
        "topics": enrichment.topics or [],
        "audience": enrichment.audience or "",
        "bible_passages": enrichment.bible_passages or [],
        "keywords": enrichment.keywords or [],
        "generated_at": enrichment.generated_at.isoformat() if enrichment.generated_at else None,
    }
