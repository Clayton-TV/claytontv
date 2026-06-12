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

import os
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

BASE_URL = os.environ.get("LEGACY_ADMIN_BASE_URL", "https://clayton.tv/adminsection")
PAGE_SIZE = 50


class AdminAuthError(Exception):
    pass


def login(session):
    """Mint a session by submitting the admin login form. Credentials come
    from the server environment (set by the operator, e.g. via `op run`) —
    they are never stored in the repo or handled interactively."""
    user = os.environ.get("LEGACY_ADMIN_USERNAME", "").strip()
    password = os.environ.get("LEGACY_ADMIN_PASSWORD", "").strip()
    if not (user and password):
        return False

    page = session.get(f"{BASE_URL}/", timeout=30)  # sets the ASP session cookie, lands on login.asp?at=...
    soup = BeautifulSoup(page.text, "html.parser")
    form = soup.find("form")
    action = (form.get("action") if form else None) or page.url
    response = session.post(
        action,
        data={
            "kt_login_user": user,
            "kt_login_password": password,
            "kt_login_rememberme": "1",
            "kt_login1": "Login",
        },
        timeout=30,
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
    response = session.get(f"{BASE_URL}/{path}", timeout=30, allow_redirects=True)
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


def list_programme_ids(session, pages=1):
    """Newest-modified programme ids from the paginated list."""
    ids = []
    for page in range(pages):
        html = fetch(session, f"mediaProgramme.asp?order=mdate&direc=up&offset={page * PAGE_SIZE}")
        page_ids = re.findall(r"mediaProgramme\w*\.asp\?ID=(\d+)", html)
        for pid in page_ids:
            if pid not in ids:
                ids.append(pid)
        if not page_ids:
            break
    return ids


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
    from .legacy import ingest_programmes

    session = session or session_from_env()
    records = []
    for programme_id in list_programme_ids(session, pages=pages):
        meta = parse_meta_page(fetch(session, f"mediaProgrammeMeta.asp?ID={programme_id}"))
        records.append(to_dump_record(programme_id, meta))
        time.sleep(delay_seconds)  # be gentle: the legacy server is dying as it is

    return ingest_programmes(records), records
