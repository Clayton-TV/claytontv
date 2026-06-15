"""Enrichment store + invisible search feed (Epic #201, E1).

`store_enrichment` upserts a VideoEnrichment row from the model's suggestions;
the stored values fold invisibly into the video's search `text` (recall boost)
and a save re-indexes the parent video. The Ollama call is always mocked.
"""

import pytest

from catalogue import search
from catalogue.enrichment import PROMPT_VERSION, store_enrichment
from catalogue.models.enrichment import VideoEnrichment
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db


def _suggestions(**overrides):
    base = {
        "summary": "A sermon on grace.",
        "suggested_topics": ["Grace", "Salvation"],
        "suggested_audience": "Adults",
        "bible_passages": [{"book": "Romans", "label": "Romans 8"}],
        "keywords": ["grace", "adoption", "spirit"],
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- #
# store_enrichment — upsert + provenance
# --------------------------------------------------------------------------- #


def test_store_enrichment_creates_a_row(monkeypatch):
    video = VideoFactory(name="Romans 8")
    monkeypatch.setattr("catalogue.enrichment.enrich_video", lambda *a, **k: _suggestions())

    enrichment = store_enrichment(video)

    assert enrichment is not None
    assert enrichment.video_id == video.pk
    assert enrichment.summary == "A sermon on grace."
    assert enrichment.topics == ["Grace", "Salvation"]
    assert enrichment.audience == "Adults"
    assert enrichment.keywords == ["grace", "adoption", "spirit"]
    assert enrichment.bible_passages == [{"book": "Romans", "label": "Romans 8"}]
    # Provenance stamped.
    assert enrichment.prompt_version == PROMPT_VERSION
    assert enrichment.model  # the configured model name
    assert enrichment.generated_at is not None


def test_store_enrichment_updates_in_place(monkeypatch):
    video = VideoFactory()
    monkeypatch.setattr("catalogue.enrichment.enrich_video", lambda *a, **k: _suggestions(summary="first"))
    first = store_enrichment(video)

    monkeypatch.setattr(
        "catalogue.enrichment.enrich_video",
        lambda *a, **k: _suggestions(summary="second", keywords=["new"]),
    )
    second = store_enrichment(video)

    assert VideoEnrichment.objects.filter(video=video).count() == 1
    assert second.pk == first.pk
    assert second.summary == "second"
    assert second.keywords == ["new"]


def test_store_enrichment_no_ops_when_model_returns_nothing(monkeypatch):
    """An unreachable / unparseable model yields empty_suggestions — we must not
    store an empty row (which would mark the video 'done' for the batch)."""
    from catalogue.enrichment import empty_suggestions

    video = VideoFactory()
    monkeypatch.setattr("catalogue.enrichment.enrich_video", lambda *a, **k: empty_suggestions())

    assert store_enrichment(video) is None
    assert not VideoEnrichment.objects.filter(video=video).exists()


def test_store_enrichment_records_the_model_override(monkeypatch):
    video = VideoFactory()
    monkeypatch.setattr("catalogue.enrichment.enrich_video", lambda *a, **k: _suggestions())

    enrichment = store_enrichment(video, model="gemma4:31b-it-qat")

    assert enrichment.model == "gemma4:31b-it-qat"


# --------------------------------------------------------------------------- #
# Invisible search feed — enrichment folds into the video's `text`
# --------------------------------------------------------------------------- #


def test_enrichment_keywords_fold_into_search_text(monkeypatch):
    video = VideoFactory(name="A talk", description="The given description.")
    monkeypatch.setattr("catalogue.enrichment.enrich_video", lambda *a, **k: _suggestions())
    store_enrichment(video)
    video.refresh_from_db()

    doc = search.build_video_doc(video)

    # Human description is preserved AND the AI keywords/topics/summary are folded in.
    assert "The given description." in doc["text"]
    assert "adoption" in doc["text"]  # a keyword
    assert "Grace" in doc["text"]  # a topic
    assert "A sermon on grace." in doc["text"]  # the summary


def test_missing_enrichment_is_a_search_no_op():
    video = VideoFactory(description="Just the description.")

    doc = search.build_video_doc(video)

    assert doc["text"] == "Just the description."


def test_build_video_doc_handles_empty_description_with_enrichment(monkeypatch):
    video = VideoFactory(description="")
    monkeypatch.setattr(
        "catalogue.enrichment.enrich_video", lambda *a, **k: _suggestions(summary="", suggested_topics=[])
    )
    store_enrichment(video)
    video.refresh_from_db()

    doc = search.build_video_doc(video)

    # No description, no summary/topics — just the keywords, cleanly joined.
    assert doc["text"] == "grace adoption spirit"


# --------------------------------------------------------------------------- #
# Signal — storing/removing enrichment re-indexes the parent video
# --------------------------------------------------------------------------- #


def test_storing_enrichment_reindexes_the_video(monkeypatch):
    video = VideoFactory()
    monkeypatch.setattr("catalogue.enrichment.enrich_video", lambda *a, **k: _suggestions())

    indexed = []
    monkeypatch.setattr(search, "index_object", lambda obj: indexed.append(obj))

    store_enrichment(video)

    assert any(getattr(obj, "pk", None) == video.pk for obj in indexed)


def test_deleting_enrichment_reindexes_the_video(monkeypatch):
    video = VideoFactory()
    monkeypatch.setattr("catalogue.enrichment.enrich_video", lambda *a, **k: _suggestions())
    enrichment = store_enrichment(video)

    indexed = []
    monkeypatch.setattr(search, "index_object", lambda obj: indexed.append(obj))

    enrichment.delete()

    assert any(getattr(obj, "pk", None) == video.pk for obj in indexed)
