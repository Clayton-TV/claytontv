"""Background enrichment batch (catalogue/management/commands/enrich_catalogue.py).

`store_enrichment` is always mocked — no test touches Ollama. We assert the
command's *orchestration*: which videos it picks, that it resumes/limits/throttles,
that one bad row never aborts the run, and that the ETA helper is sane.
"""

from io import StringIO

import pytest
from django.core.management import call_command

from catalogue.enrichment import PROMPT_VERSION
from catalogue.management.commands.enrich_catalogue import format_eta, pending_videos
from catalogue.models.enrichment import VideoEnrichment
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db

COMMAND_PATH = "catalogue.management.commands.enrich_catalogue.store_enrichment"


def _current_enrichment(video):
    return VideoEnrichment.objects.create(video=video, prompt_version=PROMPT_VERSION, keywords=["x"])


# --------------------------------------------------------------------------- #
# pending_videos — the resumable selection
# --------------------------------------------------------------------------- #


def test_pending_includes_videos_without_enrichment():
    video = VideoFactory()
    assert video in list(pending_videos())


def test_pending_excludes_videos_with_current_enrichment():
    video = VideoFactory()
    _current_enrichment(video)
    assert video not in list(pending_videos())


def test_pending_includes_videos_with_stale_prompt_version():
    video = VideoFactory()
    VideoEnrichment.objects.create(video=video, prompt_version=PROMPT_VERSION - 1)
    assert video in list(pending_videos())


def test_pending_excludes_soft_deleted_videos():
    from django.utils import timezone

    video = VideoFactory()
    video.deleted_at = timezone.now()
    video.save()
    assert video not in list(pending_videos())


def test_refresh_includes_already_enriched_videos():
    video = VideoFactory()
    _current_enrichment(video)
    assert video in list(pending_videos(refresh=True))


# --------------------------------------------------------------------------- #
# The command — orchestration
# --------------------------------------------------------------------------- #


def test_enriches_only_pending_videos(monkeypatch):
    pending = VideoFactory()
    already = VideoFactory()
    _current_enrichment(already)

    seen = []
    monkeypatch.setattr(COMMAND_PATH, lambda video, **k: seen.append(video.pk) or object())

    call_command("enrich_catalogue", "--sleep", "0", stdout=StringIO())

    assert pending.pk in seen
    assert already.pk not in seen


def test_limit_caps_the_run(monkeypatch):
    for _ in range(5):
        VideoFactory()

    seen = []
    monkeypatch.setattr(COMMAND_PATH, lambda video, **k: seen.append(video.pk) or object())

    call_command("enrich_catalogue", "--limit", "2", "--sleep", "0", stdout=StringIO())

    assert len(seen) == 2


def test_one_failure_does_not_abort_the_run(monkeypatch):
    good1, bad, good2 = VideoFactory(), VideoFactory(), VideoFactory()
    order = sorted([good1, bad, good2], key=lambda v: (v.date_created, v.id))

    seen = []

    def fake_store(video, **k):
        seen.append(video.pk)
        if video.pk == order[1].pk:  # the middle one explodes
            raise RuntimeError("ollama melted")
        return object()

    monkeypatch.setattr(COMMAND_PATH, fake_store)

    out = StringIO()
    call_command("enrich_catalogue", "--sleep", "0", stdout=out, stderr=StringIO())

    # All three were attempted despite the middle failure.
    assert len(seen) == 3
    assert "1 errors" in out.getvalue()


def test_empty_result_is_counted_and_left_for_retry(monkeypatch):
    VideoFactory()
    monkeypatch.setattr(COMMAND_PATH, lambda video, **k: None)  # model returned nothing

    out = StringIO()
    call_command("enrich_catalogue", "--sleep", "0", stdout=out, stderr=StringIO())

    assert "0 stored, 1 empty/retry" in out.getvalue()


def test_no_op_when_nothing_pending(monkeypatch):
    video = VideoFactory()
    _current_enrichment(video)

    called = []
    monkeypatch.setattr(COMMAND_PATH, lambda video, **k: called.append(video.pk))

    out = StringIO()
    call_command("enrich_catalogue", "--sleep", "0", stdout=out)

    assert called == []
    assert "up to date" in out.getvalue()


def test_model_override_is_passed_through(monkeypatch):
    VideoFactory()
    captured = {}
    monkeypatch.setattr(COMMAND_PATH, lambda video, **k: captured.update(k) or object())

    call_command("enrich_catalogue", "--sleep", "0", "--model", "gemma4:31b-it-qat", stdout=StringIO())

    assert captured.get("model") == "gemma4:31b-it-qat"


# --------------------------------------------------------------------------- #
# ETA helper — pure
# --------------------------------------------------------------------------- #


def test_format_eta_before_any_progress():
    assert format_eta(0, 100, 0) == "0/100 (0.0%)"


def test_format_eta_projects_rate_and_finish():
    line = format_eta(10, 100, 30.0)  # 3.0s/video, 90 remaining → 270s
    assert "10/100 (10.0%)" in line
    assert "3.0s/video" in line
    assert "ETA ~4m" in line
    assert "finish" in line


def test_format_eta_uses_days_and_hours_for_long_runs():
    # 1 done in 30s → 30s/video; 9999 remaining → ~83h → days+hours.
    line = format_eta(1, 10000, 30.0)
    assert "d" in line and "h" in line
