import pytest

from catalogue.models import Video
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db

CSV = """ID,ID Number,Name,Description,URL,Thumbnail,DateRecorded,DateCreated,IsLivestream
1,YT000001,Sunday Service,desc,https://youtu.be/a,t,01/01/2026,01/01/2026,1
2,YT000002,Midweek Talk,desc,https://youtu.be/b,t,01/01/2026,01/01/2026,0
"""


def write_csv(tmp_path):
    path = tmp_path / "Videos.csv"
    path.write_text(CSV, encoding="utf-8-sig")
    return str(path)


def test_backfill_promotes_and_demotes_to_match_csv(tmp_path):
    from django.core.management import call_command

    live = VideoFactory(id="1", is_livestream=False)  # should be promoted
    not_live = VideoFactory(id="2", is_livestream=True)  # should be demoted
    stale = VideoFactory(id="99", is_livestream=True)  # not in CSV → demoted

    call_command("backfill_livestream_flags", csv=write_csv(tmp_path))

    live.refresh_from_db()
    not_live.refresh_from_db()
    stale.refresh_from_db()
    assert live.is_livestream is True
    assert not_live.is_livestream is False
    assert stale.is_livestream is False


def test_backfill_is_idempotent(tmp_path):
    from django.core.management import call_command

    VideoFactory(id="1", is_livestream=False)
    path = write_csv(tmp_path)

    call_command("backfill_livestream_flags", csv=path)
    call_command("backfill_livestream_flags", csv=path)

    assert Video.objects.filter(is_livestream=True).count() == 1
