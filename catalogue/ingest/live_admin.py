"""Incremental sync from the live legacy admin ("The Internet Broadcaster").

Supersedes ClayScraper: fetches the newest-modified programme list and each
programme's meta form, adapts them into the SAME record shape as the legacy
dump, and feeds them through the proven idempotent upsert core
(catalogue.ingest.legacy.ingest_programmes). One write path, no CSVs.

Auth is an operator-supplied session cookie (env LEGACY_ADMIN_COOKIE,
"name=value; name2=value2"), harvested from a logged-in browser — the legacy
app has no API or stable login endpoint. Expired sessions redirect to
/accessdenied.html, which we detect and report clearly.
"""

import logging
import os
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .normalize import date_from_ref

logger = logging.getLogger(__name__)

BASE_URL = os.environ.get("LEGACY_ADMIN_BASE_URL", "https://clayton.tv/adminsection")
PAGE_SIZE = 50
MAX_AUTO_PAGES = 200  # auto-depth runaway stop: 10,000 programmes

# The legacy server drops and stalls requests routinely — retry those rather
# than abandoning the run (and alerting) over a blip. Waits before each retry;
# one more attempt than there are waits.
RETRY_WAITS_SECONDS = (2, 5)
MAX_ATTEMPTS = len(RETRY_WAITS_SECONDS) + 1
TRANSIENT_ERRORS = (
    requests.exceptions.ConnectionError,  # refused, aborted, hung up before replying
    requests.exceptions.Timeout,  # too slow to connect, or to answer
    requests.exceptions.ChunkedEncodingError,  # hung up part-way through the page
)


class AdminAuthError(Exception):
    pass


def _with_retries(description, request):
    """Call `request()`, retrying transient network failures with a growing
    wait. Once the attempts are spent the error is raised as before, so a
    genuinely-down site still surfaces."""
    for attempt, wait in enumerate(RETRY_WAITS_SECONDS, start=1):
        try:
            return request()
        except TRANSIENT_ERRORS as exc:
            logger.warning(
                "Legacy admin %s failed (attempt %s/%s): %s — retrying in %ss",
                description,
                attempt,
                MAX_ATTEMPTS,
                exc,
                wait,
            )
            time.sleep(wait)
    return request()


def login(session):
    """Mint a session by submitting the admin login form. Credentials come
    from the server environment (set by the operator, e.g. via `op run`) —
    they are never stored in the repo or handled interactively."""
    user = os.environ.get("LEGACY_ADMIN_USERNAME", "").strip()
    password = os.environ.get("LEGACY_ADMIN_PASSWORD", "").strip()
    if not (user and password):
        return False

    # Sets the ASP session cookie, lands on login.asp?at=...
    page = _with_retries("login page", lambda: session.get(f"{BASE_URL}/", timeout=30))
    soup = BeautifulSoup(page.text, "html.parser")
    form = soup.find("form")
    action = (form.get("action") if form else None) or page.url
    response = _with_retries(
        "login submission",
        lambda: session.post(
            action,
            data={
                "kt_login_user": user,
                "kt_login_password": password,
                "kt_login_rememberme": "1",
                "kt_login1": "Login",
            },
            timeout=30,
        ),
    )
    if "kt_login_password" in response.text:  # still on the login form
        raise AdminAuthError("Legacy admin login failed — check LEGACY_ADMIN_USERNAME/PASSWORD.")
    return True


def session_from_env():
    session = requests.Session()
    session.headers.update({"User-Agent": "claytontv-beta-sync/1.0"})

    cookie = os.environ.get("LEGACY_ADMIN_COOKIE", "").strip()
    if cookie:
        session.headers.update({"Cookie": cookie})
        return session
    if login(session):
        return session
    raise AdminAuthError(
        "No legacy admin auth configured. Set LEGACY_ADMIN_USERNAME/PASSWORD "
        "(self-healing login) or LEGACY_ADMIN_COOKIE (manual session)."
    )


def fetch(session, path, _retried=False):
    response = _with_retries(
        f"GET {path}",
        lambda: session.get(f"{BASE_URL}/{path}", timeout=30, allow_redirects=True),
    )
    if "accessdenied" in response.url or response.status_code in (401, 403):
        # Session lapsed mid-run: re-login once if we hold credentials
        if not _retried and not os.environ.get("LEGACY_ADMIN_COOKIE") and login(session):
            return fetch(session, path, _retried=True)
        raise AdminAuthError(
            "Legacy admin session rejected — refresh LEGACY_ADMIN_COOKIE or set "
            "LEGACY_ADMIN_USERNAME/PASSWORD for self-healing login."
        )
    response.raise_for_status()
    return response.text


def iter_programme_id_pages(session, pages=1):
    """Yield one list of programme ids per newest-modified list page.

    pages=N scans a fixed depth (the hourly cron). pages=None is the
    self-sizing catch-up: keep paging until an entire page is ids we already
    hold (a modified programme always floats to page 0, so known territory
    means caught up). The stopping page is still yielded — its programmes
    are the newest-modified known ones, worth a refresh.
    """
    auto = pages is None
    # Snapshot once: ids ingested *during* this run must not look "known"
    known_before_run = set(_video_model().objects.values_list("id", flat=True)) if auto else set()
    seen = set()
    for page in range(MAX_AUTO_PAGES if auto else pages):
        html = fetch(session, f"mediaProgramme.asp?order=mdate&direc=up&offset={page * PAGE_SIZE}")
        page_ids = re.findall(r"mediaProgramme\w*\.asp\?ID=(\d+)", html)
        if page == 0 and not page_ids:
            raise RuntimeError(
                "Legacy admin list returned no programme links — layout change or error page? "
                "Refusing to report a silent empty sync."
            )
        if not page_ids:
            break
        fresh = []
        for pid in page_ids:
            if pid not in seen:  # pages repeat ids (meta + timeline links)
                seen.add(pid)
                fresh.append(pid)
        if fresh:
            yield fresh
        if auto and all(pid in known_before_run for pid in page_ids):
            break


def _video_model():
    from catalogue.models import Video

    return Video


def list_programme_ids(session, pages=1):
    """Newest-modified programme ids from the paginated list (flat)."""
    return [pid for page_ids in iter_programme_id_pages(session, pages=pages) for pid in page_ids]


def parse_meta_page(html):
    """Extract the programme form into a dump-shaped record fragment."""
    soup = BeautifulSoup(html, "html.parser")

    def input_value(name):
        node = soup.find("input", attrs={"name": name})
        return (node.get("value") or "").strip() if node else ""

    def textarea_value(name):
        node = soup.find("textarea", attrs={"name": name})
        return node.get_text().strip() if node else ""

    def selected(name):
        select = soup.find("select", attrs={"name": name})
        if not select:
            return []
        out = []
        for option in select.find_all("option", selected=True):
            raw = (option.get("value") or "").split("|")[0].strip()
            if raw.isdigit():
                out.append({"id": int(raw), "name": option.get_text().strip()})
        return out

    return {
        "ref": input_value("programmeRef"),
        "name": input_value("programmeName") or input_value("URL"),
        "date": input_value("programmeDate"),
        "description": textarea_value("programmeDescription"),
        "url": input_value("vimeoLink"),
        "thumbnail": input_value("ThumbnailURL"),
        "transcript_link": input_value("ProgrammeTranscript"),
        "audio_link": input_value("ProgrammeAudio"),
        "speakers": selected("ProgrammeRelatedSpeakers"),
        "topics": selected("ProgrammeRelatedTopics"),
        "books": selected("ProgrammeRelatedBooks"),
    }


def resolve_media(session, programme_id):
    """The current admin's meta form carries no video link (observed live
    2026-06-12, ID 12408): the URL lives on the media-item editor. The
    programme's image-picker options encode "<thumbnail>|<media id>" — follow
    the media id to mediaUpdate.asp, whose vimeoLink holds the actual URL
    (YouTube or Vimeo, despite the name)."""
    html = fetch(session, f"mediaProgrammeImage.asp?ID={programme_id}")
    option = re.search(r'value="([^"|]*)\|(\d+)"', html)
    if not option:
        return None
    thumbnail, media_id = option.group(1), option.group(2)
    media_html = fetch(session, f"mediaUpdate.asp?ID={media_id}")
    link = re.search(r'name="vimeoLink"[^>]*value="([^"]+)"', media_html)
    if not link:
        return None
    return {"url": link.group(1), "thumbnail": thumbnail}


def to_dump_record(programme_id, meta):
    """Shape a live-admin programme exactly like a legacy-dump record so the
    standard ingest path handles it (same normalization, same collisions,
    same idempotency)."""
    date = None
    raw = meta.get("date")
    if raw:
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                date = datetime.strptime(raw, fmt).date().isoformat()
                break
            except ValueError:
                continue
    # The admin frequently leaves programmeDate blank but the ref still
    # encodes DD.MM.YY — recover it rather than sink the video undated.
    if date is None:
        date = date_from_ref(meta.get("ref"))

    media = []
    if meta.get("url"):
        media.append({"id": 0, "type": "Video", "url": meta["url"], "image": meta.get("thumbnail")})

    return {
        "id": int(programme_id),
        "ref": meta.get("ref"),
        "name": meta.get("name"),
        "description": meta.get("description"),
        "date_added": date,
        "date_modified": date,
        "image": meta.get("thumbnail"),
        "transcript_link": meta.get("transcript_link"),
        "audio_link": meta.get("audio_link"),
        "media": media,
        "label_a": meta.get("speakers") or [],
        "label_b": meta.get("topics") or [],
        "label_c": meta.get("books") or [],
    }


def sync(pages=1, delay_seconds=1.0, session=None):
    """Fetch and ingest page by page, so a crash mid-catch-up (network blip,
    session lapse on the dying legacy server) keeps everything already
    fetched — the rerun then starts from a smaller gap."""
    from .legacy import ingest_programmes

    session = session or session_from_env()
    stats = {}
    records = []
    for page_ids in iter_programme_id_pages(session, pages=pages):
        page_records = []
        for programme_id in page_ids:
            meta = parse_meta_page(fetch(session, f"mediaProgrammeMeta.asp?ID={programme_id}"))
            if not meta.get("url"):
                # Current admin layout: the link lives on the media editor
                time.sleep(delay_seconds)
                media = resolve_media(session, programme_id)
                if media:
                    meta["url"] = media["url"]
                    meta["thumbnail"] = meta.get("thumbnail") or media["thumbnail"]
            page_records.append(to_dump_record(programme_id, meta))
            time.sleep(delay_seconds)  # be gentle: the legacy server is dying as it is
        page_stats = ingest_programmes(page_records)
        records.extend(page_records)
        for key, value in page_stats.items():
            if isinstance(value, list):
                stats.setdefault(key, []).extend(value)
            else:
                stats[key] = stats.get(key, 0) + value

    return stats, records
