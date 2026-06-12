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


def ingest_series_trees(trees):
    stats = {"series_created": 0, "series_updated": 0, "memberships": 0, "live_flagged": 0, "live_demoted": 0}

    numbered = set()  # videos already given number_in_series by an earlier node
    mentioned_ids = set()
    live_ids = set()

    for node, path in all_nodes(trees):
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
    return stats
