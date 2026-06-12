"""Series-tree ingestion against a real trimmed slice of series.json
(tests/fixtures/legacy_series_sample.json): LIVE STREAMS tree + the nested
WEEKLY SERMONS tree."""

import json
from pathlib import Path

import pytest

from catalogue.ingest.series_tree import ingest_series_trees
from catalogue.models import Series, Video
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db

FIXTURE = Path(__file__).parent / "fixtures" / "legacy_series_sample.json"


@pytest.fixture
def trees():
    return json.loads(FIXTURE.read_text())


def programme_ids(trees):
    out = []

    def walk(node):
        out.extend(str(p["id"]) for p in node.get("programmes") or [])
        for sub in node.get("subSeries") or []:
            walk(sub)

    for tree in trees:
        walk(tree)
    return out


@pytest.fixture
def videos(trees):
    return {pid: VideoFactory(id=pid) for pid in programme_ids(trees)}


def test_series_upsert_by_id_number_with_clean_node_names(trees, videos):
    # Simulate the old pipeline's mangled path-joined name
    Series.objects.create(id_number="2817", name="Series '24: Revelation, John,Revelation: The Throne Room")

    stats = ingest_series_trees(trees)

    fixed = Series.objects.get(id_number="2817")
    assert fixed.name == "Revelation: The Throne Room"
    assert Series.objects.filter(id_number="2817").count() == 1
    # Browse roots ("BROWSE: WEEKLY SERMONS", "LIVE STREAMS") are taxonomy, not series
    assert not Series.objects.filter(name__startswith="BROWSE:").exists()
    assert not Series.objects.filter(id_number="471").exists()
    assert stats["series_created"] > 0


def test_memberships_and_episode_numbers_follow_dump_order(trees, videos):
    ingest_series_trees(trees)

    series = Series.objects.get(id_number="2817")
    members = list(series.videos.all())
    assert len(members) == 3
    expected_order = [str(p["id"]) for p in find_node(trees, 2817)["programmes"]]
    numbered = {v.id: v.number_in_series for v in Video.objects.filter(id__in=expected_order)}
    assert [numbered[pid] for pid in expected_order] == [1, 2, 3]


def test_livestream_flag_follows_tree_1993(trees, videos):
    live_node = find_node(trees, 1994)  # JPC 10.30am under LIVE STREAMS
    live_pid = str(live_node["programmes"][0]["id"])
    sermon_node = find_node(trees, 2817)
    sermon_pid = str(sermon_node["programmes"][0]["id"])
    # Wrong flags beforehand: sermon marked live, livestream not marked
    Video.objects.filter(id=sermon_pid).update(is_livestream=True)
    Video.objects.filter(id=live_pid).update(is_livestream=False)

    stats = ingest_series_trees(trees)

    assert Video.objects.get(id=live_pid).is_livestream is True
    assert Video.objects.get(id=sermon_pid).is_livestream is False
    assert stats["live_flagged"] >= 1
    assert stats["live_demoted"] >= 1


def test_videos_unknown_to_the_dump_keep_their_flag(trees, videos):
    newer = VideoFactory(id="99999", is_livestream=True)  # post-dump content

    ingest_series_trees(trees)

    newer.refresh_from_db()
    assert newer.is_livestream is True


def test_reingestion_is_a_no_op(trees, videos):
    ingest_series_trees(trees)
    snapshot = list(Series.objects.order_by("id_number").values("id_number", "name"))
    memberships = {s.id_number: list(s.videos.values_list("id", flat=True)) for s in Series.objects.all()}

    stats = ingest_series_trees(trees)

    assert stats["series_created"] == 0
    assert list(Series.objects.order_by("id_number").values("id_number", "name")) == snapshot
    assert {s.id_number: list(s.videos.values_list("id", flat=True)) for s in Series.objects.all()} == memberships


def test_series_routes_by_id_number_with_name_fallback(client, trees, videos):
    ingest_series_trees(trees)
    series = Series.objects.get(id_number="2817")
    series.videos.first()

    assert series.get_absolute_url() == "/series/2817"
    assert client.get("/series/2817").status_code == 200
    assert client.get("/series/Revelation%3A%20The%20Throne%20Room").status_code == 200


def find_node(trees, node_id):
    def walk(node):
        if node["id"] == node_id:
            return node
        for sub in node.get("subSeries") or []:
            found = walk(sub)
            if found:
                return found

    for tree in trees:
        found = walk(tree)
        if found:
            return found
    raise AssertionError(f"node {node_id} not in fixture")


class TestSeriesDeduplication:
    def trees_with(self, *nodes):
        """A minimal browse root wrapping the given series nodes."""
        return [{"id": 9000, "name": "BROWSE: ROOT", "subSeries": list(nodes)}]

    def node(self, nid, name, programme_ids):
        return {"id": nid, "name": name, "programmes": [{"id": p} for p in programme_ids]}

    def test_orphan_series_not_in_hierarchy_are_removed(self):
        from catalogue.models import Series

        Series.objects.create(id_number="999", name="Shorts with Peter Orr,Psalms")  # CSV artifact
        VideoFactory(id="1")

        stats = ingest_series_trees(self.trees_with(self.node(1994, "JPC Services", ["1"])))

        assert not Series.objects.filter(id_number="999").exists()
        assert Series.objects.filter(id_number="1994").exists()
        assert stats["orphans_removed"] == 1

    def test_identical_content_twins_collapse_to_lowest_id(self):
        from catalogue.models import Series

        for pid in ("1", "2"):
            VideoFactory(id=pid)
        # Same name, same videos, under two browse paths → one survives (id 488)
        trees = self.trees_with(
            self.node(1994, "JPC Services", ["1", "2"]),
            self.node(488, "JPC Services", ["1", "2"]),
        )

        stats = ingest_series_trees(trees)

        survivors = list(Series.objects.filter(name="JPC Services").values_list("id_number", flat=True))
        assert survivors == ["488"]
        assert stats["duplicates_merged"] == 1

    def test_same_name_distinct_content_is_kept(self):
        from catalogue.models import Series

        for pid in ("1", "2"):
            VideoFactory(id=pid)
        trees = self.trees_with(
            self.node(10, "One-offs", ["1"]),
            self.node(20, "One-offs", ["2"]),  # different video → genuinely separate
        )

        ingest_series_trees(trees)

        assert Series.objects.filter(name="One-offs").count() == 2

    def test_dedup_is_idempotent(self):
        from catalogue.models import Series

        for pid in ("1", "2"):
            VideoFactory(id=pid)
        trees = self.trees_with(
            self.node(1994, "JPC Services", ["1", "2"]),
            self.node(488, "JPC Services", ["1", "2"]),
        )

        ingest_series_trees(trees)
        ingest_series_trees(trees)  # re-run: re-creates 1994 then re-collapses

        assert list(Series.objects.filter(name="JPC Services").values_list("id_number", flat=True)) == ["488"]
