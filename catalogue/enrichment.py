"""AI metadata enrichment via a self-hosted Ollama LLM (Epic #201).

`enrich_video(video, transcript=None)` asks the model to read a video's title +
description (plus speaker/series context) and propose catalogue metadata: a
summary, topics, an audience, Bible passages and keywords. It returns a plain
SUGGESTIONS dict — nothing is written to the database.

`store_enrichment(video)` is the wiring on top: it runs `enrich_video` and
upserts a `VideoEnrichment` row (stamping the model + prompt version), so the
values can feed search recall invisibly and, later, the editor pre-fill UI.

Design notes
------------
- **Resilient by construction.** A model timeout, a transport error, or garbage
  output must never raise — the caller gets ``empty_suggestions()`` (or a
  partial dict) instead. Enrichment is advisory; it can't be allowed to break a
  command or a save.
- **STRICT JSON prompt, defensive parse.** Small quantised models wrap JSON in
  prose or ```json fences and occasionally emit trailing junk; we strip fences
  and fall back to extracting the first balanced ``{...}`` object before giving
  up.
- **Bible refs are cross-checked against the real catalogue** using
  ``catalogue.passages`` + the canonical book list, so a hallucinated or
  malformed reference is dropped and a valid one is normalised to a
  ``{"book", "label", ...}`` shape the importer could later consume. We mostly
  have NO transcripts yet, so the default path works from title + description;
  the ``transcript`` arg is plumbed through for when we do.
"""

import json
import logging
import re

import requests
from django.conf import settings
from django.utils import timezone

from catalogue.passages import parse_passage, passage_label

logger = logging.getLogger(__name__)

# Bumping this invalidates stored enrichments: the batch (E2) re-runs any row
# whose prompt_version is behind, so a prompt/schema change re-enriches cleanly.
PROMPT_VERSION = 1

# The keys every SUGGESTIONS dict carries, with their empty defaults. Callers can
# rely on the shape being present even on total failure.
SUGGESTION_KEYS = {
    "summary": "",
    "suggested_topics": list,
    "suggested_audience": "",
    "bible_passages": list,
    "keywords": list,
}


def empty_suggestions():
    """A fully-formed SUGGESTIONS dict with every field at its empty default."""
    return {k: (default() if callable(default) else default) for k, default in SUGGESTION_KEYS.items()}


# --------------------------------------------------------------------------- #
# Canonical Bible book names (for cross-checking model output)
# --------------------------------------------------------------------------- #


def _canonical_book_names():
    """Display names of every Bible book the catalogue knows, e.g. ``"1 Samuel"``.
    Imported lazily so this module stays import-safe outside Django app loading.
    """
    from catalogue.models.bible_book import BIBLE_BOOKS

    return [display for _code, display in BIBLE_BOOKS]


# --------------------------------------------------------------------------- #
# Prompt building
# --------------------------------------------------------------------------- #

_SYSTEM_PROMPT = (
    "You are a metadata assistant for a Christian church video catalogue. "
    "Given a video's title and description, you propose catalogue metadata. "
    "Reply with STRICT JSON only — no prose, no markdown, no code fences. "
    "Use this exact schema, with these keys:\n"
    "{\n"
    '  "summary": "one or two plain-sentence summary of the video",\n'
    '  "suggested_topics": ["short topic", ...],\n'
    '  "suggested_audience": "the intended audience, e.g. Adults, Youth, Children, Families",\n'
    '  "bible_passages": ["Book Chapter:Verse", ...],\n'
    '  "keywords": ["keyword", ...]\n'
    "}\n"
    "Bible passages must use full book names like 'John 3:16', '1 Samuel 18'. "
    "If a field is unknown, use an empty string or empty list. Output JSON only."
)


def build_prompt(video, transcript=None):
    """Assemble the user prompt from the fields that carry signal: title,
    description, speaker(s) and series for context, and a transcript when (one
    day) we have one."""
    lines = [f"Title: {video.name or ''}", f"Description: {video.description or ''}"]

    speakers = _related_names(video, "speaker")
    if speakers:
        lines.append(f"Speaker(s): {', '.join(speakers)}")

    series_name = getattr(getattr(video, "series", None), "name", None)
    if series_name:
        lines.append(f"Series: {series_name}")

    if transcript:
        # Keep the prompt bounded — a full transcript can be enormous, and the
        # opening usually carries the passage + theme.
        lines.append(f"Transcript (excerpt):\n{transcript[:8000]}")

    lines.append("\nReturn the metadata JSON now.")
    return "\n".join(lines)


def _related_names(video, attr):
    """Names from an M2M relation, swallowing any DB error (best-effort context)."""
    try:
        manager = getattr(video, attr)
        return [obj.name for obj in manager.all() if getattr(obj, "name", None)]
    except Exception:
        return []


# --------------------------------------------------------------------------- #
# Ollama client (thin)
# --------------------------------------------------------------------------- #


def _ollama_config():
    cfg = getattr(settings, "OLLAMA", None) or {}
    return (
        cfg.get("host", "http://100.81.40.52:11434"),
        cfg.get("model", "gemma4:31b-it-qat"),
        cfg.get("timeout_seconds", 120),
    )


def call_ollama(prompt, *, system=_SYSTEM_PROMPT, model=None, timeout=None):
    """POST to Ollama's native ``/api/generate`` and return the raw response text,
    or ``None`` on any timeout / transport / HTTP error. Never raises.

    ``format="json"`` nudges the server to constrain output to JSON; we still
    parse defensively because small models don't always honour it.
    """
    host, default_model, default_timeout = _ollama_config()
    payload = {
        "model": model or default_model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2},
    }
    url = f"{host.rstrip('/')}/api/generate"
    try:
        resp = requests.post(url, json=payload, timeout=timeout or default_timeout)
        resp.raise_for_status()
        return resp.json().get("response", "")
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Ollama call failed (%s): %s", url, exc)
        return None


# --------------------------------------------------------------------------- #
# Defensive JSON parsing
# --------------------------------------------------------------------------- #

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def parse_json_response(text):
    """Best-effort parse of model output into a dict. Handles bare JSON, JSON
    wrapped in ``` fences, and JSON embedded in surrounding prose. Returns
    ``{}`` (never raises) when nothing usable is found."""
    if not text or not text.strip():
        return {}

    candidate = _FENCE_RE.sub("", text.strip())

    # 1) Straight parse.
    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        pass

    # 2) Extract the first balanced {...} block and try that.
    block = _first_json_object(candidate)
    if block:
        try:
            parsed = json.loads(block)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            pass

    logger.warning("Could not parse JSON from model output: %.200s", text)
    return {}


# A JSON token: a complete double-quoted string (with escapes) OR a single
# non-string character. Iterating these lets us count braces while treating any
# brace inside a string as opaque, without hand-rolling a character state machine.
_JSON_TOKEN_RE = re.compile(r'"(?:\\.|[^"\\])*"|.', re.DOTALL)


def _first_json_object(text):
    """Return the substring of the first balanced ``{...}`` object, or ``None``.
    Brace-counting, ignoring braces inside strings."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for match in _JSON_TOKEN_RE.finditer(text, start):
        token = match.group()
        if token == "{":
            depth += 1
        elif token == "}":
            depth -= 1
            if depth == 0:
                return text[start : match.end()]
    return None


# --------------------------------------------------------------------------- #
# Normalisation / coercion
# --------------------------------------------------------------------------- #


def _as_str_list(value):
    """Coerce a model field into a clean list of non-empty strings. Accepts a
    list, a comma-separated string, or ``None``."""
    if value is None:
        return []
    if isinstance(value, str):
        value = value.split(",")
    if not isinstance(value, (list, tuple)):
        return []
    out = []
    for item in value:
        s = str(item).strip()
        if s:
            out.append(s)
    return out


def cross_check_passages(raw_passages):
    """Validate model-suggested Bible references against the real catalogue.

    Each raw reference is matched (case-insensitively) against a known book name
    and re-parsed with ``catalogue.passages`` so we emit a normalised shape and
    silently drop hallucinations / malformed refs. Returns a list of
    ``{"book", "label"?, "chapter"?, "verse_start"?, "verse_end"?, "raw"}`` dicts.
    """
    books = _canonical_book_names()
    # Longest names first so "1 Samuel" wins over a bare "Samuel"-style partial.
    books_sorted = sorted(books, key=len, reverse=True)

    results = []
    seen = set()
    for raw in _as_str_list(raw_passages):
        matched_book = _match_book(raw, books_sorted)
        if not matched_book:
            continue
        passage = parse_passage(raw, matched_book)
        entry = {"book": matched_book, "raw": raw}
        if passage:
            entry["chapter"] = passage["chapter"]
            entry["verse_start"] = passage["verse_start"]
            entry["verse_end"] = passage["verse_end"]
            label = passage_label(passage)
            entry["label"] = f"{matched_book} {label}" if label else matched_book
        else:
            entry["label"] = matched_book
        # Dedupe on the normalised label.
        if entry["label"] not in seen:
            seen.add(entry["label"])
            results.append(entry)
    return results


def _match_book(reference, books_sorted):
    """Return the canonical book name that ``reference`` starts with / contains,
    else ``None``. ``parse_passage`` handles the chapter/verse from there."""
    ref_lower = reference.lower()
    for book in books_sorted:
        if ref_lower.startswith(book.lower()) or book.lower() in ref_lower:
            return book
    return None


# --------------------------------------------------------------------------- #
# Public entry points
# --------------------------------------------------------------------------- #


def enrich_video(video, transcript=None, *, model=None, timeout=None):
    """Return a SUGGESTIONS dict of AI-proposed metadata for ``video``.

    Never raises and never writes to the DB. On any failure (Ollama
    unreachable, timeout, unparseable output) returns ``empty_suggestions()``;
    on partial output, fills what it can and leaves the rest empty.
    """
    prompt = build_prompt(video, transcript=transcript)
    raw = call_ollama(prompt, model=model, timeout=timeout)
    if raw is None:
        return empty_suggestions()

    data = parse_json_response(raw)
    if not data:
        return empty_suggestions()

    suggestions = empty_suggestions()
    summary = data.get("summary")
    if isinstance(summary, str):
        suggestions["summary"] = summary.strip()
    audience = data.get("suggested_audience")
    if isinstance(audience, str):
        suggestions["suggested_audience"] = audience.strip()
    suggestions["suggested_topics"] = _as_str_list(data.get("suggested_topics"))
    suggestions["keywords"] = _as_str_list(data.get("keywords"))
    suggestions["bible_passages"] = cross_check_passages(data.get("bible_passages"))
    return suggestions


def store_enrichment(video, transcript=None, *, model=None, timeout=None):
    """Run ``enrich_video`` and upsert the video's ``VideoEnrichment`` row,
    stamping the model + ``PROMPT_VERSION``. Returns the row, or ``None`` when
    the model produced nothing (unreachable / unparseable) — so a batch run
    leaves the video for a later retry rather than marking it done with an empty
    row. Human-authored ``Video`` fields are never touched.

    Saving the row fires the search signal, which folds the new keywords /
    summary / topics into the video's Typesense doc (invisible recall boost).
    """
    from catalogue.models.enrichment import VideoEnrichment

    suggestions = enrich_video(video, transcript=transcript, model=model, timeout=timeout)
    if suggestions == empty_suggestions():
        return None

    resolved_model = model or _ollama_config()[1]
    enrichment, _created = VideoEnrichment.objects.update_or_create(
        video=video,
        defaults={
            "summary": suggestions["summary"],
            "topics": suggestions["suggested_topics"],
            "audience": suggestions["suggested_audience"],
            "bible_passages": suggestions["bible_passages"],
            "keywords": suggestions["keywords"],
            "model": resolved_model,
            "prompt_version": PROMPT_VERSION,
            "generated_at": timezone.now(),
        },
    )
    return enrichment
