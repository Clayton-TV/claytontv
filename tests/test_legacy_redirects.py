"""Legacy clayton.tv URL → new-route 301 redirects (cutover safety).

The dying site's watch URLs end in `.../0i0/<programme_id>/`; our Video.id is
that id, so they 301 to /video/<id> when the programme is public, else 404.
"""

import pytest

from catalogue.models.video import DRAFT
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "legacy_path",
    [
        "/new/0i0/{id}/",
        "/find/explore/475-1503/0i0/{id}/",
        "/find/explore/475-1477-1488/0i0/{id}/",
        "/schedule/0i0/{id}",  # no trailing slash
        "/new/0i0/{id}",  # tolerate missing trailing slash
    ],
)
def test_legacy_watch_urls_301_to_video(client, legacy_path):
    video = VideoFactory()  # published + alive by default
    resp = client.get(legacy_path.format(id=video.id))
    assert resp.status_code == 301
    assert resp.headers["Location"] == f"/video/{video.id}"


def test_unknown_id_404s(client):
    resp = client.get("/new/0i0/9999999/")
    assert resp.status_code == 404


def test_draft_is_not_redirected(client):
    video = VideoFactory(status=DRAFT)
    assert client.get(f"/new/0i0/{video.id}/").status_code == 404


def test_trashed_is_not_redirected(client):
    from app.studio import services

    video = VideoFactory()
    services.delete_videos([video.id])  # soft delete
    assert client.get(f"/new/0i0/{video.id}/").status_code == 404


def test_real_video_routes_are_not_shadowed(client):
    # The redirect pattern must only catch the legacy shapes, not real routes.
    video = VideoFactory()
    assert client.get(f"/video/{video.id}").status_code == 200
