# Course download utility

This downloads the course files in Issue #97 to a local directory. It never uploads to Dropbox. After a successful run, upload the chosen output directory to the Clayton TV Dropbox manually.

Run from a clone of this repository. Choose a local folder with adequate free space; downloading the whole-course archive and the individual files duplicates material. Do not use a Dropbox-synchronised folder until the download is complete.

Windows PowerShell:

```powershell
uv run python scripts/download_course_media.py "D:\Clayton-TV-downloads"
```

macOS or Linux:

```bash
uv run python scripts/download_course_media.py "/path/to/Clayton-TV-downloads"
```

The utility requires `curl` 7.71 or newer. It retries transient failures, retains `<file>.part` files to resume later, and writes `download-report.tsv`. Re-run the same command after a failure. A completed file is skipped only when its matching completion record exists; an existing unrecorded file is never overwritten. A partial file is resumed only when it has a matching source URL record.

`scripts/course-downloads.tsv` is the source manifest. It has 49 distinct Issue #97 URLs: the first Children's Ministry entry is one worksheet PDF, not a duplicate fake video. The 13 Children's Ministry video URLs use the verified `Video` filename correction. Eight God’s Big Picture filenames that returned 404 remain as listed in the issue because their proposed replacements returned 403; they will be reported as failures until corrected at the source.

For a small local test manifest, pass `--manifest path/to/manifest.tsv`.
