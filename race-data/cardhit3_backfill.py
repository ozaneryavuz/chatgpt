#!/usr/bin/env python3
"""Backfill official TJK program/result CSV pairs for CardHit-3.

The collector uses two independent meeting indexes:

1. A pinned public program-file index is used only to identify historical
   date/track pairs. Every actual training file is then downloaded from the
   official TJK CDN; the public file contents are never used as labels.
2. For dates after the public index, the official TJK daily program page is
   queried and its domestic track tabs are used as the meeting index.

Outputs are fail-closed: only pairs with both an official program CSV and an
official result CSV are retained in ``complete_meetings.csv``. SHA-256 hashes,
source URLs, HTTP status, byte counts and parser sentinels are recorded.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import random
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://www.tjk.org"
CDN = "https://medya-cdn.tjk.org/raporftp/TJKPDF"
PROGRAM_PAGE = f"{BASE}/TR/YarisSever/Info/Page/GunlukYarisProgrami"

DOMESTIC = {
    "adana": "Adana",
    "ankara": "Ankara",
    "antalya": "Antalya",
    "bursa": "Bursa",
    "diyarbakir": "Diyarbakır",
    "elazig": "Elazığ",
    "istanbul": "İstanbul",
    "izmir": "İzmir",
    "kocaeli": "Kocaeli",
    "sanliurfa": "Şanlıurfa",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 CardHit3/1.0"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.6",
}


@dataclass(frozen=True, order=True)
class Meeting:
    meeting_date: date
    track: str
    index_source: str

    @property
    def stem(self) -> str:
        safe = ascii_key(self.track).replace(" ", "_")
        return f"{self.meeting_date.isoformat()}__{safe}"


@dataclass
class DownloadResult:
    meeting_date: str
    track: str
    index_source: str
    program_url: str
    result_url: str
    program_status: int | None
    result_status: int | None
    program_bytes: int
    result_bytes: int
    program_sha256: str | None
    result_sha256: str | None
    program_valid: bool
    result_valid: bool
    complete: bool
    program_file: str | None
    result_file: str | None
    error: str | None


def ascii_key(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("ı", "i").replace("İ", "I")
    return re.sub(r"[^A-Za-z0-9]+", " ", text).strip().lower()


def canonical_track(value: str) -> str | None:
    key = ascii_key(value)
    key = re.sub(r"\s*\(\d+\.\s*y\.g\.\)\s*$", "", key).strip()
    for token, canonical in DOMESTIC.items():
        if key == token or key.startswith(token + " "):
            return canonical
    return None


def daterange(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def make_session() -> requests.Session:
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        raise_on_status=False,
    )
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=12, pool_maxsize=12))
    session.mount("http://", HTTPAdapter(max_retries=retry, pool_connections=12, pool_maxsize=12))
    return session


def seed_meetings(seed_dir: Path, start: date, end: date) -> set[Meeting]:
    meetings: set[Meeting] = set()
    pattern = re.compile(r"(?P<day>\d{2}\.\d{2}\.\d{4})-(?P<track>.+)\.csv$", re.I)
    for path in seed_dir.glob("*.csv"):
        match = pattern.match(path.name)
        if not match:
            continue
        try:
            meeting_date = datetime.strptime(match.group("day"), "%d.%m.%Y").date()
        except ValueError:
            continue
        if not (start <= meeting_date <= end):
            continue
        track = canonical_track(match.group("track"))
        if track:
            meetings.add(Meeting(meeting_date, track, "public_filename_index_official_redownload"))
    return meetings


def discover_one_day(day: date, timeout: float = 35.0) -> tuple[list[Meeting], dict]:
    session = make_session()
    params = {"QueryParameter_Tarih": day.strftime("%d/%m/%Y")}
    audit = {
        "date": day.isoformat(),
        "url": PROGRAM_PAGE,
        "status": None,
        "tracks": [],
        "error": None,
    }
    try:
        response = session.get(PROGRAM_PAGE, params=params, timeout=timeout)
        audit["status"] = response.status_code
        if response.status_code != 200:
            audit["error"] = f"HTTP {response.status_code}"
            return [], audit
        soup = BeautifulSoup(response.text, "html.parser")
        found: set[str] = set()
        for tab in soup.select("ul.gunluk-tabs li a[data-sehir-id], a[data-sehir-id]"):
            track = canonical_track(tab.get_text(" ", strip=True))
            if track:
                found.add(track)
        audit["tracks"] = sorted(found)
        return [Meeting(day, track, "official_daily_program_tabs") for track in sorted(found)], audit
    except Exception as exc:  # noqa: BLE001 - persisted to audit
        audit["error"] = f"{type(exc).__name__}: {exc}"
        return [], audit
    finally:
        session.close()


def discover_recent(start: date, end: date, workers: int) -> tuple[set[Meeting], list[dict]]:
    meetings: set[Meeting] = set()
    audits: list[dict] = []
    days = list(daterange(start, end))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(discover_one_day, day): day for day in days}
        for future in concurrent.futures.as_completed(futures):
            found, audit = future.result()
            meetings.update(found)
            audits.append(audit)
    audits.sort(key=lambda item: item["date"])
    return meetings, audits


def official_urls(meeting: Meeting) -> tuple[str, str]:
    iso = meeting.meeting_date.isoformat()
    dotted = meeting.meeting_date.strftime("%d.%m.%Y")
    year = meeting.meeting_date.strftime("%Y")
    city = quote(meeting.track, safe="")
    program = (
        f"{CDN}/{year}/{iso}/CSV/GunlukYarisProgrami/"
        f"{dotted}-{city}-GunlukYarisProgrami-TR.csv"
    )
    result = (
        f"{CDN}/{year}/{iso}/CSV/GunlukYarisSonuclari/"
        f"{dotted}-{city}-GunlukYarisSonuclari-TR.csv"
    )
    return program, result


def valid_csv(content: bytes, result: bool) -> bool:
    if len(content) < 350:
        return False
    text = content[:5000].decode("utf-8-sig", errors="replace")
    race_marker = bool(re.search(r"\d+\.\s*(?:Kosu|Koşu)", text, flags=re.I))
    table_marker = "At No" in text and ";" in text
    if result:
        result_marker = "GANYAN" in text.upper() or "Derece" in text or "SONUÇ" in text.upper()
        return race_marker and table_marker and result_marker
    return race_marker and table_marker


def fetch_bytes(url: str, timeout: float = 40.0) -> tuple[int | None, bytes, str | None]:
    session = make_session()
    try:
        response = session.get(url, timeout=timeout)
        return response.status_code, response.content, None
    except Exception as exc:  # noqa: BLE001
        return None, b"", f"{type(exc).__name__}: {exc}"
    finally:
        session.close()


def download_meeting(meeting: Meeting, program_dir: Path, result_dir: Path) -> DownloadResult:
    program_url, result_url = official_urls(meeting)
    # Small jitter keeps concurrent requests from landing at exactly the same instant.
    time.sleep(random.random() * 0.25)
    p_status, p_bytes, p_error = fetch_bytes(program_url)
    r_status, r_bytes, r_error = fetch_bytes(result_url)
    p_valid = p_status == 200 and valid_csv(p_bytes, result=False)
    r_valid = r_status == 200 and valid_csv(r_bytes, result=True)
    program_file = result_file = None
    if p_valid:
        path = program_dir / f"{meeting.stem}.csv"
        path.write_bytes(p_bytes)
        program_file = str(path)
    if r_valid:
        path = result_dir / f"{meeting.stem}.csv"
        path.write_bytes(r_bytes)
        result_file = str(path)
    errors = [value for value in (p_error, r_error) if value]
    return DownloadResult(
        meeting_date=meeting.meeting_date.isoformat(),
        track=meeting.track,
        index_source=meeting.index_source,
        program_url=program_url,
        result_url=result_url,
        program_status=p_status,
        result_status=r_status,
        program_bytes=len(p_bytes),
        result_bytes=len(r_bytes),
        program_sha256=hashlib.sha256(p_bytes).hexdigest() if p_valid else None,
        result_sha256=hashlib.sha256(r_bytes).hexdigest() if r_valid else None,
        program_valid=p_valid,
        result_valid=r_valid,
        complete=bool(p_valid and r_valid),
        program_file=program_file,
        result_file=result_file,
        error=" | ".join(errors) if errors else None,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-dir", type=Path, required=True)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2021, 8, 25))
    parser.add_argument("--recent-start", type=date.fromisoformat, default=date(2025, 1, 21))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2026, 8, 15))
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.start > args.end or args.recent_start > args.end:
        raise SystemExit("Invalid date range")
    root = args.output
    program_dir = root / "raw" / "history" / "program"
    result_dir = root / "raw" / "history" / "results"
    program_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    seeded = seed_meetings(args.seed_dir, args.start, args.end)
    recent, discovery_audit = discover_recent(args.recent_start, args.end, args.workers)
    # Prefer official discovery provenance where the same pair appears twice.
    meeting_map: dict[tuple[date, str], Meeting] = {
        (meeting.meeting_date, meeting.track): meeting for meeting in seeded
    }
    for meeting in recent:
        meeting_map[(meeting.meeting_date, meeting.track)] = meeting
    meetings = sorted(meeting_map.values())

    results: list[DownloadResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(download_meeting, meeting, program_dir, result_dir): meeting
            for meeting in meetings
        }
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: (item.meeting_date, item.track))

    manifest = pd.DataFrame([asdict(item) for item in results])
    manifest.to_csv(root / "source_manifest.csv", index=False)
    complete = manifest[manifest["complete"].eq(True)].copy() if not manifest.empty else manifest
    complete.to_csv(root / "complete_meetings.csv", index=False)
    (root / "discovery_audit.json").write_text(
        json.dumps(discovery_audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "generated_at_utc": datetime.now().astimezone().isoformat(),
        "date_range": {"start": args.start.isoformat(), "end": args.end.isoformat()},
        "seed_index_pairs": len(seeded),
        "official_discovered_pairs": len(recent),
        "candidate_pairs": len(meetings),
        "complete_official_pairs": int(len(complete)),
        "program_only": int((manifest["program_valid"] & ~manifest["result_valid"]).sum()) if not manifest.empty else 0,
        "result_only": int((~manifest["program_valid"] & manifest["result_valid"]).sum()) if not manifest.empty else 0,
        "failed_pairs": int((~manifest["complete"]).sum()) if not manifest.empty else 0,
        "official_source_only": True,
        "public_seed_content_used_for_training": False,
        "raw_program_dir": str(program_dir),
        "raw_result_dir": str(result_dir),
    }
    (root / "backfill_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if len(complete) < 150:
        raise SystemExit(
            f"Fail closed: only {len(complete)} complete official meetings; expected at least 150"
        )


if __name__ == "__main__":
    main()
