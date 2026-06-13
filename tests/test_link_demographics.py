"""Demographic links were dropped by the dump/live-admin ingest (the admin
meta form has no demographic field). Recover them from the legacy CSV export,
which carries the comma-separated tags. Keyed on legacy id, idempotent."""

import pytest

from catalogue.management.commands.link_demographics_from_csv import link_demographics
from catalogue.models import Demographic
from tests.factories import DemographicFactory, VideoFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def demographics():
    return {name: DemographicFactory(name=name) for name in ("Kids", "Youth", "Adults")}


def write_csv(tmp_path, rows):
    path = tmp_path / "Videos.csv"
    lines = ["ID,Demographic,URL"]
    lines += [f'{vid},"{demo}",http://x' for vid, demo in rows]
    path.write_text("\n".join(lines) + "\n")
    return str(path)


def test_links_comma_separated_demographics(demographics, tmp_path):
    both = VideoFactory(id="500")
    solo = VideoFactory(id="501")
    csv_path = write_csv(tmp_path, [("500", "adult,kids"), ("501", "adult")])

    linked = link_demographics(csv_path)

    assert linked == 2
    assert {d.name for d in both.demographic.all()} == {"Adults", "Kids"}
    assert [d.name for d in solo.demographic.all()] == ["Adults"]


def test_blank_and_unknown_tags_are_ignored(demographics, tmp_path):
    blank = VideoFactory(id="600")
    junk = VideoFactory(id="601")
    csv_path = write_csv(tmp_path, [("600", ""), ("601", "grownups")])

    link_demographics(csv_path)

    assert blank.demographic.count() == 0
    assert junk.demographic.count() == 0


def test_rows_for_unknown_videos_are_skipped(demographics, tmp_path):
    csv_path = write_csv(tmp_path, [("999", "kids")])  # no such Video

    assert link_demographics(csv_path) == 0


def test_is_idempotent(demographics, tmp_path):
    video = VideoFactory(id="700")
    csv_path = write_csv(tmp_path, [("700", "kids")])

    assert link_demographics(csv_path) == 1
    link_demographics(csv_path)  # second pass

    assert [d.name for d in video.demographic.all()] == ["Kids"]  # not doubled


def test_demographic_page_shows_its_videos_after_linking(demographics, tmp_path):
    """The bug the user hit — /demographic/Kids was empty. browse_demographic
    renders demographic.video_set, so the M2M is what was missing."""
    VideoFactory(id="800", name="Beginning with God")
    VideoFactory(id="801", name="Adult sermon")
    link_demographics(write_csv(tmp_path, [("800", "kids"), ("801", "adult")]))

    names = [v.name for v in Demographic.objects.get(name="Kids").video_set.all()]

    assert names == ["Beginning with God"]
