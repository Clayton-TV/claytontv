"""Studio editor — AI suggestions pre-fill (Epic #201, E3).

The edit props carry the stored enrichment (or None), and a /suggest endpoint
(re)generates it. store_enrichment is mocked — no test touches Ollama.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from app.auth import EDITORS_GROUP
from app.studio import services
from catalogue.enrichment import PROMPT_VERSION
from catalogue.models.enrichment import VideoEnrichment
from tests.factories import VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db

User = get_user_model()
PASSWORD = "pw-correct-horse-1"  # gitleaks:allow


def make_editor(username="editor"):
    user = User.objects.create_user(username=username, password=PASSWORD)
    group, _ = Group.objects.get_or_create(name=EDITORS_GROUP)
    user.groups.add(group)
    return user


def login_editor(client, username="editor"):
    make_editor(username)
    client.login(username=username, password=PASSWORD)


def _enrich(video):
    return VideoEnrichment.objects.create(
        video=video,
        summary="A sermon on grace.",
        topics=["Grace"],
        audience="Adults",
        bible_passages=[{"book": "Romans", "label": "Romans 8"}],
        keywords=["grace", "adoption"],
        prompt_version=PROMPT_VERSION,
    )


# --- enrichment in the edit props ---------------------------------------- #


def test_edit_props_enrichment_is_none_without_a_row():
    video = VideoFactory()
    props = services.get_video_for_edit(video.id)
    assert props["enrichment"] is None


def test_edit_props_include_stored_enrichment():
    video = VideoFactory()
    _enrich(video)

    props = services.get_video_for_edit(video.id)

    e = props["enrichment"]
    assert e["summary"] == "A sermon on grace."
    assert e["topics"] == ["Grace"]
    assert e["audience"] == "Adults"
    assert e["bible_passages"] == [{"book": "Romans", "label": "Romans 8"}]
    assert e["keywords"] == ["grace", "adoption"]


def test_edit_page_renders_enrichment_prop(client):
    login_editor(client)
    video = VideoFactory(name="Has suggestions")
    _enrich(video)

    page = inertia_page(client.get(f"/studio/videos/{video.id}/edit"))

    assert page["props"]["video"]["enrichment"]["summary"] == "A sermon on grace."


# --- the /suggest endpoint ----------------------------------------------- #


def test_suggest_regenerates_and_redirects(client, monkeypatch):
    login_editor(client)
    video = VideoFactory()

    called = []
    # The view does `from catalogue.enrichment import store_enrichment` at call
    # time, so patching it at the source intercepts the view's lookup.
    monkeypatch.setattr("catalogue.enrichment.store_enrichment", lambda v, **k: called.append(v.pk) or _enrich(v))

    resp = client.post(f"/studio/videos/{video.id}/suggest")

    assert resp.status_code == 302
    assert resp.headers["Location"] == f"/studio/videos/{video.id}/edit"
    assert called == [video.pk]


def test_suggest_warns_when_model_returns_nothing(client, monkeypatch):
    login_editor(client)
    video = VideoFactory()
    monkeypatch.setattr("catalogue.enrichment.store_enrichment", lambda v, **k: None)

    resp = client.post(f"/studio/videos/{video.id}/suggest", follow=False)

    assert resp.status_code == 302  # still redirects, just flashes a warning


def test_suggest_404_for_missing(client):
    login_editor(client)
    assert client.post("/studio/videos/ghost/suggest").status_code == 404


def test_suggest_requires_login(client):
    video = VideoFactory()
    assert client.post(f"/studio/videos/{video.id}/suggest").status_code == 302  # anon → login


def test_suggest_forbidden_for_non_editor(client):
    video = VideoFactory()
    User.objects.create_user(username="viewer", password=PASSWORD)
    client.login(username="viewer", password=PASSWORD)
    assert client.post(f"/studio/videos/{video.id}/suggest").status_code == 403


def test_suggest_rejects_get(client):
    login_editor(client)
    video = VideoFactory()
    assert client.get(f"/studio/videos/{video.id}/suggest").status_code == 405


# --- taxonomy uses Bible-book display names (so suggestions can match) ----- #


def test_taxonomy_bible_books_use_display_names():
    from tests.factories import BibleBookFactory

    BibleBookFactory(name="GEN")  # stored as the code; displays as "Genesis"
    books = services.taxonomy_options()["bible_books"]
    names = [b["name"] for b in books]
    assert "Genesis" in names  # the human name, not the raw "GEN" code
    assert "GEN" not in names
