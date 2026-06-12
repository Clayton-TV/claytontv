"""Idempotent ingestion of the legacy series hierarchy (series.json).

The dump is 79 top-level browse trees ("LIVE STREAMS", "BROWSE: WEEKLY
SERMONS", ...) containing 2,287 series nodes (verified globally-unique ids)
with programmes attached per node. This module owns:

- Series upserts keyed on id_number (= legacy node id). Node names are clean
  here — the comma-concatenated monsters in old data were manufactured by the
  previous pipeline's path-joining.
- Series→video memberships (Series.videos) in dump order, which also yields
  Video.number_in_series (from the first tree-order node containing the video).
- The authoritative is_livestream signal: membership under tree 1993
  ("LIVE STREAMS"). Videos the dump doesn't mention (post-dump content from
  the live admin) keep whatever flag they have.
"""

from catalogue.models import Series, Video

from .normalize import clean_name

LIVE_STREAMS_TREE_ID = 1993


def walk(node, path=()):
    yield node, path
    for sub in node.get("subSeries") or []:
        yield from walk(sub, (*path, node["id"]))


def all_nodes(trees):
    for tree in trees:
        yield from walk(tree)


def canonical_id(id_numbers):
    """Pick the survivor among duplicate series: the lowest legacy id (oldest,
    most stable). Numeric where possible, else lexical."""

    def key(value):
        return (0, int(value)) if str(value).isdigit() else (1, str(value))

    return min(id_numbers, key=key)


def deduplicate_series(node_ids, stats):
    """Make the series set authoritative and free of legacy-taxonomy noise:

    1. Drop orphans — series not present in the hierarchy at all (stale
       CSV-pipeline rows, often with comma-mangled names).
    2. Collapse same-name twins that carry the IDENTICAL video set — the legacy
       site listed one series under several browse trees, creating real
       duplicate rows. Distinct-content same-name series (e.g. several
       "One-offs") are kept.

    Safe: Series.videos is M2M (delete only unlinks), and no Channel FK points
    at series (verified). Survivor is the lowest legacy id, so the choice is
    stable across re-runs.
    """
    from collections import defaultdict

    from django.db.models import Count

    orphans = Series.objects.exclude(id_number__in=node_ids)
    stats["orphans_removed"] = orphans.count()
    orphans.delete()

    by_name = defaultdict(list)
    for series in Series.objects.annotate(n=Count("videos")).filter(n__gt=0):
        by_name[series.name].append(series)

    removable = []
    for rows in by_name.values():
        if len(rows) < 2:
            continue
        by_content = defaultdict(list)
        for series in rows:
            by_content[frozenset(series.videos.values_list("id", flat=True))].append(series.id_number)
        for id_numbers in by_content.values():
            if len(id_numbers) > 1:
                keep = canonical_id(id_numbers)
                removable += [i for i in id_numbers if i != keep]

    stats["duplicates_merged"] = len(removable)
    Series.objects.filter(id_number__in=removable).delete()


def ingest_series_trees(trees):
    stats = {
        "series_created": 0,
        "series_updated": 0,
        "memberships": 0,
        "live_flagged": 0,
        "live_demoted": 0,
        "orphans_removed": 0,
        "duplicates_merged": 0,
    }

    numbered = set()  # videos already given number_in_series by an earlier node
    mentioned_ids = set()
    live_ids = set()
    node_ids = set()

    for node, path in all_nodes(trees):
        node_ids.add(str(node["id"]))
        programme_ids = [str(p["id"]) for p in node.get("programmes") or []]
        mentioned_ids.update(programme_ids)
        if LIVE_STREAMS_TREE_ID in path or node["id"] == LIVE_STREAMS_TREE_ID:
            live_ids.update(programme_ids)

        if not path:  # the 79 browse roots are taxonomy, not series
            continue

        series, created = Series.objects.update_or_create(
            id_number=str(node["id"]),
            # Year fields are intentionally untouched: this dump carries no
            # year data, and the existing values (however dirty) are all we have.
            defaults={"name": clean_name(node["name"])},
        )
        stats["series_created" if created else "series_updated"] += 1

        videos = {v.id: v for v in Video.objects.filter(id__in=programme_ids)}
        ordered = [videos[pid] for pid in programme_ids if pid in videos]
        series.videos.set(ordered)
        stats["memberships"] += len(ordered)

        for position, video in enumerate(ordered, start=1):
            if video.id not in numbered and video.number_in_series != position:
                Video.objects.filter(id=video.id).update(number_in_series=position)
            numbered.add(video.id)

    stats["live_flagged"] = Video.objects.filter(id__in=live_ids, is_livestream=False).update(is_livestream=True)
    stats["live_demoted"] = Video.objects.filter(is_livestream=True, id__in=mentioned_ids - live_ids).update(
        is_livestream=False
    )

    deduplicate_series(node_ids, stats)
    return stats
