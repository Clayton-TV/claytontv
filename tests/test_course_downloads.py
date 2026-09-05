from __future__ import annotations

import os
import subprocess
import sys
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "download_course_media.py"
MANIFEST = ROOT / "scripts" / "course-downloads.tsv"
BODY = b"the local fixture checks interrupted transfers"
PDF_BODY = b"%PDF-1.7\nfixture"
HTML_BODY = b"<html>not a PDF</html>"


@contextmanager
def fixture_server():
    class Handler(BaseHTTPRequestHandler):
        interrupted = False
        starts: ClassVar[list[int]] = []

        def do_GET(self):
            if self.path == "/missing":
                self.send_error(404)
                return
            if self.path == "/no-range":
                self.send_response(200)
                self.send_header("Content-Length", str(len(BODY)))
                self.end_headers()
                self.wfile.write(BODY)
                return
            if self.path == "/html":
                self.send_response(200)
                self.send_header("Content-Length", str(len(HTML_BODY)))
                self.end_headers()
                self.wfile.write(HTML_BODY)
                return
            if self.path == "/pdf":
                self.send_response(200)
                self.send_header("Content-Length", str(len(PDF_BODY)))
                self.end_headers()
                self.wfile.write(PDF_BODY)
                return

            start = int(self.headers.get("Range", "bytes=0-")[6:].split("-")[0])
            type(self).starts.append(start)
            if not type(self).interrupted and start == 0:
                type(self).interrupted = True
                self.send_response(200)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(len(BODY)))
                self.end_headers()
                self.wfile.write(BODY[:12])
                self.wfile.flush()
                self.connection.shutdown(2)
                return

            content = BODY[start:]
            self.send_response(206 if start else 200)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(len(content)))
            if start:
                self.send_header("Content-Range", f"bytes {start}-{len(BODY) - 1}/{len(BODY)}")
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", Handler
    finally:
        server.shutdown()
        thread.join()


def run_downloader(output: Path, manifest: Path, *, retries: str = "0"):
    env = os.environ | {"CURL_RETRIES": retries}
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(output), "--manifest", str(manifest)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_manifest_has_50_distinct_urls_and_separate_first_video():
    rows = [line.split("\t") for line in MANIFEST.read_text().splitlines()[1:]]
    urls = [row[2] for row in rows]

    assert len(rows) == len(set(urls)) == 50
    first_unit = [row for row in rows if "unit-01" in row[1] and "training" in row[1]]
    assert [row[1] for row in first_unit] == [
        "training-for-childrens-ministry/unit-01-worksheet.pdf",
        "training-for-childrens-ministry/unit-01-video.mp4",
    ]
    assert all("Worksheet" not in row[2] for row in rows if row[1].endswith("-video.mp4"))


def test_downloader_resumes_failure_skips_completed_and_reports_failure(tmp_path):
    with fixture_server() as (base_url, handler):
        manifest = tmp_path / "fixture.tsv"
        manifest.write_text(
            "course\tpath\turl\nFixture\tmedia/file.bin\t"
            f"{base_url}/file\nFixture\tmedia/missing.bin\t{base_url}/missing\n"
        )
        output = tmp_path / "downloads"

        first = run_downloader(output, manifest)
        assert first.returncode == 1
        assert (output / "media/file.bin.part").read_bytes() == BODY[:12]
        assert "failed\tmedia/missing.bin" in (output / "download-report.tsv").read_text()

        manifest.write_text(f"course\tpath\turl\nFixture\tmedia/file.bin\t{base_url}/changed\n")
        changed_url = run_downloader(output, manifest)
        assert changed_url.returncode == 1
        assert handler.starts == [0]
        assert "different or unknown URL" in (output / "download-report.tsv").read_text()

        manifest.write_text(f"course\tpath\turl\nFixture\tmedia/file.bin\t{base_url}/file\n")
        second = run_downloader(output, manifest)
        assert second.returncode == 0
        assert (output / "media/file.bin").read_bytes() == BODY
        assert handler.starts == [0, 12]

        third = run_downloader(output, manifest)
        assert third.returncode == 0
        assert handler.starts == [0, 12]
        assert "skipped\tmedia/file.bin" in (output / "download-report.tsv").read_text()


def test_downloader_rejects_manifest_path_outside_output_directory(tmp_path):
    manifest = tmp_path / "fixture.tsv"
    manifest.write_text("course\tpath\turl\nFixture\t../outside.bin\thttp://127.0.0.1/file\n")

    result = run_downloader(tmp_path / "downloads", manifest)

    assert result.returncode == 1
    assert not (tmp_path / "outside.bin").exists()
    assert "must stay inside the output directory" in result.stderr


def test_downloader_handles_no_range_resume_and_rejects_html_as_pdf(tmp_path):
    with fixture_server() as (base_url, _handler):
        output = tmp_path / "downloads"
        partial = output / "media/no-range.bin.part"
        partial.parent.mkdir(parents=True)
        partial.write_bytes(BODY[:12])
        state = output / ".course-downloads-state/media/no-range.bin.part.url"
        state.parent.mkdir(parents=True)
        state.write_text(f"{base_url}/no-range\n")
        manifest = tmp_path / "fixture.tsv"
        manifest.write_text(
            "course\tpath\turl\n"
            f"Fixture\tmedia/no-range.bin\t{base_url}/no-range\n"
            f"Fixture\tmedia/error.pdf\t{base_url}/html\n"
            f"Fixture\tmedia/valid.pdf\t{base_url}/pdf\n"
        )

        result = run_downloader(output, manifest)

        assert result.returncode == 1
        assert "curl could not resume (exit 33)" in result.stderr
        assert partial.exists()
        assert (output / "media/error.pdf.part.rejected").read_bytes() == HTML_BODY
        assert not (output / ".course-downloads-state/media/error.pdf.url").exists()
        assert (output / "media/valid.pdf").read_bytes() == PDF_BODY
