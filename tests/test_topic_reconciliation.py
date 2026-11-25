"""Approved legacy-ID topic reconciliation (#311)."""

from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection

from catalogue import search
from catalogue.models import Topic
from catalogue.topic_reconciliation import (
    ReconciliationBlockedError,
    TopicMapping,
    apply_plan,
    build_plan,
    resolve_ingest_topic,
)
from tests.factories import DemographicFactory, SeriesFactory, TopicFactory, VideoFactory

pytestmark = pytest.mark.django_db


def mapping(legacy_id="900", source="Old name", canonical="Canonical", summary="Approved summary"):
    return TopicMapping(legacy_id, source, canonical, "Teaching", summary)


def test_ingest_mapping_does_not_trust_colliding_database_primary_key(monkeypatch):
    wrong = TopicFactory(id="900", name="Unrelated seed topic")
    canonical = TopicFactory(id="42", name="Canonical")
    monkeypatch.setattr("catalogue.topic_reconciliation.TOPIC_MAPPINGS", (mapping(),))

    resolved = resolve_ingest_topic("900", "Old name")

    assert resolved == canonical
    assert resolved != wrong


def test_ingest_rejects_payload_name_that_disagrees_with_mapped_identity(monkeypatch):
    monkeypatch.setattr("catalogue.topic_reconciliation.TOPIC_MAPPINGS", (mapping(),))

    with pytest.raises(ReconciliationBlockedError, match="does not match mapping source"):
        resolve_ingest_topic("900", "Different old name")


def test_unmapped_ingest_collision_allocates_new_id_instead_of_mislinking(monkeypatch):
    wrong = TopicFactory(id="900", name="Unrelated seed topic")
    monkeypatch.setattr("catalogue.topic_reconciliation.TOPIC_MAPPINGS", ())

    resolved = resolve_ingest_topic("900", "A new legacy topic")

    assert resolved.name == "A new legacy topic"
    assert resolved.pk.startswith("R311")
    assert resolved != wrong


def test_plan_blocks_ambiguous_clean_database_identity_before_writes():
    TopicFactory(name="Old name")
    TopicFactory(name="\N{MINUS SIGN} Old name")

    with pytest.raises(ReconciliationBlockedError, match="ambiguous"):
        build_plan((mapping(),))

    assert Topic.objects.count() == 2


def test_missing_source_is_an_idempotent_no_op_when_canonical_exists():
    TopicFactory(name="Canonical")

    assert build_plan((mapping(),)) == []


def test_missing_historical_source_is_covered_by_unambiguous_compatibility_alias():
    workaround = TopicFactory(name="Heaven and Hell and the Spiritual Realm")
    historical = TopicMapping(
        "63",
        "Heaven & Hell",
        "Heaven, Hell, and the Spiritual Realm",
        "Theology - Systematic",
        "Summary",
    )
    alias = TopicMapping(
        None,
        "Heaven and Hell and the Spiritual Realm",
        "Heaven, Hell, and the Spiritual Realm",
        "Theology - Systematic",
        "Summary",
        warning="Approved spelling compatibility alias.",
    )

    plan = build_plan((historical, alias))

    assert plan[0]["sources"] == [workaround]


def test_education_identity_without_database_provenance_is_not_reconciled():
    education = TopicFactory(name="Education", category="Politics, Culture, and Ethics")
    unsafe = TopicMapping("108", "Education", "Discipleship", "Christian Life", "Teaching", False)

    assert build_plan((unsafe,)) == []
    assert Topic.objects.get(pk=education.pk).name == "Education"


def test_ingest_distinguishes_education_legacy_ids():
    discipleship = TopicFactory(name="Discipleship")
    education = TopicFactory(name="Education", category="Politics, Culture, and Ethics")

    assert resolve_ingest_topic("108", "Education") == discipleship
    assert resolve_ingest_topic("169", "Education") == education


def test_apply_moves_all_five_topic_relations_and_retains_target_summary():
    source = TopicFactory(name="Old name")
    target = TopicFactory(name="Canonical", summary="Existing editorial summary")
    video_reverse = VideoFactory()
    series_reverse = SeriesFactory()
    demographic = DemographicFactory()
    video_forward = VideoFactory()
    series_forward = SeriesFactory()
    video_reverse.topic.add(source)
    series_reverse.topic.add(source)
    demographic.topics.add(source)
    source.videos.add(video_forward)
    source.series.add(series_forward)

    changed = apply_plan(build_plan((mapping(),)))

    target.refresh_from_db()
    assert changed == [target]
    assert target.summary == "Existing editorial summary"
    assert target in video_reverse.topic.all()
    assert target in series_reverse.topic.all()
    assert target in demographic.topics.all()
    assert video_forward in target.videos.all()
    assert series_forward in target.series.all()
    assert not Topic.objects.filter(pk=source.pk).exists()


def test_apply_does_not_update_search_from_inside_database_transaction(monkeypatch):
    TopicFactory(name="Old name")
    external_writes = []
    monkeypatch.setattr(
        "catalogue.search.index_object", lambda instance: external_writes.append(("index", instance.pk))
    )
    monkeypatch.setattr("catalogue.search.delete_object", lambda kind, pk: external_writes.append(("delete", pk)))

    apply_plan(build_plan((mapping(),)))

    assert external_writes == []


def test_summary_conflict_is_reported_and_does_not_replace_target():
    TopicFactory(name="First old")
    TopicFactory(name="Second old")
    target = TopicFactory(name="Canonical", summary="Existing editorial summary")
    rows = (mapping(source="First old", summary="First"), mapping("901", "Second old", summary="Second"))

    plan = build_plan(rows)
    apply_plan(plan)

    target.refresh_from_db()
    assert plan[0]["summary_conflict"] == ["First", "Second"]
    assert target.summary == "Existing editorial summary"


def test_command_defaults_to_dry_run_without_search_or_writes(monkeypatch):
    source = TopicFactory(name="Old name")
    monkeypatch.setattr("catalogue.topic_reconciliation.TOPIC_MAPPINGS", (mapping(),))
    reindexed = []
    monkeypatch.setattr("catalogue.search.reindex", lambda **kwargs: reindexed.append(True))
    output = StringIO()

    call_command("reconcile_topics", stdout=output)

    assert Topic.objects.filter(pk=source.pk).exists()
    assert reindexed == []
    assert "Dry run only" in output.getvalue()


def test_apply_commits_database_before_search_refresh(monkeypatch):
    source = TopicFactory(name="Old name")
    monkeypatch.setattr("catalogue.topic_reconciliation.TOPIC_MAPPINGS", (mapping(),))
    search_states = []
    outer_atomic_depth = len(connection.atomic_blocks)
    monkeypatch.setattr(
        "catalogue.search.reindex",
        lambda **kwargs: search_states.append(len(connection.atomic_blocks)) or 1,
    )

    call_command("reconcile_topics", "--apply", stdout=StringIO())

    assert not Topic.objects.filter(pk=source.pk).exists()
    assert search_states == [outer_atomic_depth]


def test_second_apply_is_no_op_and_does_not_reindex(monkeypatch):
    TopicFactory(name="Old name")
    monkeypatch.setattr("catalogue.topic_reconciliation.TOPIC_MAPPINGS", (mapping(),))
    reindexed = []
    monkeypatch.setattr("catalogue.search.reindex", lambda **kwargs: reindexed.append(True) or 1)

    call_command("reconcile_topics", "--apply", stdout=StringIO())
    call_command("reconcile_topics", "--apply", stdout=StringIO())

    assert reindexed == [True]


@pytest.mark.parametrize(
    "failure",
    [search.SearchUnavailableError("down"), *(error("down") for error in search.TYPESENSE_ERRORS)],
)
def test_search_failure_warns_that_database_was_applied(monkeypatch, failure):
    source = TopicFactory(name="Old name")
    monkeypatch.setattr("catalogue.topic_reconciliation.TOPIC_MAPPINGS", (mapping(),))
    monkeypatch.setattr(
        "catalogue.search.reindex",
        lambda **kwargs: (_ for _ in ()).throw(failure),
    )

    error = StringIO()
    call_command("reconcile_topics", "--apply", stdout=StringIO(), stderr=error)

    assert not Topic.objects.filter(pk=source.pk).exists()
    assert "Database reconciliation applied" in error.getvalue()
    assert "Run reindex_search" in error.getvalue()


def test_old_topic_url_redirects_to_existing_canonical(client, monkeypatch):
    TopicFactory(name="Canonical")
    monkeypatch.setattr("catalogue.topic_reconciliation.TOPIC_MAPPINGS", (mapping(),))

    response = client.get("/topic/Old%20name")

    assert response.status_code == 301
    assert response.url == "/topic/Canonical"
