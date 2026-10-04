"""Bulk import behaviour when Typesense is unavailable (#326)."""

from io import StringIO

import httpx
import pytest
from django.core.management import call_command

from catalogue import search
from catalogue.management.commands import link_and_import_all
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("failure", [search.SearchUnavailableError("not configured"), httpx.ConnectError("refused")])
def test_bulk_import_skips_per_object_indexing_and_reports_one_unavailable_reindex(monkeypatch, failure):
    def create_imported_video(_command, _debug):
        VideoFactory(name="Imported video")

    def create_linked_video(_command, _debug):
        VideoFactory(name="Linked video")

    indexed = []

    def record_index(video):
        indexed.append(video.pk)
        return False

    reindex_attempts = []

    def unavailable_reindex(**_kwargs):
        reindex_attempts.append(True)
        raise failure

    monkeypatch.setattr(link_and_import_all.Import, "myimport", create_imported_video)
    monkeypatch.setattr(link_and_import_all.Link, "mylink", create_linked_video)
    monkeypatch.setattr(search, "index_object", record_index)
    monkeypatch.setattr(
        link_and_import_all,
        "reindex",
        unavailable_reindex,
    )

    output = StringIO()
    call_command("link_and_import_all", stdout=output)

    assert indexed == []
    assert reindex_attempts == [True]
    assert "Typesense unavailable; skipped search reindex." in output.getvalue()

    VideoFactory(name="Saved after bulk import")
    assert len(indexed) == 1
