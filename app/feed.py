"""The Latest feed: a feed with a spine, not a wall of cards.

Videos are grouped into editorial time buckets ("This week", "Last week",
"Earlier in June", "October 2024") because people think "two Sundays ago",
never "page 3". A series that floods a bucket (FLOOD_THRESHOLD+ episodes,
which livestream-heavy series do constantly) collapses into a single series
row at the position of its newest episode. Spec: docs/DESIGN_SPEC.md § Latest.
"""

import datetime
from collections import Counter
from itertools import groupby

from django.core.paginator import Paginator
from django.db.models import F

from app.cards import video_card_props
from catalogue.models.series import Series
from catalogue.models.video import Video

PER_PAGE = 24
FLOOD_THRESHOLD = 3


def latest_feed(page_num, today=None):
    today = today or datetime.date.today()
    talks = (
        Video.objects.published()
        .filter(is_livestream=False)
        .order_by(
            # Explicit nulls_last: Postgres defaults DESC to nulls FIRST, SQLite
            # to nulls last — without this the two environments disagree.
            F("date_recorded").desc(nulls_last=True),
            "-id",
        )
    )
    paginator = Paginator(talks, PER_PAGE)
    page = paginator.get_page(page_num)
    videos = list(page.object_list)

    groups = [
        {"label": label, "items": _collapse_floods(list(bucket))}
        for label, bucket in groupby(videos, key=lambda v: _bucket_label(_display_date(v), today))
    ]

    return {
        "groups": groups,
        "page": page.number,
        "num_pages": paginator.num_pages,
        "has_prev_page": page.has_previous(),
        "has_next_page": page.has_next(),
    }


def _display_date(video):
    # Mirrors the card components: recorded date, else the upload date
    return video.date_recorded or video.date_created


def _bucket_label(date, today):
    if date is None:
        return "Undated"
    monday = today - datetime.timedelta(days=today.weekday())
    if date >= monday:
        return "This week"
    if date >= monday - datetime.timedelta(days=7):
        return "Last week"
    if (date.year, date.month) == (today.year, today.month):
        return f"Earlier in {date.strftime('%B')}"
    return date.strftime("%B %Y")


def _collapse_floods(videos):
    """Collapse series with FLOOD_THRESHOLD+ episodes in this bucket into one
    series row each; everything else stays an individual video card."""
    links = Series.videos.through.objects.filter(video_id__in=[v.id for v in videos]).values_list(
        "series_id", "video_id"
    )
    members = {}  # series_id -> set of video ids in this bucket
    for series_id, video_id in links:
        members.setdefault(series_id, set()).add(video_id)

    assigned = _assign_videos_to_floods(members)

    kept_series = {s for s in assigned.values() if s is not None}
    series_by_id = {s.pk: s for s in Series.objects.filter(pk__in=kept_series)} if kept_series else {}

    items, emitted = [], set()
    for video in videos:
        series_id = assigned.get(video.id)
        if series_id is None:
            items.append({"type": "video", **video_card_props([video])[0]})
        elif series_id not in emitted:
            emitted.add(series_id)
            flood = [v for v in videos if assigned.get(v.id) == series_id]
            series = series_by_id[series_id]
            items.append(
                {
                    "type": "series",
                    "id": series.pk,
                    "name": series.name,
                    "url": series.get_absolute_url(),
                    "count": len(flood),
                    "latest_date": _display_date(flood[0]),
                    "thumbnails": [v.thumbnail for v in flood if v.thumbnail][:3],
                }
            )
    return items


def _assign_videos_to_floods(members):
    """Each video belongs to at most one series row: the flooding series with
    the most episodes here (ties broken by id for determinism). Assigning a
    shared video away can drop another series below the threshold, so dissolve
    and repeat until stable."""
    while True:
        flooding = {s: vids for s, vids in members.items() if len(vids) >= FLOOD_THRESHOLD}
        assigned = {
            video_id: max(
                (s for s, vids in flooding.items() if video_id in vids),
                key=lambda s: (len(flooding[s]), -_sort_rank(s)),
            )
            for video_id in {v for vids in flooding.values() for v in vids}
        }
        counts = Counter(assigned.values())
        dissolved = [s for s in flooding if counts[s] < FLOOD_THRESHOLD]
        if not dissolved:
            return assigned
        for series_id in dissolved:
            del members[series_id]


def _sort_rank(series_id):
    # Series pks are stringified legacy integers; rank numerically when possible
    try:
        return int(series_id)
    except (TypeError, ValueError):
        return 0
