"""Repairing dates the live admin left blank but the ref still encodes —
runs locally off id_number, no network. Idempotent."""

import pytest

from catalogue.management.commands.backfill_dates_from_ref import recover_dates
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db


def test_recovers_dates_for_undated_videos_whose_ref_encodes_one():
    dated_in_ref = VideoFactory(date_recorded=None, id_number="MD8280CINews25.10.24")
    genuinely_undateable = VideoFactory(date_recorded=None, id_number="RedRocksWorshipAscend")
    already_dated = VideoFactory(date_recorded="2026-06-07", id_number="YT6336SermonPM31.05.26")

    updated = recover_dates()

    dated_in_ref.refresh_from_db()
    genuinely_undateable.refresh_from_db()
    already_dated.refresh_from_db()

    assert updated == 1
    assert dated_in_ref.date_recorded.isoformat() == "2024-10-25"
    assert genuinely_undateable.date_recorded is None  # nothing to recover, left null
    assert already_dated.date_recorded.isoformat() == "2026-06-07"  # not clobbered


def test_is_idempotent():
    VideoFactory(date_recorded=None, id_number="MD8280CINews25.10.24")

    assert recover_dates() == 1
    assert recover_dates() == 0  # second pass finds nothing left to do
