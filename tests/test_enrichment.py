"""AI metadata enrichment PoC (catalogue/enrichment.py, issue #201).

The Ollama HTTP call is always mocked here — no test touches the network. The
one optional live test is skipped unless the host is actually reachable.
"""

import json
import logging

import pytest
import requests

from catalogue import enrichment
from catalogue.enrichment import (
    build_prompt,
    cross_check_passages,
    empty_suggestions,
    enrich_video,
    parse_json_response,
)
from tests.factories import SeriesFactory, SpeakerFactory, VideoFactory

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return {"response": self._payload}


def fake_post_returning(payload, captured=None):
    """A drop-in for ``requests.post`` that records the call and returns ``payload``
    as the model's ``response`` text."""

    def _post(url, json=None, timeout=None):
        if captured is not None:
            captured["url"] = url
            captured["json"] = json
            captured["timeout"] = timeout
        return FakeResponse(payload)

    return _post


# --------------------------------------------------------------------------- #
# Prompt building — from the right fields
# --------------------------------------------------------------------------- #


def test_prompt_built_from_title_and_description():
    video = VideoFactory(name="Luke 20:9-19 - The Wicked Tenants", description="A sermon on the parable.")
    prompt = build_prompt(video)
    assert "Luke 20:9-19 - The Wicked Tenants" in prompt
    assert "A sermon on the parable." in prompt


def test_prompt_includes_speaker_and_series_context():
    speaker = SpeakerFactory(name="Dr Martyn Lloyd-Jones")
    series = SeriesFactory(name="Studies in Luke")
    video = VideoFactory(name="Luke 20 - Talk 3", series=series)
    video.speaker.add(speaker)

    prompt = build_prompt(video)
    assert "Dr Martyn Lloyd-Jones" in prompt
    assert "Studies in Luke" in prompt


def test_prompt_includes_transcript_excerpt_when_provided():
    video = VideoFactory(name="A talk", description="desc")
    prompt = build_prompt(video, transcript="The grace of God is sufficient. " * 10)
    assert "Transcript (excerpt)" in prompt
    assert "The grace of God is sufficient." in prompt


def test_prompt_omits_transcript_section_by_default():
    video = VideoFactory(name="A talk", description="desc")
    assert "Transcript" not in build_prompt(video)


# --------------------------------------------------------------------------- #
# Defensive JSON parsing
# --------------------------------------------------------------------------- #


def test_parse_clean_json():
    assert parse_json_response('{"summary": "hi"}') == {"summary": "hi"}


def test_parse_json_wrapped_in_code_fence():
    raw = '```json\n{"summary": "fenced"}\n```'
    assert parse_json_response(raw) == {"summary": "fenced"}


def test_parse_json_embedded_in_prose():
    raw = 'Sure! Here is the metadata:\n{"summary": "embedded", "keywords": ["a"]}\nHope that helps.'
    assert parse_json_response(raw) == {"summary": "embedded", "keywords": ["a"]}


def test_parse_handles_nested_braces():
    raw = 'noise {"summary": "has {brace} inside", "topics": ["x"]} trailing junk }'
    parsed = parse_json_response(raw)
    assert parsed["summary"] == "has {brace} inside"
    assert parsed["topics"] == ["x"]


@pytest.mark.parametrize("raw", ["", "   ", "not json at all", "{broken", None, "[1, 2, 3]"])
def test_parse_malformed_returns_empty_dict(raw):
    assert parse_json_response(raw) == {}


# --------------------------------------------------------------------------- #
# Bible passage cross-check
# --------------------------------------------------------------------------- #


def test_cross_check_keeps_valid_passage_and_normalises_label():
    result = cross_check_passages(["Luke 20:9-19"])
    assert len(result) == 1
    entry = result[0]
    assert entry["book"] == "Luke"
    assert entry["chapter"] == 20
    assert entry["verse_start"] == 9
    assert entry["verse_end"] == 19
    assert entry["label"] == "Luke 20:9-19"


def test_cross_check_handles_book_with_leading_number():
    result = cross_check_passages(["1 Samuel 18"])
    assert result[0]["book"] == "1 Samuel"
    assert result[0]["chapter"] == 18
    assert result[0]["label"] == "1 Samuel 18"


def test_cross_check_drops_hallucinated_books():
    result = cross_check_passages(["Book of Hezekiah 4:2", "The Gospel of Thomas 1"])
    assert result == []


def test_cross_check_accepts_comma_separated_string():
    result = cross_check_passages("John 3:16, Romans 8")
    labels = {e["label"] for e in result}
    assert labels == {"John 3:16", "Romans 8"}


def test_cross_check_dedupes():
    result = cross_check_passages(["John 3:16", "John 3:16"])
    assert len(result) == 1


# --------------------------------------------------------------------------- #
# enrich_video — happy path
# --------------------------------------------------------------------------- #


def test_enrich_video_returns_full_suggestions(monkeypatch):
    video = VideoFactory(name="Luke 20:9-19 - The Wicked Tenants", description="A parable.")
    payload = json.dumps(
        {
            "summary": "Jesus tells the parable of the wicked tenants.",
            "suggested_topics": ["Parables", "Judgement"],
            "suggested_audience": "Adults",
            "bible_passages": ["Luke 20:9-19", "Made up 1:1"],
            "keywords": ["parable", "vineyard"],
        }
    )
    captured = {}
    monkeypatch.setattr(requests, "post", fake_post_returning(payload, captured))

    result = enrich_video(video)

    assert result["summary"] == "Jesus tells the parable of the wicked tenants."
    assert result["suggested_topics"] == ["Parables", "Judgement"]
    assert result["suggested_audience"] == "Adults"
    assert result["keywords"] == ["parable", "vineyard"]
    # Hallucinated passage dropped; valid one normalised.
    assert [p["label"] for p in result["bible_passages"]] == ["Luke 20:9-19"]

    # Prompt was built from the right fields and sent to /api/generate.
    assert captured["url"].endswith("/api/generate")
    assert "Luke 20:9-19 - The Wicked Tenants" in captured["json"]["prompt"]


def test_enrich_video_uses_model_override(monkeypatch):
    video = VideoFactory()
    captured = {}
    monkeypatch.setattr(requests, "post", fake_post_returning("{}", captured))
    enrich_video(video, model="gemma4:26b-a4b-it-qat")
    assert captured["json"]["model"] == "gemma4:26b-a4b-it-qat"


# --------------------------------------------------------------------------- #
# enrich_video — resilience (never raises)
# --------------------------------------------------------------------------- #


def test_enrich_video_timeout_returns_empty(monkeypatch):
    video = VideoFactory()

    def _raise(*_args, **_kwargs):
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr(requests, "post", _raise)
    assert enrich_video(video) == empty_suggestions()


def test_enrich_video_connection_error_returns_empty(monkeypatch):
    video = VideoFactory()

    def _raise(*_args, **_kwargs):
        raise requests.exceptions.ConnectionError("connection refused")

    monkeypatch.setattr(requests, "post", _raise)
    assert enrich_video(video) == empty_suggestions()


def test_transport_failure_is_an_error_but_unparseable_output_is_a_warning(monkeypatch, caplog):
    def _raise(*_args, **_kwargs):
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr(requests, "post", _raise)

    with caplog.at_level(logging.WARNING, logger="catalogue.enrichment"):
        assert enrichment.call_ollama("prompt") is None

    transport = caplog.records[-1]
    assert transport.levelno == logging.ERROR
    assert transport.exc_info is not None

    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="catalogue.enrichment"):
        assert parse_json_response("not JSON") == {}

    assert caplog.records[-1].levelno == logging.WARNING


def test_enrich_video_unparseable_output_returns_empty(monkeypatch):
    video = VideoFactory()
    monkeypatch.setattr(requests, "post", fake_post_returning("the model rambled with no json"))
    assert enrich_video(video) == empty_suggestions()


def test_enrich_video_partial_output_fills_what_it_can(monkeypatch):
    video = VideoFactory()
    monkeypatch.setattr(requests, "post", fake_post_returning('{"summary": "only a summary"}'))
    result = enrich_video(video)
    assert result["summary"] == "only a summary"
    assert result["suggested_topics"] == []
    assert result["bible_passages"] == []


def test_enrich_video_coerces_string_topics_to_list(monkeypatch):
    video = VideoFactory()
    payload = json.dumps({"suggested_topics": "Grace, Faith, Hope"})
    monkeypatch.setattr(requests, "post", fake_post_returning(payload))
    result = enrich_video(video)
    assert result["suggested_topics"] == ["Grace", "Faith", "Hope"]


def test_empty_suggestions_has_all_keys():
    s = empty_suggestions()
    assert set(s) == {"summary", "suggested_topics", "suggested_audience", "bible_passages", "keywords"}
    assert s["summary"] == ""
    assert s["suggested_topics"] == []


# --------------------------------------------------------------------------- #
# Optional live test — skipped unless Ollama is actually reachable
# --------------------------------------------------------------------------- #


def _ollama_reachable():
    host, _model, _timeout = enrichment._ollama_config()
    try:
        requests.get(f"{host.rstrip('/')}/api/tags", timeout=2)
    except requests.RequestException:
        return False
    return True


@pytest.mark.skipif(not _ollama_reachable(), reason="Ollama host not reachable")
def test_enrich_video_live_smoke():
    video = VideoFactory(
        name="John 3:16 - For God So Loved the World",
        description="An evangelistic message on the love of God.",
    )
    result = enrich_video(video)
    # We can't assert exact content, only the shape and that it didn't crash.
    assert set(result) == set(empty_suggestions())
    assert isinstance(result["bible_passages"], list)
