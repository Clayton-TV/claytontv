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

The utility requires `curl` 7.71 or newer. It retries transient failures, retains `<file>.part` files to resume later, and writes `download-report.tsv`. Re-run the same command after a failure. A completed file is skipped only when its matching completion record exists; an existing unrecorded file is never overwritten. A partial file is resumed only when it has a matching source URL record. If the report says `curl could not resume (exit 33)`, move that `<file>.part` out of the output folder before retrying; the server does not support continuation.

`scripts/course-downloads.tsv` is the source manifest. It has 50 distinct Issue #97 URLs, including separate first-unit Children’s Ministry video and worksheet files. It uses seven verified God’s Big Picture filename corrections and all fourteen verified Children’s Ministry video corrections. The Intro printables URL remains unresolved (404).

The source provides no authoritative checksums. To prevent obvious error documents being accepted as media, completed PDFs, ZIPs, and MP4s must have their basic file signature. A rejected transfer is retained as `<file>.part.rejected` for inspection and is never marked complete.

For a small local test manifest, pass `--manifest path/to/manifest.tsv`.
