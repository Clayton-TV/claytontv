# Course download utility

This downloads the course files in Issue #97 to a local directory. It never uploads to Dropbox. After a successful run, upload the chosen output directory to the Clayton TV Dropbox manually.

Run from a clone of this repository. Choose a local folder with adequate free space; downloading the whole-course archive and the individual files duplicates material. Do not use a Dropbox-synchronised folder until the download is complete.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\download-course-media.ps1 -OutputDirectory "D:\Clayton-TV-downloads"
```

macOS, Linux, or Git Bash on Windows:

```bash
bash scripts/download-course-media.sh "/path/to/Clayton-TV-downloads"
```

Both scripts require `curl` 7.71 or newer. They retry transient failures, retain `<file>.part` files to resume later, and write `download-report.tsv`. Re-run the same command after a failure. A completed file is skipped only when its matching completion record exists; an existing unrecorded file is never overwritten.

`scripts/course-downloads.tsv` is the source manifest. It has 49 distinct Issue #97 URLs: the first Children's Ministry entry is one worksheet PDF, not a duplicate fake video. The 13 Children's Ministry video URLs use the verified `Video` filename correction. Eight God’s Big Picture filenames that returned 404 remain as listed in the issue because their proposed replacements returned 403; they will be reported as failures until corrected at the source.

For a small local test manifest, pass `--manifest path/to/manifest.tsv` to either script.
