"""Explicit legacy-topic reconciliation used by ingest and the one-off command."""

import csv
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from django.db import transaction
from django.db.models.signals import post_delete, post_save

from catalogue.ingest.normalize import clean_topic_name
from catalogue.models import Demographic, Series, Topic, Video


@dataclass(frozen=True)
class TopicMapping:
    legacy_id: str | None
    source_name: str
    canonical_name: str
    category: str
    summary: str
    reconcile_existing: bool = True
    warning: str = ""


def _load_mappings():
    path = Path(__file__).with_name("data") / "topic_reconciliation.csv"
    with path.open(newline="") as source:
        rows = []
        for row in csv.DictReader(source):
            row["legacy_id"] = row["legacy_id"] or None
            row["reconcile_existing"] = row["reconcile_existing"] == "True"
            rows.append(TopicMapping(**row))
    return tuple(rows)


# Explicit legacy IDs generated from the editor-approved topics-mergers sheet
# and data/legacy_rescue/lookups/topics.csv. Destination seed IDs are omitted:
# runtime primary keys are not legacy identities and demonstrably collide.
TOPIC_MAPPINGS = _load_mappings()


RELATIONS = (
    (Video.topic.through, "video_id"),
    (Series.topic.through, "series_id"),
    (Demographic.topics.through, "demographic_id"),
    (Topic.videos.through, "video_id"),
    (Topic.series.through, "series_id"),
)


class ReconciliationBlockedError(Exception):
    """The database cannot be matched to the source mapping unambiguously."""


def mapping_for_legacy_id(legacy_id):
    return next((row for row in TOPIC_MAPPINGS if row.legacy_id == str(legacy_id)), None)


def _topics_by_clean_name(name):
    wanted = clean_topic_name(name)
    return [topic for topic in Topic.objects.all() if clean_topic_name(topic.name) == wanted]


def resolve_ingest_topic(legacy_id, source_name):
    """Resolve a dump label without trusting a colliding database primary key."""
    source_name = clean_topic_name(source_name)
    mapping = mapping_for_legacy_id(legacy_id)
    if mapping is not None and clean_topic_name(mapping.source_name) != source_name:
        raise ReconciliationBlockedError(
            f"legacy {legacy_id}: payload name {source_name!r} does not match mapping source {mapping.source_name!r}"
        )
    wanted_name = mapping.canonical_name if mapping else source_name

    existing = Topic.objects.filter(name=wanted_name).first()
    if existing is not None:
        return existing

    legacy_pk = Topic.objects.filter(pk=str(legacy_id)).first()
    if mapping is None and legacy_pk is not None and clean_topic_name(legacy_pk.name) == source_name:
        return legacy_pk

    return Topic.objects.create(
        id=_next_topic_id(),
        name=wanted_name,
        category=mapping.category if mapping else "",
        summary=mapping.summary if mapping else "",
    )


def _next_topic_id():
    for sequence in range(1, 10_000_000):
        candidate = f"R311{sequence:06d}"
        if not Topic.objects.filter(pk=candidate).exists():
            return candidate
    raise ReconciliationBlockedError("No collision-free reconciliation topic ID remains.")


def _mapping_sources(row):
    sources = (
        list(Topic.objects.filter(name=row.source_name))
        if row.legacy_id is None
        else _topics_by_clean_name(row.source_name)
    )
    if len(sources) > 1:
        identities = ", ".join(f"{topic.pk}:{topic.name!r}" for topic in sources)
        raise ReconciliationBlockedError(f"legacy {row.legacy_id}: source topic is ambiguous ({identities})")
    return sources


def _resolve_missing(groups, missing, blockers):
    for row, message in missing:
        if row.canonical_name in groups:
            continue
        target = Topic.objects.filter(name=row.canonical_name).first()
        if target is not None:
            groups.setdefault(row.canonical_name, []).append((row, target))
        else:
            blockers.append(message)


def build_plan(mappings=None):
    if mappings is None:
        mappings = TOPIC_MAPPINGS
    groups = {}
    blockers = []
    missing = []
    for row in mappings:
        if not row.reconcile_existing:
            continue
        try:
            sources = _mapping_sources(row)
        except ReconciliationBlockedError as exc:
            blockers.append(str(exc))
            continue
        if not sources:
            identity = f"legacy {row.legacy_id}" if row.legacy_id else "name-only alias"
            missing.append((row, f"{identity}: source topic {row.source_name!r} not found"))
            continue
        groups.setdefault(row.canonical_name, []).append((row, sources[0]))

    _resolve_missing(groups, missing, blockers)

    if blockers:
        raise ReconciliationBlockedError("\n".join(blockers))

    plan = []
    for canonical_name, rows in groups.items():
        targets = list(Topic.objects.filter(name=canonical_name))
        if len(targets) > 1:
            raise ReconciliationBlockedError(f"canonical topic {canonical_name!r} is ambiguous")
        target = targets[0] if targets else None
        summaries = {row.summary for row, _ in rows if row.summary}
        categories = {row.category for row, _ in rows if row.category}
        sources = list(dict.fromkeys(source for _, source in rows))
        category = next(iter(categories)) if len(categories) == 1 else ""
        category_update = bool(target and category and target.category != category)
        relation_merge = target is None or any(source.pk != target.pk for source in sources)
        if not relation_merge and not category_update:
            continue
        plan.append(
            {
                "canonical_name": canonical_name,
                "target": target,
                "sources": sources,
                "summary": next(iter(summaries)) if len(summaries) == 1 else "",
                "category": category,
                "category_update": category_update,
                "summary_conflict": sorted(summaries) if len(summaries) > 1 else [],
                "category_conflict": sorted(categories) if len(categories) > 1 else [],
                "warnings": sorted({row.warning for row, _ in rows if row.warning}),
            }
        )
    return plan


def describe_plan(plan):
    lines = []
    for item in plan:
        target = item["target"]
        action = "merge into" if target else "create"
        if target and not any(source.pk != target.pk for source in item["sources"]):
            action = "update"
        sources = ", ".join(f"{source.pk}:{source.name}" for source in item["sources"])
        lines.append(f"{action} {item['canonical_name']!r} from [{sources}]")
        if item["summary_conflict"]:
            lines.append(
                f"  summary conflict: retain existing target value ({len(item['summary_conflict'])} source values)"
            )
        if item["category_conflict"]:
            lines.append(
                f"  category conflict: retain existing target value ({len(item['category_conflict'])} source values)"
            )
        for warning in item["warnings"]:
            lines.append(f"  warning: {warning}")
    return lines


def _move_relations(source, target):
    for through, related_field in RELATIONS:
        topic_field = "topic_id"
        related_ids = through.objects.filter(**{topic_field: source.pk}).values_list(related_field, flat=True)
        through.objects.bulk_create(
            [through(**{topic_field: target.pk, related_field: related_id}) for related_id in related_ids],
            ignore_conflicts=True,
        )


@contextmanager
def _suspend_topic_search_signals():
    """Prevent external index writes while the database transaction is open."""
    from catalogue import search_signals

    save_uid = f"typesense_index_{Topic.__name__}"
    delete_uid = f"typesense_deindex_{Topic.__name__}"
    post_save.disconnect(sender=Topic, dispatch_uid=save_uid)
    post_delete.disconnect(sender=Topic, dispatch_uid=delete_uid)
    try:
        yield
    finally:
        post_save.connect(search_signals._on_save, sender=Topic, dispatch_uid=save_uid)
        post_delete.connect(search_signals._on_delete, sender=Topic, dispatch_uid=delete_uid)


@transaction.atomic
def apply_plan(plan):
    changed = []
    with _suspend_topic_search_signals():
        for item in plan:
            target = item["target"]
            if target is None:
                target = Topic.objects.create(
                    id=_next_topic_id(),
                    name=item["canonical_name"],
                    summary=item["summary"],
                    category=item["category"],
                )
            elif item["category_update"]:
                target.category = item["category"]
                target.save(update_fields=["category"])
            for source in item["sources"]:
                if source.pk == target.pk:
                    continue
                _move_relations(source, target)
                source.delete()
            changed.append(target)
    return changed


def canonical_name_for_alias(name):
    canonical = {
        row.canonical_name
        for row in TOPIC_MAPPINGS
        if clean_topic_name(row.source_name) == clean_topic_name(name) and row.canonical_name != name
    }
    return next(iter(canonical)) if len(canonical) == 1 else None
