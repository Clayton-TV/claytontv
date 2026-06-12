"""The live-admin adapter, tested against synthetic HTML replicating the
observed form structure (input/textarea/select names verified in the
authenticated recon of 2026-06-12; see data/legacy_rescue/lookups/README.md)."""

import pytest

from catalogue.ingest.legacy import ingest_programmes
from catalogue.ingest.live_admin import list_programme_ids, parse_meta_page, to_dump_record
from catalogue.models import Video

pytestmark = pytest.mark.django_db

LIST_HTML = """
<table>
<tr><td><a href="mediaProgrammeMeta.asp?ID=12404">Luke 14 - Excuses</a></td></tr>
<tr><td><a href="mediaProgrammeTimeline.asp?ID=12404">timeline</a></td></tr>
<tr><td><a href="mediaProgrammeMeta.asp?ID=12403">Kids Talk</a></td></tr>
</table>
"""

META_HTML = """
<form action="mediaProgrammeMeta.asp?ID=12404">
<input name="programmeRef" value="YT6325KidsTalkAM17.05.26">
<input name="URL" value="Luke 14:1,15-24 - Excuses - Jesmond Parish - Sermon">
<input name="programmeName" value="Luke 14:1,15-24  - Excuses - Jesmond Parish - Sermon">
<input name="programmeDate" value="17/05/2026">
<textarea name="programmeDescription">&lt;p&gt;Dan McBride preaches.&lt;/p&gt;</textarea>
<input name="vimeoLink" value="https://www.youtube.com/watch?v=oCivERk8ZWQ">
<input name="ThumbnailURL" value="https://i.ytimg.com/vi/oCivERk8ZWQ/mqdefault.jpg">
<input name="ProgrammeTranscript" value="">
<input name="ProgrammeAudio" value="">
<select name="ProgrammeRelatedSpeakers" multiple>
  <option value="360|0" selected>McBride, Dan </option>
  <option value="11|0">Redfearn, Jonathan</option>
</select>
<select name="ProgrammeRelatedTopics" multiple>
  <option value="146|0" selected>&#8722;&#8722;&#8722; Preaching &amp; Teaching</option>
</select>
<select name="ProgrammeRelatedBooks" multiple>
  <option value="42|0" selected>Luke</option>
</select>
</form>
"""


class FakeSession:
    def __init__(self, pages):
        self.pages = pages

    def get(self, url, **kwargs):
        class R:
            status_code = 200
            url_ = None

            def __init__(self, text, url):
                self.text = text
                self.url = url

            def raise_for_status(self):
                pass

        for fragment, body in self.pages.items():
            if fragment in url:
                return R(body, url)
        return R("", url)


def test_list_page_yields_unique_ids_in_order():
    session = FakeSession({"mediaProgramme.asp": LIST_HTML})
    assert list_programme_ids(session, pages=1) == ["12404", "12403"]


def test_meta_page_parses_to_a_dump_shaped_record():
    record = to_dump_record("12404", parse_meta_page(META_HTML))

    assert record["id"] == 12404
    assert record["ref"] == "YT6325KidsTalkAM17.05.26"
    assert record["date_added"] == "2026-05-17"  # DD/MM/YYYY parsed
    assert record["media"][0]["url"] == "https://www.youtube.com/watch?v=oCivERk8ZWQ"
    assert record["label_a"] == [{"id": 360, "name": "McBride, Dan"}]
    assert record["label_b"][0]["id"] == 146
    assert record["label_c"] == [{"id": 42, "name": "Luke"}]
    # Only SELECTED options count — Redfearn is in the dropdown but not assigned
    assert all(label["id"] != 11 for label in record["label_a"])


def test_adapted_records_flow_through_the_standard_ingest():
    record = to_dump_record("12404", parse_meta_page(META_HTML))

    stats = ingest_programmes([record])

    assert stats["created"] == 1
    video = Video.objects.get(id="12404")
    assert video.name.startswith("Luke 14:1,15-24 - Excuses")  # double space normalized
    assert [s.name for s in video.speaker.all()] == ["McBride, Dan"]
    assert "Preaching & Teaching" in [t.name for t in video.topic.all()]

    # And the cornerstone: re-sync is a no-op
    again = ingest_programmes([to_dump_record("12404", parse_meta_page(META_HTML))])
    assert again["created"] == 0 and again["updated"] == 1
