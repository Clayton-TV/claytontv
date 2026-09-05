#!/usr/bin/env python3
"""Download the Issue #97 course files with curl."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("course-downloads.tsv"))
    return parser.parse_args()


def output_path(output_directory: Path, manifest_path: str) -> Path:
    relative_path = PurePosixPath(manifest_path)
    if ":" in manifest_path or "\\" in manifest_path or relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("manifest path must stay inside the output directory")

    target = (output_directory / relative_path).resolve()
    if not target.is_relative_to(output_directory.resolve()):
        raise ValueError("manifest path must stay inside the output directory")
    return target


def write_report(report: csv.writer, status: str, path: str, url: str, message: str = "") -> None:
    report.writerow([status, path, url, message])


def error(message: str) -> None:
    sys.stderr.write(f"{message}\n")


def download_entry(
    output_directory: Path, state_directory: Path, retries: str, report: csv.writer, path: str, url: str
) -> bool:
    try:
        target = output_path(output_directory, path)
    except ValueError as exception:
        write_report(report, "failed", path, url, str(exception))
        error(f"Refusing {path}: {exception}")
        return False

    partial = target.with_name(f"{target.name}.part")
    completed_marker = state_directory / f"{path}.url"
    partial_marker = state_directory / f"{path}.part.url"
    target.parent.mkdir(parents=True, exist_ok=True)
    completed_marker.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        if (
            target.is_file()
            and completed_marker.is_file()
            and completed_marker.read_text(encoding="utf-8") == f"{url}\n"
        ):
            write_report(report, "skipped", path, url, "previously completed")
            return True
        message = "target exists without a matching completion record"
        write_report(report, "failed", path, url, message)
        error(f"Refusing to overwrite {target}")
        return False

    if partial.is_file() and (not partial_marker.is_file() or partial_marker.read_text(encoding="utf-8") != f"{url}\n"):
        message = "partial file belongs to a different or unknown URL"
        write_report(report, "failed", path, url, message)
        error(f"Refusing to resume {partial}: {message}")
        return False

    partial_marker.write_text(f"{url}\n", encoding="utf-8")
    command = [
        "curl",
        "--fail",
        "--location",
        "--continue-at",
        "-",
        "--retry",
        retries,
        "--retry-delay",
        "2",
        "--retry-all-errors",
        "--connect-timeout",
        "30",
        "--output",
        str(partial),
        url,
    ]
    if subprocess.run(command, check=False).returncode != 0:
        write_report(report, "failed", path, url, "curl failed; retained .part file for resume")
        error(f"Failed: {url}")
        return False

    partial.replace(target)
    completed_marker.write_text(f"{url}\n", encoding="utf-8")
    partial_marker.unlink(missing_ok=True)
    write_report(report, "completed", path, url)
    return True


def download(output_directory: Path, manifest: Path) -> int:
    if shutil.which("curl") is None:
        error("curl is required.")
        return 2
    if not manifest.is_file():
        error(f"Manifest not found: {manifest}")
        return 2

    output_directory.mkdir(parents=True, exist_ok=True)
    output_directory = output_directory.resolve()
    state_directory = output_directory / ".course-downloads-state"
    state_directory.mkdir(exist_ok=True)
    retries = os.environ.get("CURL_RETRIES", "3")
    failures = False

    with (
        manifest.open(newline="", encoding="utf-8") as manifest_file,
        (output_directory / "download-report.tsv").open("w", newline="", encoding="utf-8") as report_file,
    ):
        entries = csv.DictReader(manifest_file, delimiter="\t")
        if entries.fieldnames != ["course", "path", "url"]:
            error("Manifest must have course, path, and url columns.")
            return 2
        report = csv.writer(report_file, delimiter="\t", lineterminator="\n")
        report.writerow(["status", "path", "url", "message"])

        for entry in entries:
            path, url = entry["path"], entry["url"]
            failures = not download_entry(output_directory, state_directory, retries, report, path, url) or failures

    if failures:
        error(f"One or more downloads failed. See {output_directory / 'download-report.tsv'}")
        return 1
    sys.stdout.write(f"Completed. Report: {output_directory / 'download-report.tsv'}\n")
    return 0


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(download(arguments.output_directory, arguments.manifest))
